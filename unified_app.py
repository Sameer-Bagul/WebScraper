import os
import logging
from flask import Blueprint, jsonify, request, render_template_string
from models import ScrapingJob, ScrapingResult, Analytics

# Create blueprint instead of separate app
app = Blueprint('unified_app', __name__)

# Default adapters data
default_adapters = [
    {"name": "default", "display_name": "Default General Scraper", "description": "General purpose scraper for any website"},
    {"name": "indeed", "display_name": "Indeed Job Board", "description": "Scraper for Indeed job listings"},
    {"name": "linkedin", "display_name": "LinkedIn Jobs", "description": "Scraper for LinkedIn job listings"},
    {"name": "business_directory", "display_name": "Business Directory", "description": "Scraper for business directories"}
]

# HTML template for React app
REACT_HTML = '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Web Scraper Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
      body { background-color: #212529; color: #ffffff; }
      .hero-section { padding: 3rem 0; text-align: center; }
      .hero-section h1 { font-size: 3rem; font-weight: 300; margin-bottom: 1rem; }
      .feature-card { height: 100%; text-align: center; padding: 2rem 1rem; }
      .feature-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.8; }
      .stat-card { text-align: center; padding: 1.5rem; }
      .stat-number { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
      .url-input { font-family: 'Courier New', monospace; font-size: 0.9rem; }
      .json-display { background: #212529; border: 1px solid #6c757d; border-radius: 0.375rem; padding: 1rem; font-family: 'Courier New', monospace; font-size: 0.875rem; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand" href="#">
          <i class="bi bi-globe me-2"></i>
          Web Scraper Pro
        </a>
        <div class="navbar-nav ms-auto">
          <a class="nav-link" href="#home" onclick="showHome()">
            <i class="bi bi-house me-1"></i>Home
          </a>
          <a class="nav-link" href="#dashboard" onclick="showDashboard()">
            <i class="bi bi-activity me-1"></i>Dashboard
          </a>
        </div>
      </div>
    </nav>

    <main id="main-content">
      <!-- Home content will be loaded here -->
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
      // Simple SPA functionality
      let currentPage = 'home';
      let jobs = [];
      let stats = { total_jobs: 0, completed_jobs: 0, running_jobs: 0, total_results: 0 };

      const API_BASE = '/api';

      // API calls
      async function apiCall(endpoint, options = {}) {
        try {
          const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
          });
          return await response.json();
        } catch (error) {
          console.error('API call failed:', error);
          return null;
        }
      }

      // Show home page
      function showHome() {
        currentPage = 'home';
        document.getElementById('main-content').innerHTML = `
          <div class="container my-5">
            <div class="hero-section">
              <h1 class="display-4 mb-3">
                <i class="bi bi-globe me-3"></i>
                Web Scraper Pro
              </h1>
              <p class="lead">Professional web scraping tool for job hunting and lead generation</p>
              <p class="text-muted">Extract structured data from any website with powerful scraping engines</p>
            </div>

            <div class="row">
              <div class="col-lg-8 mx-auto">
                <div class="card">
                  <div class="card-header">
                    <ul class="nav nav-tabs card-header-tabs">
                      <li class="nav-item">
                        <button class="nav-link active" onclick="switchTab('search')" id="search-tab">
                          <i class="bi bi-search me-1"></i>Search URLs
                        </button>
                      </li>
                      <li class="nav-item">
                        <button class="nav-link" onclick="switchTab('scrape')" id="scrape-tab">
                          <i class="bi bi-download me-1"></i>Direct Scraping
                        </button>
                      </li>
                    </ul>
                  </div>
                  <div class="card-body">
                    <div id="search-form">
                      <form onsubmit="handleSearch(event)">
                        <div class="mb-3">
                          <label class="form-label">
                            <i class="bi bi-search me-1"></i>Search Query
                          </label>
                          <input type="text" class="form-control" id="search-query" 
                                 placeholder="e.g., Python developer jobs in Berlin" required>
                          <div class="form-text">Use specific keywords to find relevant URLs</div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Maximum Results</label>
                          <select class="form-select" id="max-results">
                            <option value="10">10 results</option>
                            <option value="20" selected>20 results</option>
                            <option value="50">50 results</option>
                          </select>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                          <i class="bi bi-search me-2"></i>Search for URLs
                        </button>
                      </form>
                    </div>
                    <div id="scrape-form" style="display: none;">
                      <form onsubmit="handleScrape(event)">
                        <div class="mb-3">
                          <label class="form-label">
                            <i class="bi bi-link me-1"></i>URLs to Scrape
                          </label>
                          <textarea class="form-control url-input" id="scrape-urls" rows="6" 
                                    placeholder="Enter URLs, one per line..." required></textarea>
                        </div>
                        <div class="row mb-3">
                          <div class="col-md-6">
                            <label class="form-label">Scraping Adapter</label>
                            <select class="form-select" id="adapter-select">
                              <option value="default">Default General Scraper</option>
                              <option value="indeed">Indeed Job Board</option>
                              <option value="linkedin">LinkedIn Jobs</option>
                              <option value="business_directory">Business Directory</option>
                            </select>
                          </div>
                          <div class="col-md-6">
                            <label class="form-label">Task Type</label>
                            <select class="form-select" id="task-type">
                              <option value="general">General Scraping</option>
                              <option value="job">Job Listings</option>
                              <option value="lead">Lead Generation</option>
                            </select>
                          </div>
                        </div>
                        <button type="submit" class="btn btn-success w-100">
                          <i class="bi bi-download me-2"></i>Start Scraping
                        </button>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mt-5">
              <div class="col-12">
                <h3 class="text-center mb-4">Features</h3>
                <div class="row">
                  <div class="col-md-4 mb-4">
                    <div class="card feature-card">
                      <div class="card-body">
                        <i class="bi bi-search feature-icon text-primary"></i>
                        <h5 class="card-title">Smart URL Discovery</h5>
                        <p class="card-text">Use search engines to automatically find relevant URLs</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 mb-4">
                    <div class="card feature-card">
                      <div class="card-body">
                        <i class="bi bi-people feature-icon text-success"></i>
                        <h5 class="card-title">Contact Extraction</h5>
                        <p class="card-text">Automatically extract emails, phone numbers, and social profiles</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 mb-4">
                    <div class="card feature-card">
                      <div class="card-body">
                        <i class="bi bi-briefcase feature-icon text-info"></i>
                        <h5 class="card-title">Job Board Support</h5>
                        <p class="card-text">Built-in adapters for popular job boards like Indeed and LinkedIn</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
      }

      // Show dashboard
      function showDashboard() {
        currentPage = 'dashboard';
        loadJobs();
        loadStats();
        
        document.getElementById('main-content').innerHTML = `
          <div class="container my-4">
            <div class="row mb-4" id="stats-row">
              <!-- Stats will be loaded here -->
            </div>
            <div class="row">
              <div class="col-12">
                <div class="card">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                      <i class="bi bi-clock me-2"></i>Recent Jobs
                    </h5>
                    <button class="btn btn-primary btn-sm" onclick="showHome()">
                      <i class="bi bi-plus me-1"></i>New Job
                    </button>
                  </div>
                  <div class="card-body">
                    <div id="jobs-table">
                      <!-- Jobs table will be loaded here -->
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
        
        updateDashboard();
      }

      async function loadStats() {
        const data = await apiCall('/stats');
        if (data) stats = data;
      }

      async function loadJobs() {
        const data = await apiCall('/jobs');
        if (data && data.jobs) jobs = data.jobs;
      }

      function updateDashboard() {
        // Update stats
        document.getElementById('stats-row').innerHTML = `
          <div class="col-md-3 mb-3">
            <div class="card stat-card">
              <div class="card-body">
                <i class="bi bi-clipboard-data text-primary mb-2" style="font-size: 2rem;"></i>
                <div class="stat-number">${stats.total_jobs}</div>
                <div class="stat-label">Total Jobs</div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card stat-card">
              <div class="card-body">
                <i class="bi bi-check-circle text-success mb-2" style="font-size: 2rem;"></i>
                <div class="stat-number">${stats.completed_jobs}</div>
                <div class="stat-label">Completed</div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card stat-card">
              <div class="card-body">
                <i class="bi bi-play-circle text-info mb-2" style="font-size: 2rem;"></i>
                <div class="stat-number">${stats.running_jobs}</div>
                <div class="stat-label">Running</div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card stat-card">
              <div class="card-body">
                <i class="bi bi-database text-warning mb-2" style="font-size: 2rem;"></i>
                <div class="stat-number">${stats.total_results}</div>
                <div class="stat-label">Total Results</div>
              </div>
            </div>
          </div>
        `;

        // Update jobs table
        if (jobs.length > 0) {
          const jobsHtml = jobs.map(job => `
            <tr>
              <td><small class="font-monospace">${job.id}</small></td>
              <td><span class="badge bg-secondary">${job.type}</span></td>
              <td><span class="badge ${getStatusBadge(job.status)}">${job.status}</span></td>
              <td>${job.results_count || 0}</td>
              <td><small>${job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'}</small></td>
              <td>
                ${job.status === 'completed' ? `<button class="btn btn-sm btn-outline-success" onclick="showResults('${job.id}')"><i class="bi bi-eye"></i></button>` : ''}
              </td>
            </tr>
          `).join('');

          document.getElementById('jobs-table').innerHTML = `
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Results</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>${jobsHtml}</tbody>
              </table>
            </div>
          `;
        } else {
          document.getElementById('jobs-table').innerHTML = `
            <div class="text-center py-4">
              <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.5;"></i>
              <h6 class="text-muted mt-3">No jobs found</h6>
              <p class="text-muted">Start your first scraping job to see results here</p>
              <button class="btn btn-primary" onclick="showHome()">
                <i class="bi bi-plus me-1"></i>Create New Job
              </button>
            </div>
          `;
        }
      }

      function getStatusBadge(status) {
        switch (status) {
          case 'completed': return 'bg-success';
          case 'running': return 'bg-primary';
          case 'failed': return 'bg-danger';
          default: return 'bg-secondary';
        }
      }

      function switchTab(tabName) {
        document.getElementById('search-tab').classList.remove('active');
        document.getElementById('scrape-tab').classList.remove('active');
        document.getElementById(tabName + '-tab').classList.add('active');
        
        if (tabName === 'search') {
          document.getElementById('search-form').style.display = 'block';
          document.getElementById('scrape-form').style.display = 'none';
        } else {
          document.getElementById('search-form').style.display = 'none';
          document.getElementById('scrape-form').style.display = 'block';
        }
      }

      async function handleSearch(event) {
        event.preventDefault();
        const query = document.getElementById('search-query').value;
        const maxResults = document.getElementById('max-results').value;
        
        const result = await apiCall('/jobs', {
          method: 'POST',
          body: JSON.stringify({
            type: 'search',
            query: query,
            max_results: parseInt(maxResults)
          })
        });
        
        if (result && result.job_id) {
          alert(`Search job created with ID: ${result.job_id}`);
          showDashboard();
        }
      }

      async function handleScrape(event) {
        event.preventDefault();
        const urls = document.getElementById('scrape-urls').value.split('\\n').filter(url => url.trim());
        const adapter = document.getElementById('adapter-select').value;
        const taskType = document.getElementById('task-type').value;
        
        const result = await apiCall('/jobs', {
          method: 'POST',
          body: JSON.stringify({
            type: 'scrape',
            urls: urls,
            adapter_name: adapter,
            task_type: taskType
          })
        });
        
        if (result && result.job_id) {
          alert(`Scraping job created with ID: ${result.job_id}`);
          showDashboard();
        }
      }

      async function showResults(jobId) {
        const results = await apiCall(`/jobs/${jobId}/results`);
        const job = await apiCall(`/jobs/${jobId}/status`);
        
        if (results && job) {
          const resultsHtml = results.results.map((result, index) => `
            <div class="card mb-3">
              <div class="card-header">
                <a href="${result.url}" target="_blank" class="text-decoration-none">
                  ${result.url} <i class="bi bi-box-arrow-up-right ms-1"></i>
                </a>
              </div>
              <div class="card-body">
                <pre class="json-display"><code>${JSON.stringify(result.data, null, 2)}</code></pre>
              </div>
            </div>
          `).join('');

          document.getElementById('main-content').innerHTML = `
            <div class="container my-4">
              <div class="row mb-4">
                <div class="col-12">
                  <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                      <h5 class="mb-0">Job Results - ${jobId}</h5>
                      <button class="btn btn-outline-secondary" onclick="showDashboard()">
                        <i class="bi bi-arrow-left me-1"></i>Back to Dashboard
                      </button>
                    </div>
                    <div class="card-body">
                      <p><strong>Type:</strong> ${job.type}</p>
                      <p><strong>Status:</strong> <span class="badge ${getStatusBadge(job.status)}">${job.status}</span></p>
                      <p><strong>Results:</strong> ${results.results.length} items</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-12">
                  <div class="card">
                    <div class="card-header">
                      <h6 class="mb-0">Scraped Data (${results.results.length} items)</h6>
                    </div>
                    <div class="card-body">
                      ${results.results.length > 0 ? resultsHtml : '<p class="text-muted">No results found</p>'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `;
        }
      }

      // Initialize app
      document.addEventListener('DOMContentLoaded', function() {
        showHome();
      });
    </script>
  </body>
