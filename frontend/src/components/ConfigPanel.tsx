import { useState, useEffect } from 'react';
import { X, Upload, Trash2, FileText, Check, AlertCircle } from 'lucide-react';
import { useWorkflowStore } from '../store/workflowStore';
import { uploadDocument, getDocuments, deleteDocument } from '../api';
import type { Document } from '../types';
import './ConfigPanel.css';

export default function ConfigPanel() {
  const { selectedNode, updateNode, selectNode, documents, setDocuments, addDocument, removeDocument } = useWorkflowStore();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const result = await getDocuments();
      setDocuments(result.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const document = await uploadDocument(file);
      addDocument(document);
    } catch (error) {
      setUploadError('Failed to upload file. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await deleteDocument(docId);
      removeDocument(docId);
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  const handleConfigChange = (key: string, value: unknown) => {
    if (!selectedNode) return;
    
    updateNode(selectedNode.id, {
      config: {
        ...selectedNode.data.config,
        [key]: value,
      },
    });
  };

  const toggleDocumentSelection = (docId: string) => {
    if (!selectedNode) return;
    
    const currentDocs = selectedNode.data.config.document_ids || [];
    const newDocs = currentDocs.includes(docId)
      ? currentDocs.filter((id: string) => id !== docId)
      : [...currentDocs, docId];
    
    handleConfigChange('document_ids', newDocs);
  };

  if (!selectedNode) {
    return (
      <aside className="config-panel">
        <div className="config-empty">
          <div className="empty-icon">⚙️</div>
          <h3>No Component Selected</h3>
          <p>Click on a component in the canvas to configure it.</p>
        </div>
      </aside>
    );
  }

  const nodeType = selectedNode.type.toLowerCase();

  return (
    <aside className="config-panel">
      <div className="config-header">
        <h2>Configure {selectedNode.data.label}</h2>
        <button className="close-btn" onClick={() => selectNode(null)}>
          <X size={18} />
        </button>
      </div>

      <div className="config-content">
        {/* Common: Label */}
        <div className="config-group">
          <label>Label</label>
          <input
            type="text"
            value={selectedNode.data.label}
            onChange={(e) => updateNode(selectedNode.id, { label: e.target.value })}
            placeholder="Component label"
          />
        </div>

        {/* Input Node Config */}
        {nodeType === 'input' && (
          <div className="config-group">
            <label>Placeholder Text</label>
            <input
              type="text"
              value={selectedNode.data.config.placeholder || ''}
              onChange={(e) => handleConfigChange('placeholder', e.target.value)}
              placeholder="Enter your question..."
            />
          </div>
        )}

        {/* Knowledge Base Node Config */}
        {nodeType === 'knowledgebase' && (
          <>
            <div className="config-group">
              <label>Documents</label>
              <div className="document-upload">
                <input
                  type="file"
                  id="file-upload"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  hidden
                />
                <label htmlFor="file-upload" className={`upload-btn ${isUploading ? 'uploading' : ''}`}>
                  <Upload size={16} />
                  {isUploading ? 'Uploading...' : 'Upload Document'}
                </label>
              </div>
              
              {uploadError && (
                <div className="upload-error">
                  <AlertCircle size={14} />
                  {uploadError}
                </div>
              )}

              <div className="document-list">
                {documents.map((doc: Document) => (
                  <div key={doc.id} className="document-item">
                    <div 
                      className={`doc-select ${
                        (selectedNode.data.config.document_ids || []).includes(doc.id) 
                          ? 'selected' 
                          : ''
                      }`}
                      onClick={() => toggleDocumentSelection(doc.id)}
                    >
                      <div className="doc-icon">
                        <FileText size={16} />
                      </div>
                      <div className="doc-info">
                        <span className="doc-name">{doc.original_filename}</span>
                        <span className="doc-status">
                          {doc.status === 'completed' && <Check size={12} />}
                          {doc.status}
                        </span>
                      </div>
                    </div>
                    <button 
                      className="doc-delete"
                      onClick={() => handleDeleteDocument(doc.id)}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
                
                {documents.length === 0 && (
                  <div className="no-documents">
                    No documents uploaded yet
                  </div>
                )}
              </div>
            </div>

            <div className="config-group">
              <label>Top K Results</label>
              <input
                type="number"
                min={1}
                max={20}
                value={selectedNode.data.config.top_k || 5}
                onChange={(e) => handleConfigChange('top_k', parseInt(e.target.value))}
              />
              <span className="config-hint">Number of relevant chunks to retrieve</span>
            </div>
          </>
        )}

        {/* LLM Node Config */}
        {nodeType === 'llm' && (
          <>
            <div className="config-group">
              <label>Model</label>
              <select
                value={selectedNode.data.config.model || 'gemini-2.0-flash'}
                onChange={(e) => handleConfigChange('model', e.target.value)}
              >
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="gemini-pro">Gemini Pro</option>
              </select>
            </div>

            <div className="config-group">
              <label>Temperature: {selectedNode.data.config.temperature ?? 0.7}</label>
              <input
                type="range"
                min={0}
                max={1}
                step={0.1}
                value={selectedNode.data.config.temperature ?? 0.7}
                onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
              />
              <span className="config-hint">Higher = more creative, Lower = more focused</span>
            </div>

            <div className="config-group">
              <label>Max Tokens</label>
              <input
                type="number"
                min={100}
                max={8192}
                step={100}
                value={selectedNode.data.config.max_tokens || 2048}
                onChange={(e) => handleConfigChange('max_tokens', parseInt(e.target.value))}
              />
            </div>

            <div className="config-group">
              <label>System Prompt</label>
              <textarea
                value={selectedNode.data.config.system_prompt || ''}
                onChange={(e) => handleConfigChange('system_prompt', e.target.value)}
                placeholder="You are a helpful assistant..."
                rows={4}
              />
            </div>

            <div className="config-group toggle-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={selectedNode.data.config.enable_web_search || false}
                  onChange={(e) => handleConfigChange('enable_web_search', e.target.checked)}
                />
                <span className="toggle-slider"></span>
                Enable Web Search
              </label>
              <span className="config-hint">Search the web for real-time information</span>
            </div>
          </>
        )}

        {/* Output Node Config */}
        {nodeType === 'output' && (
          <div className="config-group">
            <label>Output Format</label>
            <select
              value={selectedNode.data.config.format || 'markdown'}
              onChange={(e) => handleConfigChange('format', e.target.value)}
            >
              <option value="text">Plain Text</option>
              <option value="markdown">Markdown</option>
              <option value="json">JSON</option>
            </select>
          </div>
        )}
      </div>
    </aside>
  );
}
