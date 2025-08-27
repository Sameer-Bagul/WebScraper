import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API methods
export const apiClient = {
  // Health check
  health: () => api.get('/health'),
  
  // Adapters
  getAdapters: () => api.get('/adapters'),
  
  // Search
  searchUrls: (query, maxResults = 20) => 
    api.post('/search', { query, max_results: maxResults }),
  
  // Jobs
  createJob: (jobData) => api.post('/jobs', jobData),
  getJobStatus: (jobId) => api.get(`/jobs/${jobId}/status`),
  getJobResults: (jobId) => api.get(`/jobs/${jobId}/results`),
  listJobs: () => api.get('/jobs'),
  
  // Stats
  getStats: () => api.get('/stats'),
}

export default api