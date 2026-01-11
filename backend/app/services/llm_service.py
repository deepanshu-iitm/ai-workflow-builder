import google.generativeai as genai
from typing import List, Optional, Dict, Any
import time

from app.core.config import settings


class LLMService:
    """Service for interacting with Google Gemini LLM and embeddings."""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
    
    async def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Generate a response using Gemini LLM."""
        start_time = time.time()
        
        # Build the prompt
        full_prompt = ""
        
        if system_prompt:
            full_prompt += f"{system_prompt}\n\n"
        
        if context:
            full_prompt += f"Context:\n{context}\n\n"
        
        full_prompt += f"User Query: {query}"
        
        try:
            # Generate response
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.text,
                "model": settings.GEMINI_MODEL,
                "execution_time_ms": execution_time,
                "tokens_used": None,  
                "success": True
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                "response": f"Error generating response: {str(e)}",
                "model": settings.GEMINI_MODEL,
                "execution_time_ms": execution_time,
                "tokens_used": None,
                "success": False,
                "error": str(e)
            }
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Gemini."""
        embeddings = []
        
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Error generating embedding: {e}")
                # Return zero vector on error
                embeddings.append([0.0] * 768)
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return [0.0] * 768
    
    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Have a conversation with message history."""
        start_time = time.time()
        
        try:
            # Build conversation history
            chat = self.model.start_chat(history=[])
            
            # Add system prompt as first message if provided
            if system_prompt:
                await chat.send_message_async(f"System: {system_prompt}")
            
            # Process message history
            for msg in messages[:-1]:  # All but the last message
                if msg["role"] == "user":
                    await chat.send_message_async(msg["content"])
            
            # Send the last message and get response
            last_message = messages[-1]["content"] if messages else ""
            response = await chat.send_message_async(last_message)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.text,
                "model": settings.GEMINI_MODEL,
                "execution_time_ms": execution_time,
                "success": True
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                "response": f"Error in chat: {str(e)}",
                "model": settings.GEMINI_MODEL,
                "execution_time_ms": execution_time,
                "success": False,
                "error": str(e)
            }
