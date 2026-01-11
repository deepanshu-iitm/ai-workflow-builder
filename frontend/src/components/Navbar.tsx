import { Save, Play, CheckCircle, AlertCircle, Loader2, Trash2 } from 'lucide-react';
import { useWorkflowStore } from '../store/workflowStore';
import { validateWorkflow, saveWorkflow } from '../api';
import { useState } from 'react';
import './Navbar.css';

export default function Navbar() {
  const { 
    nodes, 
    edges, 
    validation, 
    setValidation, 
    isValidated, 
    setIsValidated,
    clearWorkflow 
  } = useWorkflowStore();
  
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const handleBuildStack = async () => {
    if (nodes.length === 0) {
      setValidation({
        is_valid: false,
        errors: ['Add at least one component to the workflow'],
        warnings: [],
      });
      return;
    }

    setIsValidating(true);
    
    try {
      const apiNodes = nodes.map((node) => ({
        node_id: node.id,
        node_type: node.type,
        config: node.data.config,
      }));

      const apiEdges = edges.map((edge) => ({
        edge_id: edge.id,
        source_node_id: edge.source,
        target_node_id: edge.target,
      }));

      const result = await validateWorkflow(apiNodes, apiEdges);
      setValidation(result);
      setIsValidated(result.is_valid);
    } catch (error) {
      setValidation({
        is_valid: false,
        errors: ['Failed to validate workflow. Is the backend running?'],
        warnings: [],
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    if (nodes.length === 0) {
      setSaveMessage('Nothing to save');
      setTimeout(() => setSaveMessage(null), 2000);
      return;
    }

    setIsSaving(true);
    
    try {
      const apiNodes = nodes.map((node) => ({
        node_id: node.id,
        node_type: node.type,
        label: node.data.label,
        position_x: Math.round(node.position.x),
        position_y: Math.round(node.position.y),
        config: node.data.config,
      }));

      const apiEdges = edges.map((edge) => ({
        edge_id: edge.id,
        source_node_id: edge.source,
        target_node_id: edge.target,
      }));

      await saveWorkflow('My Workflow', apiNodes, apiEdges);
      setSaveMessage('Workflow saved!');
    } catch (error) {
      setSaveMessage('Failed to save');
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(null), 2000);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <div className="logo">
          <div className="logo-icon">
            <span>AI</span>
          </div>
          <span className="logo-text">GenAI Stack</span>
        </div>
      </div>

      <div className="navbar-center">
        {validation && (
          <div className={`validation-status ${validation.is_valid ? 'valid' : 'invalid'}`}>
            {validation.is_valid ? (
              <>
                <CheckCircle size={16} />
                <span>Workflow is valid</span>
              </>
            ) : (
              <>
                <AlertCircle size={16} />
                <span>{validation.errors[0] || 'Invalid workflow'}</span>
              </>
            )}
          </div>
        )}
      </div>

      <div className="navbar-right">
        <button className="nav-btn clear-btn" onClick={clearWorkflow} title="Clear workflow">
          <Trash2 size={16} />
        </button>
        
        <button 
          className={`nav-btn build-btn ${isValidated ? 'validated' : ''}`}
          onClick={handleBuildStack}
          disabled={isValidating}
        >
          {isValidating ? (
            <Loader2 size={16} className="spin" />
          ) : isValidated ? (
            <CheckCircle size={16} />
          ) : (
            <Play size={16} />
          )}
          <span>{isValidating ? 'Validating...' : isValidated ? 'Validated' : 'Build Stack'}</span>
        </button>

        <button 
          className="nav-btn save-btn"
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <Loader2 size={16} className="spin" />
          ) : (
            <Save size={16} />
          )}
          <span>{saveMessage || 'Save'}</span>
        </button>

        <div className="user-avatar">D</div>
      </div>
    </nav>
  );
}
