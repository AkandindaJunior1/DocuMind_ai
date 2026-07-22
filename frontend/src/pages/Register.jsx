import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    fullName: '',
    organizationName: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">

      <div className="auth-header fade-in">
        <h1>DocuMind AI</h1>
        <p>Create your organization's AI workspace</p>
      </div>

      <div className="glass-panel auth-card fade-in" style={{ animationDelay: '100ms', maxWidth: '480px' }}>
        <form onSubmit={handleRegister} className="auth-form">

          {error && <div className="alert alert-error">{error}</div>}

          <div className="auth-form-row">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="fullName"
                className="input-glass"
                placeholder="John Doe"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Company</label>
              <input
                type="text"
                name="organizationName"
                className="input-glass"
                placeholder="Acme Corp"
                value={formData.organizationName}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Work Email</label>
            <input
              type="email"
              name="email"
              className="input-glass"
              placeholder="name@company.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="input-glass"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? <span className="spinner" /> : 'Create Account'}
          </button>

        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>

    </div>
  );
}
