import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function DashboardHome() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to load stats", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="fade-in">
        <h1 style={{ fontSize: '1.75rem', marginBottom: 'var(--space-sm)' }}>
          Welcome back 👋
        </h1>
        <p className="text-secondary" style={{ marginBottom: 'var(--space-2xl)' }}>
          Here's an overview of your AI knowledge base.
        </p>
      </div>

      <div className="stats-grid fade-in" style={{ animationDelay: '100ms' }}>
        <div className="glass-panel stat-card">
          <span className="stat-label">Documents</span>
          <span className="stat-value">
            {loading ? '...' : stats?.documents || 0}
          </span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-label">Conversations</span>
          <span className="stat-value">
            {loading ? '...' : stats?.conversations || 0}
          </span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-label">Chunks Indexed</span>
          <span className="stat-value">
            {loading ? '...' : stats?.chunks || 0}
          </span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-label">Messages</span>
          <span className="stat-value">
            {loading ? '...' : stats?.messages || 0}
          </span>
        </div>
      </div>
    </>
  );
}
