import React from 'react';

export default function MessageBubble({ message }) {
  const isAI = message.role === 'ai' || message.role === 'system';
  
  return (
    <div style={{
      display: 'flex',
      marginBottom: 'var(--space-lg)',
      justifyContent: isAI ? 'flex-start' : 'flex-end',
      animation: 'fadeIn var(--duration-fast) var(--ease-out)',
    }}>
      <div style={{
        maxWidth: '80%',
        padding: 'var(--space-md) var(--space-lg)',
        borderRadius: 'var(--radius-lg)',
        background: isAI ? 'var(--bg-overlay)' : 'var(--accent-primary)',
        border: isAI ? '1px solid var(--border-subtle)' : 'none',
        color: isAI ? 'var(--text-primary)' : '#fff',
        boxShadow: 'var(--shadow-sm)',
        borderBottomLeftRadius: isAI ? '4px' : 'var(--radius-lg)',
        borderBottomRightRadius: !isAI ? '4px' : 'var(--radius-lg)',
      }}>
        {isAI && (
          <div style={{ 
            fontSize: '0.7rem', 
            color: 'var(--accent-primary)', 
            marginBottom: 'var(--space-xs)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            fontWeight: 700
          }}>
            DocuMind AI
          </div>
        )}
        <div style={{ 
          lineHeight: 1.7, 
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          fontSize: '0.9375rem'
        }}>
          {message.content}
          {message.isStreaming && (
            <span style={{
              display: 'inline-block',
              width: '2px',
              height: '15px',
              background: 'var(--accent-primary)',
              marginLeft: '4px',
              animation: 'blink 1s step-end infinite'
            }} />
          )}
        </div>
      </div>

      <style>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
