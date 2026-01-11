import { Handle, Position } from '@xyflow/react';
import { Send } from 'lucide-react';
import './nodes.css';

interface OutputNodeProps {
  data: {
    label: string;
    description?: string;
    config: {
      format?: 'text' | 'markdown' | 'json';
    };
  };
  selected: boolean;
}

export default function OutputNode({ data, selected }: OutputNodeProps) {
  const format = data.config?.format || 'markdown';
  
  return (
    <div className={`workflow-node output-node ${selected ? 'selected' : ''}`}>
      <Handle 
        type="target" 
        position={Position.Left} 
        className="handle handle-target"
      />
      
      <div className="node-header">
        <div className="node-icon output-icon">
          <Send size={18} />
        </div>
        <div className="node-info">
          <div className="node-title">{data.label || 'Output'}</div>
          <div className="node-subtitle">Response Display</div>
        </div>
      </div>
      
      <div className="node-body">
        <p className="node-description">
          {data.description || 'Display final response'}
        </p>
        
        <div className="node-stats">
          <div className="stat">
            <span>Format: {format}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
