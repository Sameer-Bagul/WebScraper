import axios from 'axios'

const API_BASE = 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
})

export const scraperAPI = {
  // Get all jobs
  getJobs: () => api.get('/api/jobs'),
  
  // Get job results
  getJobResults: (jobId) => api.get(`/api/jobs/${jobId}/results`),
  
  // Start scraping
  scrapeJobs: (data) => api.post('/api/scrape/jobs', data),
  scrapeLeads: (data) => api.post('/api/scrape/leads', data),
  
  // Get statistics
  getStats: () => api.get('/api/stats'),
  
  // Admin actions
  clearData: () => api.post('/admin/clear-data'),
}

export default api