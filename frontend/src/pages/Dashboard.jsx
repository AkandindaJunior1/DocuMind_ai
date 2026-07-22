import { useAuth } from '../context/AuthContext';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';

// Simple inline SVG icon component — no emojis, no external libraries
function Icon({ name, size = 18 }) {
  const icons = {
    dashboard: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1"/>
        <rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
    ),
    documents: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    ),
    chat: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
    settings: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    ),
    logout: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
        <polyline points="16 17 21 12 16 7"/>
        <line x1="21" y1="12" x2="9" y2="12"/>
      </svg>
    ),
  };
  return icons[name] || null;
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.email?.slice(0, 2).toUpperCase() || '?';
  const isChat = location.pathname.includes('/chat');

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-primary)' }}>✦</span>
          <h2>DocuMind</h2>
        </div>

        <nav className="sidebar-nav">
          <NavLink 
            to="/dashboard" 
            end
            className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}
          >
            <Icon name="dashboard" /> Dashboard
          </NavLink>
          <NavLink 
            to="/dashboard/documents" 
            className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}
          >
            <Icon name="documents" /> Documents
          </NavLink>
          <NavLink 
            to="/dashboard/chat" 
            className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}
          >
            <Icon name="chat" /> Chat
          </NavLink>
        </nav>

        <div className="sidebar-user">
          <div className="sidebar-avatar">{initials}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.email || 'User'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
              {user?.role || 'member'}
            </div>
          </div>
          <button onClick={handleLogout} className="btn-ghost" style={{ padding: '0.4rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Icon name="logout" size={14} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content" style={{ padding: isChat ? '0' : 'var(--space-2xl)' }}>
        <Outlet />
      </main>
    </div>
  );
}
