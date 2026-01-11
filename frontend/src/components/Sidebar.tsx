import { MessageSquare, Bot, BookOpen, Send, GripVertical, Sparkles } from 'lucide-react';
import { useWorkflowStore } from '../store/workflowStore';
import './Sidebar.css';

const components = [
  { 
    type: 'Input', 
    nodeType: 'input',
    icon: <MessageSquare size={18} />, 
    color: '#666',
    description: 'Entry point for user queries'
  },
  { 
    type: 'Knowledge Base', 
    nodeType: 'knowledgebase',
    icon: <BookOpen size={18} />, 
    color: '#666',
    description: 'RAG-powered document retrieval'
  },
  { 
    type: 'LLM Engine', 
    nodeType: 'llm',
    icon: <Bot size={18} />, 
    color: '#666',
    description: 'AI-powered response generation'
  },
  { 
    type: 'Output', 
    nodeType: 'output',
    icon: <Send size={18} />, 
    color: '#666',
    description: 'Display final response'
  },
];

export default function Sidebar() {
  const { setChatOpen, isValidated } = useWorkflowStore();

  const onDragStart = (event: React.DragEvent, item: typeof components[0]) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({
      type: item.type,
      nodeType: item.nodeType,
    }));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <button 
          className={`chat-with-ai-btn ${isValidated ? 'ready' : ''}`}
          onClick={() => setChatOpen(true)}
        >
          <Sparkles size={18} />
          <span>Chat With AI</span>
          <span className="btn-arrow">→</span>
        </button>
      </div>

      <div className="sidebar-section">
        <div className="section-header">
          <span>Components</span>
          <span className="component-count">{components.length}</span>
        </div>

        <div className="component-list">
          {components.map((item) => (
            <div
              key={item.type}
              className="component-item"
              draggable
              onDragStart={(e) => onDragStart(e, item)}
            >
              <div className="component-icon" style={{ background: item.color }}>
                {item.icon}
              </div>
              <div className="component-info">
                <span className="component-name">{item.type}</span>
                <span className="component-desc">{item.description}</span>
              </div>
              <div className="drag-handle">
                <GripVertical size={16} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="sidebar-footer">
        <p>Drag components to the canvas to build your workflow</p>
      </div>
    </aside>
  );
}
