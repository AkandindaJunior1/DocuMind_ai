import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// This component wraps any page that requires login.
// If the user is NOT logged in, it redirects them to /login.
// If they ARE logged in, it renders the child page normally.
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    // Show a minimal loading state while we check the token
    return (
      <div className="auth-page">
        <div className="spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
