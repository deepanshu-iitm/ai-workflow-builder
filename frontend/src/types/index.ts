export interface NodeData {
  label: string;
  icon?: React.ReactNode;
  description?: string;
  config: NodeConfig;
}

export interface NodeConfig {
  // Input node
  placeholder?: string;
  
  // Knowledge Base node
  document_ids?: string[];
  collection_name?: string;
  top_k?: number;
  
  // LLM node
  model?: string;
  temperature?: number;
  max_tokens?: number;
  system_prompt?: string;
  enable_web_search?: boolean;
  
  // Output node
  format?: 'text' | 'markdown' | 'json';
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: NodeData;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string | null;
  page_count: number | null;
  chunk_count: number;
  is_embedded: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  execution_time_ms?: number;
  tokens_used?: number;
  model_used?: string;
  extra_data: Record<string, unknown>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  workflow_id: string | null;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  messages: ChatMessage[];
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface ChatQueryResponse {
  response: string;
  session_id: string;
  message_id: string;
  execution_time_ms: number;
  tokens_used?: number;
  model_used?: string;
  sources: Array<Record<string, unknown>>;
  metadata: Record<string, unknown>;
}
