import axios from 'axios';
import type { Document, ValidationResult, ChatQueryResponse, ChatSession } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document APIs
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (): Promise<{ documents: Document[]; total: number }> => {
  const response = await api.get('/documents/');
  return response.data;
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  await api.delete(`/documents/${documentId}`);
};

// Workflow APIs
export const validateWorkflow = async (
  nodes: Array<{ node_id: string; node_type: string; config: Record<string, unknown> }>,
  edges: Array<{ edge_id: string; source_node_id: string; target_node_id: string }>
): Promise<ValidationResult> => {
  const response = await api.post('/workflows/validate', {
    name: 'Validation',
    nodes,
    edges,
  });
  return response.data;
};

export const saveWorkflow = async (
  name: string,
  nodes: Array<{ node_id: string; node_type: string; label?: string; position_x: number; position_y: number; config: Record<string, unknown> }>,
  edges: Array<{ edge_id: string; source_node_id: string; target_node_id: string }>
): Promise<{ id: string }> => {
  const response = await api.post('/workflows/', {
    name,
    nodes,
    edges,
  });
  return response.data;
};

// Chat APIs
export const executeQuery = async (
  query: string,
  nodes: Array<Record<string, unknown>>,
  edges: Array<Record<string, unknown>>,
  sessionId?: string
): Promise<ChatQueryResponse> => {
  const response = await api.post('/chat/query', {
    query,
    nodes,
    edges,
    session_id: sessionId,
  });
  return response.data;
};

export const getChatSessions = async (): Promise<ChatSession[]> => {
  const response = await api.get('/chat/sessions');
  return response.data;
};

export const getChatSession = async (sessionId: string): Promise<ChatSession> => {
  const response = await api.get(`/chat/sessions/${sessionId}`);
  return response.data;
};

export default api;
