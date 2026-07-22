const API_URL = 'http://localhost:8000';

// Helper to get the stored JWT token
function getToken() {
  return localStorage.getItem('token');
}

// Helper to make authenticated requests
async function request(endpoint, options = {}) {
  const token = getToken();
  
  const headers = { ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Something went wrong' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

const api = {
  // Register a new user + organization
  register(data) {
    return request('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: data.email,
        password: data.password,
        organization_name: data.organizationName,
        full_name: data.fullName,
      }),
    });
  },

  // Login — FastAPI OAuth2 expects form-encoded data, not JSON
  login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    return request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
  },

  // Get the logged-in user's profile (protected endpoint)
  getMe() {
    return request('/auth/me');
  },

  // Upload a document (multipart form data)
  uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // We don't set Content-Type header here because fetch will automatically
    // set it to multipart/form-data with the correct boundary when passing a FormData body.
    return request('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // --- CHAT API ---

  // Start a new conversation
  createConversation() {
    return request('/chat/conversations', {
      method: 'POST',
    });
  },

  // Get all conversations for sidebar
  getConversations() {
    return request('/chat/conversations');
  },

  // Get history of a specific conversation
  getMessages(conversationId) {
    return request(`/chat/conversations/${conversationId}/messages`);
  },

  // Send a message and expect a JSON response (old way)
  sendMessage(conversationId, content) {
    return request(`/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
  },

  // Send a message and stream the response (new way)
  async streamMessage(conversationId, content) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response;
  },

  // Dashboard Stats
  getStats() {
    return request('/dashboard/stats');
  },

  // Documents
  getDocuments() {
    return request('/documents/');
  },
  
  deleteDocument(documentId) {
    return request(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }
};

export default api;
