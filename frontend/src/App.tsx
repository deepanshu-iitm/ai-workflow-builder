import { useCallback, useRef } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  useReactFlow,
  ReactFlowProvider,
  type Connection,
  type NodeChange,
  type EdgeChange,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ConfigPanel from './components/ConfigPanel';
import ChatModal from './components/ChatModal';
import { nodeTypes } from './nodes';
import { useWorkflowStore } from './store/workflowStore';
import type { WorkflowNode, WorkflowEdge } from './types';
import './App.css';

function WorkflowBuilder() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();
  
  const { 
    nodes, 
    edges, 
    setNodes, 
    setEdges, 
    addNode, 
    selectNode,
    selectedNode,
    setIsValidated
  } = useWorkflowStore();

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const newNodes = applyNodeChanges(changes, nodes as any) as WorkflowNode[];
      setNodes(newNodes);
      setIsValidated(false);
    },
    [nodes, setNodes, setIsValidated]
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      const newEdges = applyEdgeChanges(changes, edges as any) as WorkflowEdge[];
      setEdges(newEdges);
      setIsValidated(false);
    },
    [edges, setEdges, setIsValidated]
  );

  const onConnect = useCallback(
    (connection: Connection) => {
      const newEdges = addEdge(
        {
          ...connection,
          id: `edge-${Date.now()}`,
          animated: true,
          style: { stroke: '#6366f1', strokeWidth: 2 },
        },
        edges as any
      ) as WorkflowEdge[];
      setEdges(newEdges);
      setIsValidated(false);
    },
    [edges, setEdges, setIsValidated]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const data = event.dataTransfer.getData('application/reactflow');
      if (!data || !reactFlowWrapper.current) return;

      const { type, nodeType } = JSON.parse(data);
      const bounds = reactFlowWrapper.current.getBoundingClientRect();

      const position = screenToFlowPosition({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      });

      const newNode: WorkflowNode = {
        id: `${nodeType}-${Date.now()}`,
        type: nodeType,
        position,
        data: {
          label: type,
          description: getNodeDescription(nodeType),
          config: getDefaultConfig(nodeType),
        },
      };

      addNode(newNode);
    },
    [screenToFlowPosition, addNode]
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: any) => {
      selectNode(node as WorkflowNode);
    },
    [selectNode]
  );

  const onPaneClick = useCallback(() => {
    selectNode(null);
  }, [selectNode]);

  return (
    <div className="app">
      <Navbar />
      
      <div className="main-content">
        <Sidebar />
        
        <div ref={reactFlowWrapper} className="workflow-canvas">
          <ReactFlow
            nodes={nodes as any}
            edges={edges as any}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            fitView
            snapToGrid
            snapGrid={[15, 15]}
            defaultEdgeOptions={{
              animated: true,
              style: { stroke: '#6366f1', strokeWidth: 2 },
            }}
            connectionLineStyle={{ stroke: '#6366f1', strokeWidth: 2 }}
          >
            <Background 
              variant={BackgroundVariant.Dots} 
              gap={20} 
              size={1} 
              color="#e2e8f0"
            />
            <Controls 
              showInteractive={false}
              className="controls"
            />
            <MiniMap 
              nodeColor={(node) => getNodeColor(node.type || '')}
              maskColor="rgba(0, 0, 0, 0.1)"
              className="minimap"
            />
          </ReactFlow>
          
          {nodes.length === 0 && (
            <div className="empty-canvas">
              <h3>Build Your AI Workflow</h3>
              <p>Drag and drop components from the sidebar to get started</p>
              <div className="empty-steps">
                <div className="step">
                  <span className="step-num">1</span>
                  <span>Add an Input node</span>
                </div>
                <div className="step">
                  <span className="step-num">2</span>
                  <span>Connect to LLM or Knowledge Base</span>
                </div>
                <div className="step">
                  <span className="step-num">3</span>
                  <span>Add an Output node</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <ConfigPanel />
      </div>
      
      <ChatModal />
    </div>
  );
}

function getNodeDescription(nodeType: string): string {
  switch (nodeType) {
    case 'input':
      return 'Entry point for user queries';
    case 'knowledgebase':
      return 'RAG-powered document retrieval';
    case 'llm':
      return 'AI-powered response generation';
    case 'output':
      return 'Display final response';
    default:
      return '';
  }
}

function getDefaultConfig(nodeType: string): Record<string, unknown> {
  switch (nodeType) {
    case 'input':
      return { placeholder: 'Enter your question...' };
    case 'knowledgebase':
      return { document_ids: [], top_k: 5, collection_name: 'default' };
    case 'llm':
      return {
        model: 'gemini-2.0-flash',
        temperature: 0.7,
        max_tokens: 2048,
        system_prompt: '',
        enable_web_search: false,
      };
    case 'output':
      return { format: 'markdown' };
    default:
      return {};
  }
}

function getNodeColor(nodeType: string): string {
  switch (nodeType) {
    case 'input':
      return '#3b82f6';
    case 'knowledgebase':
      return '#8b5cf6';
    case 'llm':
      return '#10b981';
    case 'output':
      return '#f59e0b';
    default:
      return '#6366f1';
  }
}

export default function App() {
  return (
    <ReactFlowProvider>
      <WorkflowBuilder />
    </ReactFlowProvider>
  );
}
