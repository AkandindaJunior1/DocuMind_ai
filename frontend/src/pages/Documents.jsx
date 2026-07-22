import React, { useState, useEffect } from 'react';
import api from '../services/api';
import UploadModal from '../components/UploadModal';

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to fetch documents", err);
      showToast("Failed to load documents", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document? This cannot be undone.")) return;
    
    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter(doc => doc.id !== id));
      showToast("Document deleted successfully", "success");
    } catch (err) {
      console.error("Failed to delete document", err);
      showToast("Failed to delete document", "error");
    }
  };

  const handleUploadSuccess = () => {
    setIsUploadModalOpen(false);
    showToast("Document uploaded! Processing started.", "success");
    fetchDocuments();
  };

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', paddingTop: 'var(--space-2xl)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
        <h2>Document Management</h2>
        <button className="btn-primary" onClick={() => setIsUploadModalOpen(true)}>
          + Upload Document
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 'var(--space-2xl)', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div style={{ padding: 'var(--space-3xl)', textAlign: 'center' }}>
            <h3 style={{ marginBottom: 'var(--space-md)' }}>No documents yet</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>
              Upload your first document to start querying it with AI.
            </p>
            <button className="btn-primary" onClick={() => setIsUploadModalOpen(true)}>
              Upload Document
            </button>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--bg-overlay)', textAlign: 'left' }}>
                <th style={{ padding: 'var(--space-md) var(--space-lg)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Filename</th>
                <th style={{ padding: 'var(--space-md)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Type</th>
                <th style={{ padding: 'var(--space-md)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Status</th>
                <th style={{ padding: 'var(--space-md)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Uploaded</th>
                <th style={{ padding: 'var(--space-md)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} style={{ borderTop: '1px solid var(--border-subtle)', transition: 'background var(--duration-fast)' }}>
                  <td style={{ padding: 'var(--space-md) var(--space-lg)' }}>
                    <span style={{ fontWeight: 500 }}>{doc.filename}</span>
                  </td>
                  <td style={{ padding: 'var(--space-md)' }}>
                    <span style={{ 
                      padding: '2px 8px', 
                      borderRadius: 'var(--radius-sm)', 
                      background: 'var(--bg-overlay)',
                      fontSize: '0.8rem',
                      textTransform: 'uppercase',
                      fontWeight: 500,
                      color: 'var(--text-secondary)'
                    }}>
                      {doc.file_type}
                    </span>
                  </td>
                  <td style={{ padding: 'var(--space-md)' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '0.875rem',
                      color: doc.status === 'completed' ? 'var(--success)' : 
                             doc.status === 'failed' ? 'var(--error)' : 
                             'var(--warning)'
                    }}>
                      <span style={{
                        width: '8px', height: '8px', borderRadius: '50%',
                        background: 'currentColor'
                      }}></span>
                      {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                    </span>
                  </td>
                  <td style={{ padding: 'var(--space-md)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    {formatDate(doc.created_at)}
                  </td>
                  <td style={{ padding: 'var(--space-md)', textAlign: 'right' }}>
                    <button 
                      onClick={() => handleDelete(doc.id)}
                      style={{
                        background: 'none',
                        border: '1px solid transparent',
                        color: 'var(--error)',
                        cursor: 'pointer',
                        padding: 'var(--space-xs) var(--space-sm)',
                        borderRadius: 'var(--radius-sm)',
                        transition: 'all 0.2s',
                        fontSize: '0.875rem',
                        fontFamily: 'inherit',
                        fontWeight: 500
                      }}
                      onMouseOver={(e) => { e.target.style.background = '#fef2f2'; e.target.style.borderColor = '#fecaca'; }}
                      onMouseOut={(e) => { e.target.style.background = 'none'; e.target.style.borderColor = 'transparent'; }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <UploadModal 
        isOpen={isUploadModalOpen} 
        onClose={() => setIsUploadModalOpen(false)} 
        onSuccess={handleUploadSuccess} 
      />

      {/* TOAST NOTIFICATION */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: 'var(--space-xl)',
          right: 'var(--space-xl)',
          background: toast.type === 'error' ? 'var(--error)' : 'var(--success)',
          color: 'white',
          padding: 'var(--space-md) var(--space-lg)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          animation: 'slideUp 0.3s ease-out',
          zIndex: 1000,
          fontSize: '0.875rem',
          fontWeight: 500
        }}>
          {toast.message}
        </div>
      )}
      
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
