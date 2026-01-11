import { Handle, Position } from '@xyflow/react';
import { Bot, Globe, Thermometer } from 'lucide-react';
import './nodes.css';

interface LLMNodeProps {
  data: {
    label: string;
    description?: string;
    config: {
      model?: string;
      temperature?: number;
      enable_web_search?: boolean;
      system_prompt?: string;
    };
  };
  selected: boolean;
}

export default function LLMNode({ data, selected }: LLMNodeProps) {
  const model = data.config?.model || 'Gemini 1.5 Flash';
  const temp = data.config?.temperature ?? 0.7;
  const webSearch = data.config?.enable_web_search || false;
  
  return (
    <div className={`workflow-node llm-node ${selected ? 'selected' : ''}`}>
      <Handle 
        type="target" 
        position={Position.Left} 
        className="handle handle-target"
      />
      
      <div className="node-header">
        <div className="node-icon llm-icon">
          <Bot size={18} />
        </div>
        <div className="node-info">
          <div className="node-title">{data.label || 'LLM Engine'}</div>
          <div className="node-subtitle">{model}</div>
        </div>
      </div>
      
      <div className="node-body">
        <p className="node-description">
          {data.description || 'AI-powered response generation'}
        </p>
        
        <div className="node-stats">
          <div className="stat">
            <Thermometer size={12} />
            <span>Temp: {temp}</span>
          </div>
          {webSearch && (
            <div className="stat web-enabled">
              <Globe size={12} />
              <span>Web Search</span>
            </div>
          )}
        </div>
        
        {data.config?.system_prompt && (
          <div className="node-prompt-preview">
            <span className="prompt-label">Prompt:</span>
            <span className="prompt-text">
              {data.config.system_prompt.substring(0, 50)}
              {data.config.system_prompt.length > 50 ? '...' : ''}
            </span>
          </div>
        )}
      </div>
      
      <Handle 
        type="source" 
        position={Position.Right} 
        className="handle handle-source"
      />
    </div>
  );
}
