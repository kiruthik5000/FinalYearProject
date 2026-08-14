import axios from 'axios';

// Base API configuration (FastAPI default: http://localhost:8000)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// System Health Check (GET /)
export const checkHealth = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    return { status: 'offline', message: 'Backend unreachable' };
  }
};

// Get Ingested Files & Links (GET /api/files)
export const getIngestedFiles = async () => {
  try {
    const response = await api.get('/api/files');
    return response.data?.files || [];
  } catch (error) {
    console.error('Error fetching files:', error);
    throw error;
  }
};

// Submit RAG Query (POST /api/chat)
export const sendChatQuery = async (queryText) => {
  try {
    const response = await api.post('/api/chat', { query: queryText });
    return response.data;
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
};

// Upload Document File (POST /api/upload)
export const uploadDocument = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  } catch (error) {
    console.error('File upload error:', error);
    throw error;
  }
};

// Ingest Website URL (POST /api/url)
export const ingestWebsiteUrl = async (url) => {
  try {
    const response = await api.post('/api/url', { url });
    return response.data;
  } catch (error) {
    console.error('URL ingestion error:', error);
    throw error;
  }
};

// Web Search (POST /api/websearch) — long-running, needs extended timeout
export const webSearch = async (query) => {
  try {
    const response = await api.post('/api/websearch', { query }, {
      timeout: 120000, // 2 minutes — web search can be slow
    });
    return response.data;
  } catch (error) {
    console.error('Web search error:', error);
    throw error;
  }
};

// Fetch and open source PDF in a new tab
export const openSourcePdf = async (pdfName, startPage, noOfPages = 1) => {
  try {
    const url = `/api/source/get_pdf?pdf_name=${encodeURIComponent(pdfName)}&start_page=${startPage}&no_of_pages=${noOfPages}`;
    const response = await api.get(url, { responseType: 'blob' });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const objectUrl = URL.createObjectURL(blob);
    
    // Open in new tab
    window.open(objectUrl, '_blank');
    
    // Clean up after enough time for the browser to load it
    setTimeout(() => URL.revokeObjectURL(objectUrl), 10000);
  } catch (error) {
    console.error('Error fetching source PDF:', error);
    throw error;
  }
};

export default api;
