from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import time

from app.services.document_service import DocumentService
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.services.web_search import WebSearchService
from app.models.document import Document


class WorkflowEngine:
    """Engine for executing workflows defined by connected components."""
    
    def __init__(self, db: Session):
        self.db = db
        self.document_service = DocumentService(db)
        self.llm_service = LLMService()
        self.web_search_service = WebSearchService()
    
    def validate_workflow(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate a workflow configuration."""
        errors = []
        warnings = []
        
        if not nodes:
            errors.append("Workflow must have at least one component")
            return {"is_valid": False, "errors": errors, "warnings": warnings}
        
        # Check for required node types
        node_types = [n.get("type", n.get("node_type", "")).lower().replace(" ", "") for n in nodes]
        node_ids = [n.get("id", n.get("node_id", "")) for n in nodes]
        
        has_input = any(t in ["input", "userquery"] for t in node_types)
        has_output = any(t in ["output"] for t in node_types)
        has_llm = any(t in ["llm", "llmengine"] for t in node_types)
        
        if not has_input:
            errors.append("Workflow must have an Input component")
        
        if not has_output:
            errors.append("Workflow must have an Output component")
        
        if not has_llm:
            warnings.append("Workflow should have an LLM Engine component for processing")
        
        # Check for connections
        if not edges and len(nodes) > 1:
            warnings.append("Components are not connected")
        
        # Validate edge connections
        for edge in edges:
            source = edge.get("source", edge.get("source_node_id", ""))
            target = edge.get("target", edge.get("target_node_id", ""))
            
            if source not in node_ids:
                errors.append(f"Edge references non-existent source node: {source}")
            if target not in node_ids:
                errors.append(f"Edge references non-existent target node: {target}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _build_execution_order(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build the order in which nodes should be executed."""
        # Create adjacency list
        node_map = {n.get("id", n.get("node_id", "")): n for n in nodes}
        
        # Find incoming edges for each node
        incoming = {n.get("id", n.get("node_id", "")): [] for n in nodes}
        outgoing = {n.get("id", n.get("node_id", "")): [] for n in nodes}
        
        for edge in edges:
            source = edge.get("source", edge.get("source_node_id", ""))
            target = edge.get("target", edge.get("target_node_id", ""))
            
            if source in outgoing:
                outgoing[source].append(target)
            if target in incoming:
                incoming[target].append(source)
        
        # Find input node (no incoming edges or type is input)
        execution_order = []
        visited = set()
        
        # Start with input nodes
        queue = []
        for node_id, node in node_map.items():
            node_type = node.get("type", node.get("node_type", "")).lower().replace(" ", "")
            if node_type in ["input", "userquery"] or not incoming[node_id]:
                queue.append(node_id)
        
        # BFS to determine execution order
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            
            visited.add(current_id)
            if current_id in node_map:
                execution_order.append(node_map[current_id])
            
            for next_id in outgoing.get(current_id, []):
                if next_id not in visited:
                    queue.append(next_id)
        
        # Add any remaining unvisited nodes
        for node_id, node in node_map.items():
            if node_id not in visited:
                execution_order.append(node)
        
        return execution_order
    
    async def execute(
        self,
        query: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a workflow with the given query."""
        start_time = time.time()
        
        # Validate workflow
        validation = self.validate_workflow(nodes, edges)
        if not validation["is_valid"]:
            return {
                "success": False,
                "response": "Invalid workflow: " + "; ".join(validation["errors"]),
                "errors": validation["errors"],
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
        
        # Build execution order
        execution_order = self._build_execution_order(nodes, edges)
        
        # Initialize context
        context = {
            "query": query,
            "knowledge_context": "",
            "web_context": "",
            "custom_prompt": "",
            "response": "",
            "sources": [],
            "logs": []
        }
        
        # Execute each node
        for node in execution_order:
            node_type = node.get("type", node.get("node_type", "")).lower().replace(" ", "")
            node_config = node.get("data", {}).get("config", node.get("config", {}))
            
            context["logs"].append(f"Executing: {node_type}")
            
            try:
                if node_type in ["input", "userquery"]:
                    # Input node - just pass the query through
                    context["logs"].append(f"Input received: {query}")
                
                elif node_type in ["knowledgebase", "knowledge base"]:
                    # Knowledge Base node - retrieve relevant context
                    context = await self._execute_knowledge_base(node_config, context)
                
                elif node_type in ["llm", "llmengine", "llm engine"]:
                    # LLM node - generate response
                    context = await self._execute_llm(node_config, context)
                
                elif node_type == "output":
                    # Output node - finalize response
                    context["logs"].append("Output prepared")
                
            except Exception as e:
                context["logs"].append(f"Error in {node_type}: {str(e)}")
                return {
                    "success": False,
                    "response": f"Error executing workflow: {str(e)}",
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                    "logs": context["logs"]
                }
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "response": context["response"],
            "sources": context["sources"],
            "execution_time_ms": execution_time,
            "logs": context["logs"]
        }
    
    async def _execute_knowledge_base(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute knowledge base component to retrieve relevant context."""
        document_ids = config.get("document_ids", [])
        collection_name = config.get("collection_name", "default")
        top_k = config.get("top_k", 5)
        
        if not document_ids:
            context["logs"].append("No documents configured for knowledge base")
            return context
        
        # Get query embedding
        query_embedding = self.llm_service.generate_query_embedding(context["query"])
        
        # Query vector store
        vector_store = VectorStoreService(collection_name)
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k
        )
        
        if results["documents"]:
            context["knowledge_context"] = "\n\n".join(results["documents"])
            context["sources"].extend([
                {"type": "document", "metadata": m}
                for m in results["metadatas"]
            ])
            context["logs"].append(f"Retrieved {len(results['documents'])} relevant chunks")
        else:
            context["logs"].append("No relevant context found in knowledge base")
        
        return context
    
    async def _execute_llm(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute LLM component to generate response."""
        custom_prompt = config.get("custom_prompt", config.get("system_prompt", ""))
        temperature = config.get("temperature", 0.7)
        enable_web_search = config.get("enable_web_search", False)
        
        # Optionally perform web search
        if enable_web_search:
            web_results = await self.web_search_service.async_search(
                context["query"],
                num_results=5
            )
            if web_results["success"]:
                context["web_context"] = self.web_search_service.format_results_as_context(
                    web_results
                )
                context["sources"].extend([
                    {"type": "web", "title": r["title"], "url": r["link"]}
                    for r in web_results["results"]
                ])
                context["logs"].append(f"Web search returned {len(web_results['results'])} results")
        
        # Build combined context
        combined_context = ""
        if context["knowledge_context"]:
            combined_context += f"Document Context:\n{context['knowledge_context']}\n\n"
        if context["web_context"]:
            combined_context += f"{context['web_context']}\n\n"
        
        # Generate response
        result = await self.llm_service.generate_response(
            query=context["query"],
            context=combined_context if combined_context else None,
            system_prompt=custom_prompt if custom_prompt else None,
            temperature=temperature
        )
        
        context["response"] = result["response"]
        context["model_used"] = result.get("model")
        context["tokens_used"] = result.get("tokens_used")
        context["logs"].append(f"LLM response generated in {result['execution_time_ms']}ms")
        
        return context
