import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Home() {
  const [activeTab, setActiveTab] = useState('search')
  const [adapters, setAdapters] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchForm, setSearchForm] = useState({
    query: '',
    maxResults: 20
  })
  const [scrapeForm, setScrapeForm] = useState({
    urls: '',
    adapter: 'default',
    taskType: 'general'
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchAdapters()
  }, [])

  const fetchAdapters = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/adapters')
      setAdapters(response.data.adapters)
    } catch (error) {
      console.error('Failed to fetch adapters:', error)
    }
  }

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post('http://localhost:5000/api/jobs', {
        type: 'search',
        query: searchForm.query,
        max_results: searchForm.maxResults
      })
      
      navigate(`/results/${response.data.job_id}`)
    } catch (error) {
      console.error('Search failed:', error)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleScrapeSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const urls = scrapeForm.urls.split('\\n').filter(url => url.trim())
      
      const response = await axios.post('http://localhost:5000/api/jobs', {
        type: 'scrape',
        urls: urls,
        adapter_name: scrapeForm.adapter,
        task_type: scrapeForm.taskType
      })
      
      navigate(`/results/${response.data.job_id}`)
    } catch (error) {
      console.error('Scraping failed:', error)
      alert('Scraping failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container my-5">
      {/* Hero Section */}
      <div className="hero-section">
        <h1 className="display-4 mb-3">
          <i className="bi bi-globe me-3"></i>
          Web Scraper Pro
        </h1>
        <p className="lead">Professional web scraping tool for job hunting and lead generation</p>
        <p className="text-muted">Extract structured data from any website with powerful scraping engines and intelligent contact extraction</p>
      </div>

      {/* Main Form */}
      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div className="card">
            <div className="card-header">
              <ul className="nav nav-tabs card-header-tabs">
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'search' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('search')}
                  >
                    <i className="bi bi-search me-1"></i>
                    Search URLs
                  </button>
                </li>
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'scrape' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('scrape')}
                  >
                    <i className="bi bi-download me-1"></i>
                    Direct Scraping
                  </button>
                </li>
              </ul>
            </div>
            <div className="card-body">
              {activeTab === 'search' ? (
                <form onSubmit={handleSearchSubmit}>
                  <div className="mb-3">
                    <label htmlFor="query" className="form-label">
                      <i className="bi bi-search me-1"></i>
                      Search Query
                    </label>
                    <input 
                      type="text" 
                      className="form-control" 
                      id="query" 
                      value={searchForm.query}
                      onChange={(e) => setSearchForm({...searchForm, query: e.target.value})}
                      placeholder="e.g., Python developer jobs in Berlin, or business directories" 
                      required 
                    />
                    <div className="form-text">Use specific keywords to find relevant URLs for scraping</div>
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="maxResults" className="form-label">
                      <i className="bi bi-hash me-1"></i>
                      Maximum Results
                    </label>
                    <select 
                      className="form-select" 
                      id="maxResults" 
                      value={searchForm.maxResults}
                      onChange={(e) => setSearchForm({...searchForm, maxResults: parseInt(e.target.value)})}
                    >
                      <option value={10}>10 results</option>
                      <option value={20}>20 results</option>
                      <option value={50}>50 results</option>
                      <option value={100}>100 results</option>
                    </select>
                  </div>
                  
                  <div className="d-grid">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Searching...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-search me-2"></i>
                          Search for URLs
                        </>
                      )}
                    </button>
                  </div>
                </form>
              ) : (
                <form onSubmit={handleScrapeSubmit}>
                  <div className="mb-3">
                    <label htmlFor="urls" className="form-label">
                      <i className="bi bi-link me-1"></i>
                      URLs to Scrape
                    </label>
                    <textarea 
                      className="form-control url-input" 
                      id="urls" 
                      rows="6"
                      value={scrapeForm.urls}
                      onChange={(e) => setScrapeForm({...scrapeForm, urls: e.target.value})}
                      placeholder="Enter URLs, one per line&#10;https://example.com/jobs&#10;https://another-site.com/listings" 
                      required
                    />
                    <div className="form-text">Enter one URL per line</div>
                  </div>
                  
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label htmlFor="adapter" className="form-label">
                        <i className="bi bi-gear me-1"></i>
                        Scraping Adapter
                      </label>
                      <select 
                        className="form-select" 
                        id="adapter"
                        value={scrapeForm.adapter}
                        onChange={(e) => setScrapeForm({...scrapeForm, adapter: e.target.value})}
                      >
                        {adapters.map(adapter => (
                          <option key={adapter.name} value={adapter.name} title={adapter.description}>
                            {adapter.display_name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-md-6">
                      <label htmlFor="taskType" className="form-label">
                        <i className="bi bi-target me-1"></i>
                        Task Type
                      </label>
                      <select 
                        className="form-select" 
                        id="taskType"
                        value={scrapeForm.taskType}
                        onChange={(e) => setScrapeForm({...scrapeForm, taskType: e.target.value})}
                      >
                        <option value="general">General Scraping</option>
                        <option value="job">Job Listings</option>
                        <option value="lead">Lead Generation</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="d-grid">
                    <button type="submit" className="btn btn-success" disabled={loading}>
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Starting...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-download me-2"></i>
                          Start Scraping
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Features</h3>
          <div className="row">
            <div className="col-md-4 mb-4">
              <div className="card feature-card">
                <div className="card-body">
                  <i className="bi bi-search feature-icon text-primary"></i>
                  <h5 className="card-title">Smart URL Discovery</h5>
                  <p className="card-text">Use search engines to automatically find relevant URLs for your scraping tasks</p>
                </div>
              </div>
            </div>
            <div className="col-md-4 mb-4">
              <div className="card feature-card">
                <div className="card-body">
                  <i className="bi bi-people feature-icon text-success"></i>
                  <h5 className="card-title">Contact Extraction</h5>
                  <p className="card-text">Automatically extract emails, phone numbers, and social profiles for lead generation</p>
                </div>
              </div>
            </div>
            <div className="col-md-4 mb-4">
              <div className="card feature-card">
                <div className="card-body">
                  <i className="bi bi-briefcase feature-icon text-info"></i>
                  <h5 className="card-title">Job Board Support</h5>
                  <p className="card-text">Built-in adapters for popular job boards like Indeed and LinkedIn</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home