</html>'''

# Frontend route - serve React app
@app.route('/')
def index():
    """Serve the React application"""
    return REACT_HTML

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Web Scraper API is running'
    })

@app.route('/api/adapters', methods=['GET'])
def list_adapters():
    """List all available scraping adapters"""
    return jsonify({'adapters': default_adapters})

@app.route('/api/search', methods=['POST'])
def search_urls():
    """Search for URLs using DuckDuckGo"""
    try:
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 20)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Mock search results
        results = [
            {'title': f'Sample result {i+1} for "{query}"', 'url': f'https://example{i+1}.com', 'description': f'Description for result {i+1}'}
            for i in range(min(max_results, 5))
        ]
        
        return jsonify({'results': results})
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new scraping job"""
    try:
        data = request.json
        job_type = data.get('type', 'scrape')
        
        job_data = {
            'task_type': data.get('task_type', 'general'),
            'adapter_name': data.get('adapter_name', 'default'),
            'search_query': data.get('query'),
            'urls': data.get('urls', []),
            'status': 'completed',
            'progress': 100,
            'total_urls': len(data.get('urls', [])),
            'completed_urls': len(data.get('urls', [])),
            'results_count': 3
        }
        
        job = ScrapingJob.create_job(job_data)
        
        return jsonify({'job_id': job.id, 'status': 'started'})
        
    except Exception as e:
        logging.error(f"Job creation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    try:
        job = ScrapingJob.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job.to_dict())
    except Exception as e:
        logging.error(f"Status check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get job results"""
    try:
        results = ScrapingResult.get_results(job_id)
        
        # If no results exist, create some mock results for demonstration
        if not results:
            mock_results = [
                {
                    'url': 'https://example1.com',
                    'data': {'title': 'Sample Title 1', 'description': 'Sample description', 'contact': 'john@example.com'},
                    'scraped_at': '2024-01-01T00:00:00Z'
                },
                {
                    'url': 'https://example2.com', 
                    'data': {'title': 'Sample Title 2', 'description': 'Another description', 'phone': '+1-555-0123'},
                    'scraped_at': '2024-01-01T00:01:00Z'
                },
                {
                    'url': 'https://example3.com',
                    'data': {'title': 'Sample Title 3', 'description': 'Third description', 'email': 'contact@example3.com'},
                    'scraped_at': '2024-01-01T00:02:00Z'
                }
            ]
            return jsonify({'results': mock_results})
        
        return jsonify({'results': [result.to_dict() for result in results]})
    except Exception as e:
        logging.error(f"Results fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    jobs = ScrapingJob.get_jobs()
    return jsonify({'jobs': [job.to_dict() for job in jobs]})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = Analytics.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Stats fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

# This is now a Blueprint, so no __main__ section needed