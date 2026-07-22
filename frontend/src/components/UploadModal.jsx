import { useState } from 'react';
import api from '../services/api';

export default function UploadModal({ isOpen, onClose }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError('');
    
    try {
      await api.uploadDocument(file);
      setSuccess(true);
      setFile(null);
      
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 2000);
      
    } catch (err) {
      setError(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !isUploading) {
      onClose();
    }
  };

  return (
    <div className="modal-backdrop fade-in" onClick={handleBackdropClick}>
      <div className="modal-content glass-panel" style={{ width: '100%', maxWidth: '500px', animationDelay: '50ms' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
          <h2 style={{ fontSize: '1.25rem' }}>Upload Document</h2>
          <button onClick={onClose} className="btn-icon" disabled={isUploading}>✕</button>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 'var(--space-md)' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: 'var(--space-md)' }}>Document uploaded successfully! AI is processing it.</div>}

        <div className="upload-zone">
          <input 
            type="file" 
            id="file-upload" 
            className="file-input" 
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt,.csv,.xlsx"
            disabled={isUploading}
          />
          <label htmlFor="file-upload" className="upload-label">
            <span style={{ fontSize: '2rem', marginBottom: 'var(--space-sm)' }}>📄</span>
            {file ? (
              <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{file.name}</span>
            ) : (
              <span>Click to select or drag and drop<br/><small className="text-secondary">PDF, DOCX, TXT, CSV, XLSX</small></span>
            )}
          </label>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)', marginTop: 'var(--space-xl)' }}>
          <button className="btn-ghost" onClick={onClose} disabled={isUploading}>Cancel</button>
          <button 
            className="btn-primary" 
            onClick={handleUpload} 
            disabled={!file || isUploading}
          >
            {isUploading ? <span className="spinner" /> : 'Upload & Process'}
          </button>
        </div>

      </div>
    </div>
  );
}
