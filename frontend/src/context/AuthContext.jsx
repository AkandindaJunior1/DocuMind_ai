import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

// 1. Create the Context — think of it as a "global state container"
//    Any component anywhere in the app can reach into this container
//    and check: "Is the user logged in? What's their name?"
const AuthContext = createContext(null);

// 2. Create the Provider — this wraps our entire app and manages the auth state
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, check if we have a saved token and fetch the user profile
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          // Token is expired or invalid — clean it up
          localStorage.removeItem('token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Login: call the API, save the token, then fetch the user profile
  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('token', data.access_token);
    const userData = await api.getMe();
    setUser(userData);
    return userData;
  };

  // Register: call the API (doesn't auto-login, user goes to login page after)
  const register = async (formData) => {
    return await api.register(formData);
  };

  // Logout: clear everything
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// 3. Custom hook — makes it easy to use: const { user, login } = useAuth();
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
