import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'

function JobResults() {
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchJobData()
  }, [jobId])

  const fetchJobData = async () => {
    try {
      setLoading(true)
      const [jobResponse, resultsResponse] = await Promise.all([
        axios.get(`http://localhost:5000/api/jobs/${jobId}/status`),
        axios.get(`http://localhost:5000/api/jobs/${jobId}/results`)
      ])
      
      setJob(jobResponse.data)
      setResults(resultsResponse.data.results)
      setError(null)
    } catch (error) {
      console.error('Failed to fetch job data:', error)
      setError('Failed to load job data')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed': return 'bg-success'
      case 'running': return 'bg-primary'
      case 'failed': return 'bg-danger'
      default: return 'bg-secondary'
    }
  }

  if (loading) {
    return (
      <div className="container my-4">
        <div className="loading-spinner">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container my-4">
        <div className="alert alert-danger">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </div>
        <Link to="/dashboard" className="btn btn-primary">
          <i className="bi bi-arrow-left me-1"></i>
          Back to Dashboard
        </Link>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="container my-4">
        <div className="alert alert-warning">
          <i className="bi bi-exclamation-triangle me-2"></i>
          Job not found
        </div>
        <Link to="/dashboard" className="btn btn-primary">
          <i className="bi bi-arrow-left me-1"></i>
          Back to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="container my-4">
      {/* Job Information */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <i className="bi bi-file-text me-2"></i>
                Job Results
              </h5>
              <div>
                <Link to="/dashboard" className="btn btn-outline-secondary me-2">
                  <i className="bi bi-arrow-left me-1"></i>
                  Back to Dashboard
                </Link>
                {job.status === 'completed' && (
                  <button className="btn btn-outline-primary" onClick={() => window.print()}>
                    <i className="bi bi-printer me-1"></i>
                    Print
                  </button>
                )}
              </div>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <p><strong>Job ID:</strong> <span className="font-monospace">{job.id}</span></p>
                  <p><strong>Type:</strong> {job.type}
                    {job.task_type && ` (${job.task_type})`}
                  </p>
                  {job.type === 'search' && job.query && (
                    <p><strong>Query:</strong> {job.query}</p>
                  )}
                  {job.adapter_name && (
                    <p><strong>Adapter:</strong> {job.adapter_name}</p>
                  )}
                </div>
                <div className="col-md-6">
                  <p><strong>Status:</strong> 
                    <span className={`badge ${getStatusBadgeClass(job.status)} ms-2`}>
                      {job.status}
                    </span>
                  </p>
                  <p><strong>Results:</strong> {results.length} items</p>
                  <p><strong>Created:</strong> {job.created_at ? new Date(job.created_at).toLocaleString() : 'N/A'}</p>
                </div>
              </div>
              
              {job.status === 'running' && (
                <div className="mt-3">
                  <div className="progress mb-2">
                    <div 
                      className="progress-bar progress-bar-striped progress-bar-animated" 
                      style={{width: `${job.progress || 0}%`}}
                    >
                      {job.progress || 0}%
                    </div>
                  </div>
                  <button className="btn btn-primary btn-sm" onClick={fetchJobData}>
                    <i className="bi bi-arrow-clockwise me-1"></i>
                    Refresh Status
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="bi bi-list me-2"></i>
                Scraped Data ({results.length} items)
              </h6>
            </div>
            <div className="card-body">
              {results.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover results-table">
                    <thead>
                      <tr>
                        <th>URL</th>
                        <th>Data</th>
                        <th>Scraped At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result, index) => (
                        <tr key={index}>
                          <td>
                            <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-break">
                              {result.url.length > 50 ? `${result.url.substring(0, 50)}...` : result.url}
                              <i className="bi bi-box-arrow-up-right ms-1"></i>
                            </a>
                          </td>
                          <td>
                            <div className="accordion accordion-flush">
                              <div className="accordion-item">
                                <h2 className="accordion-header">
                                  <button 
                                    className="accordion-button collapsed" 
                                    type="button" 
                                    data-bs-toggle="collapse" 
                                    data-bs-target={`#collapse${index}`}
                                  >
                                    <i className="bi bi-chevron-down me-2"></i>
                                    View Scraped Data
                                  </button>
                                </h2>
                                <div 
                                  id={`collapse${index}`} 
                                  className="accordion-collapse collapse"
                                >
                                  <div className="accordion-body">
                                    <pre className="json-display">
                                      <code>{JSON.stringify(result.data, null, 2)}</code>
                                    </pre>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <small>{result.scraped_at ? new Date(result.scraped_at).toLocaleString() : 'N/A'}</small>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="bi bi-inbox" style={{fontSize: '3rem', opacity: 0.5}}></i>
                  <h6 className="text-muted mt-3">No results found</h6>
                  <p className="text-muted">The scraping job didn't return any data</p>
                  {job.status === 'running' && (
                    <p className="text-info">
                      <i className="bi bi-hourglass-split me-1"></i>
                      Job is still running. Results will appear here as they become available.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default JobResults