import { Handle, Position } from '@xyflow/react';
import { MessageSquare } from 'lucide-react';
import './nodes.css';

interface InputNodeProps {
  data: {
    label: string;
    description?: string;
    config: Record<string, unknown>;
  };
  selected: boolean;
}

export default function InputNode({ data, selected }: InputNodeProps) {
  return (
    <div className={`workflow-node input-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <div className="node-icon input-icon">
          <MessageSquare size={18} />
        </div>
        <div className="node-info">
          <div className="node-title">{data.label || 'User Query'}</div>
          <div className="node-subtitle">Entry Point</div>
        </div>
      </div>
      
      <div className="node-body">
        <p className="node-description">
          {data.description || 'Accepts user queries and passes them to the next component.'}
        </p>
      </div>
      
      <Handle 
        type="source" 
        position={Position.Right} 
        className="handle handle-source"
      />
    </div>
  );
}
