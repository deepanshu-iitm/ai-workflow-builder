import { create } from 'zustand';
import type { WorkflowNode, WorkflowEdge, ValidationResult, Document } from '../types';

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNode: WorkflowNode | null;
  documents: Document[];
  validation: ValidationResult | null;
  isValidated: boolean;
  isChatOpen: boolean;
  
  // Actions
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  addNode: (node: WorkflowNode) => void;
  updateNode: (nodeId: string, data: Partial<WorkflowNode['data']>) => void;
  removeNode: (nodeId: string) => void;
  selectNode: (node: WorkflowNode | null) => void;
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (documentId: string) => void;
  setValidation: (validation: ValidationResult | null) => void;
  setIsValidated: (isValidated: boolean) => void;
  setChatOpen: (isOpen: boolean) => void;
  clearWorkflow: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  documents: [],
  validation: null,
  isValidated: false,
  isChatOpen: false,
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node],
    isValidated: false,
  })),
  
  updateNode: (nodeId, data) => set((state) => {
    const updatedNodes = state.nodes.map((node) =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, ...data } }
        : node
    );
    
    // Also update selectedNode if it's the one being updated
    const updatedSelectedNode = state.selectedNode?.id === nodeId
      ? updatedNodes.find(n => n.id === nodeId) || null
      : state.selectedNode;
    
    return {
      nodes: updatedNodes,
      selectedNode: updatedSelectedNode,
      isValidated: false,
    };
  }),
  
  removeNode: (nodeId) => set((state) => ({
    nodes: state.nodes.filter((node) => node.id !== nodeId),
    edges: state.edges.filter(
      (edge) => edge.source !== nodeId && edge.target !== nodeId
    ),
    selectedNode: state.selectedNode?.id === nodeId ? null : state.selectedNode,
    isValidated: false,
  })),
  
  selectNode: (node) => set({ selectedNode: node }),
  
  setDocuments: (documents) => set({ documents }),
  
  addDocument: (document) => set((state) => ({
    documents: [...state.documents, document],
  })),
  
  removeDocument: (documentId) => set((state) => ({
    documents: state.documents.filter((doc) => doc.id !== documentId),
  })),
  
  setValidation: (validation) => set({ validation }),
  
  setIsValidated: (isValidated) => set({ isValidated }),
  
  setChatOpen: (isOpen) => set({ isChatOpen: isOpen }),
  
  clearWorkflow: () => set({
    nodes: [],
    edges: [],
    selectedNode: null,
    validation: null,
    isValidated: false,
  }),
}));
