import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // System Status
  getStatus: () => apiClient.get('/status'),

  // Documents
  uploadDocuments: (formData) =>
    apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getDocuments: () => apiClient.get('/documents'),
  getDocument: (id) => apiClient.get(`/documents/${id}`),
  deleteDocument: (id) => apiClient.delete(`/documents/${id}`),

  // Chat
  sendMessage: (payload) => apiClient.post('/chat', payload),

  // Comparative Analysis
  runComparison: (payload) => apiClient.post('/comparative', payload),
  getComparisons: () => apiClient.get('/comparative'),
  getComparison: (id) => apiClient.get(`/comparative/${id}`),

  // Paper Summarization
  getSummary: (documentId, regenerate = false) =>
    apiClient.post('/summary', { document_id: documentId, regenerate }),

  // Research Sessions
  createSession: (payload) => apiClient.post('/sessions', payload),
  getSessions: () => apiClient.get('/sessions'),
  getSession: (id) => apiClient.get(`/sessions/${id}`),
  updateSessionDocuments: (id, docIds) =>
    apiClient.put(`/sessions/${id}/documents`, docIds),
  deleteSession: (id) => apiClient.delete(`/sessions/${id}`),
};

