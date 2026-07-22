import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import MessageBubble from './MessageBubble';

export default function ChatLayout() {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConversation) {
        selectConversation(data[0]);
      }
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  };

  const selectConversation = async (conv) => {
    setActiveConversation(conv);
    try {
      const data = await api.getMessages(conv.id);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages", err);
    }
  };

  const handleNewChat = async () => {
    try {
      const newConv = await api.createConversation();
      setConversations([newConv, ...conversations]);
      setActiveConversation(newConv);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create chat", err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !activeConversation) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.streamMessage(activeConversation.id, userMessage.content);
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let streamingContent = "";
      setMessages(prev => [...prev, { id: 'streaming-msg', role: 'ai', content: streamingContent, isStreaming: true }]);
      setIsLoading(false);
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        streamingContent += chunk;
        
        setMessages(prev => prev.map(msg => 
          msg.id === 'streaming-msg' ? { ...msg, content: streamingContent } : msg
        ));
      }
      
      // Mark as done streaming
      setMessages(prev => prev.map(msg => 
        msg.id === 'streaming-msg' ? { ...msg, isStreaming: false, id: Date.now().toString() } : msg
      ));
      
      fetchConversations();
    } catch (err) {
      console.error("Failed to send message", err);
      
      setMessages(prev => {
        const withoutStreaming = prev.filter(msg => msg.id !== 'streaming-msg');
        return [...withoutStreaming, { 
          role: 'system', 
          content: `Error: ${err.message || 'Failed to get response'}` 
        }];
      });
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 120px)', marginTop: 'var(--space-lg)', gap: 'var(--space-lg)', padding: '0 var(--space-lg)' }}>
      {/* SIDEBAR */}
      <div className="glass-panel" style={{ 
        width: '260px', 
        display: 'flex', 
        flexDirection: 'column',
        padding: 'var(--space-md)',
        flexShrink: 0
      }}>
        <button 
          className="btn-primary" 
          style={{ width: '100%', marginBottom: 'var(--space-md)' }}
          onClick={handleNewChat}
        >
          + New Chat
        </button>
        
        <div style={{ overflowY: 'auto', flex: 1 }}>
          {conversations.map(conv => (
            <div 
              key={conv.id}
              onClick={() => selectConversation(conv)}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: 'var(--space-xs)',
                cursor: 'pointer',
                background: activeConversation?.id === conv.id ? 'var(--accent-lighter)' : 'transparent',
                borderLeft: activeConversation?.id === conv.id ? '3px solid var(--accent-primary)' : '3px solid transparent',
                color: activeConversation?.id === conv.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                fontWeight: activeConversation?.id === conv.id ? 600 : 400,
                transition: 'all var(--duration-fast) var(--ease-out)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                fontSize: '0.875rem'
              }}
            >
              {conv.title}
            </div>
          ))}
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div className="glass-panel" style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        padding: '0',
        minWidth: 0
      }}>
        
        {/* Chat Messages */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: 'var(--space-2xl)',
        }}>
          {messages.length === 0 ? (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-secondary)' }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 'var(--space-md)', opacity: 0.6 }}>
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <h3 style={{ color: 'var(--text-primary)' }}>DocuMind AI</h3>
              <p>Ask a question about your uploaded documents.</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <MessageBubble key={msg.id || i} message={msg} />
            ))
          )}
          {isLoading && (
            <div style={{ display: 'flex', gap: 'var(--space-sm)', color: 'var(--text-secondary)', padding: 'var(--space-md)' }}>
              <span className="spinner" style={{ width: '16px', height: '16px' }} />
              <span style={{ fontSize: '0.875rem' }}>Searching documents...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: 'var(--space-lg)', borderTop: '1px solid var(--border-subtle)' }}>
          <form onSubmit={handleSend} style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="input-glass"
              style={{ flex: 1, margin: 0, padding: '0.8rem 1rem' }}
              disabled={isLoading || !activeConversation}
            />
            <button 
              type="submit" 
              className="btn-primary" 
              disabled={!input.trim() || isLoading || !activeConversation}
              style={{ padding: '0 var(--space-xl)', whiteSpace: 'nowrap' }}
            >
              Send
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
