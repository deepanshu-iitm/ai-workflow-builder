import { Handle, Position } from '@xyflow/react';
import { BookOpen, FileText } from 'lucide-react';
import './nodes.css';

interface KnowledgeBaseNodeProps {
  data: {
    label: string;
    description?: string;
    config: {
      document_ids?: string[];
      top_k?: number;
    };
  };
  selected: boolean;
}

export default function KnowledgeBaseNode({ data, selected }: KnowledgeBaseNodeProps) {
  const docCount = data.config?.document_ids?.length || 0;
  const topK = data.config?.top_k || 5;
  
  return (
    <div className={`workflow-node knowledge-node ${selected ? 'selected' : ''}`}>
      <Handle 
        type="target" 
        position={Position.Left} 
        className="handle handle-target"
      />
      
      <div className="node-header">
        <div className="node-icon knowledge-icon">
          <BookOpen size={18} />
        </div>
        <div className="node-info">
          <div className="node-title">{data.label || 'Knowledge Base'}</div>
          <div className="node-subtitle">RAG Component</div>
        </div>
      </div>
      
      <div className="node-body">
        <p className="node-description">
          {data.description || 'RAG-powered document retrieval'}
        </p>
        
        <div className="node-stats">
          <div className="stat">
            <FileText size={12} />
            <span>{docCount} document{docCount !== 1 ? 's' : ''}</span>
          </div>
          <div className="stat">
            <span>Top {topK} chunks</span>
          </div>
        </div>
      </div>
      
      <Handle 
        type="source" 
        position={Position.Right} 
        className="handle handle-source"
      />
    </div>
  );
}
