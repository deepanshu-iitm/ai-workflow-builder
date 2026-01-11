import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, Bot, User, Sparkles, Clock, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useWorkflowStore } from '../store/workflowStore';
import { executeQuery } from '../api';
import type { ChatMessage } from '../types';
import './ChatModal.css';

export default function ChatModal() {
  const { isChatOpen, setChatOpen, nodes, edges, isValidated, validation } = useWorkflowStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isChatOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isChatOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      extra_data: {},
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Convert nodes and edges to API format
      const apiNodes = nodes.map((node) => ({
        id: node.id,
        type: node.type,
        node_type: node.type,
        config: node.data.config,
        data: { config: node.data.config },
      }));

      const apiEdges = edges.map((edge) => ({
        source: edge.source,
        target: edge.target,
      }));

      const response = await executeQuery(
        userMessage.content,
        apiNodes,
        apiEdges,
        sessionId || undefined
      );

      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        execution_time_ms: response.execution_time_ms,
        tokens_used: response.tokens_used,
        model_used: response.model_used,
        extra_data: response.metadata,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError('Failed to get response. Please check your workflow configuration.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setChatOpen(false);
  };

  if (!isChatOpen) return null;

  return (
    <div className="chat-overlay" onClick={handleClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <div className="chat-header-left">
            <div className="chat-icon">
              <Sparkles size={20} />
            </div>
            <div>
              <h2>Chat with AI Stack</h2>
              <span className="chat-subtitle">
                {isValidated ? 'Workflow validated' : 'Run Build Stack first'}
              </span>
            </div>
          </div>
          <button className="chat-close" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>

        {!isValidated && validation && !validation.is_valid && (
          <div className="chat-warning">
            <AlertCircle size={16} />
            <span>
              Please fix workflow errors before chatting. 
              {validation.errors[0] && ` Error: ${validation.errors[0]}`}
            </span>
          </div>
        )}

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <div className="empty-icon">💬</div>
              <h3>Start a Conversation</h3>
              <p>Ask questions and the AI will process them through your workflow.</p>
              <div className="example-queries">
                <span>Try asking:</span>
                <button onClick={() => setInput('What can you help me with?')}>
                  What can you help me with?
                </button>
                <button onClick={() => setInput('Summarize the uploaded documents')}>
                  Summarize the uploaded documents
                </button>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-role">
                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                  </span>
                  {message.execution_time_ms && (
                    <span className="message-meta">
                      <Clock size={12} />
                      {message.execution_time_ms}ms
                    </span>
                  )}
                </div>
                <div className="message-body">
                  {message.role === 'assistant' ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  ) : (
                    message.content
                  )}
                </div>
                {message.model_used && (
                  <div className="message-footer">
                    <span className="model-badge">{message.model_used}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant loading">
              <div className="message-avatar">
                <Bot size={18} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="chat-error">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <div className="chat-input-container">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading || !isValidated}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading || !isValidated}
              className="send-btn"
            >
              {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
