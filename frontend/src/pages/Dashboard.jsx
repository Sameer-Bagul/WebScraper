import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [statsResponse, jobsResponse] = await Promise.all([
        axios.get('http://localhost:5000/api/stats'),
        axios.get('http://localhost:5000/api/jobs')
      ])
      
      setStats(statsResponse.data)
      setJobs(jobsResponse.data.jobs)
    } catch (error) {
      console.error('Failed to fetch data:', error)
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

  return (
    <div className="container my-4">
      {/* Statistics Dashboard */}
      {stats && (
        <div className="row mb-4">
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body">
                <i className="bi bi-clipboard-data text-primary mb-2" style={{fontSize: '2rem'}}></i>
                <div className="stat-number">{stats.total_jobs}</div>
                <div className="stat-label">Total Jobs</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body">
                <i className="bi bi-check-circle text-success mb-2" style={{fontSize: '2rem'}}></i>
                <div className="stat-number">{stats.completed_jobs}</div>
                <div className="stat-label">Completed</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body">
                <i className="bi bi-play-circle text-info mb-2" style={{fontSize: '2rem'}}></i>
                <div className="stat-number">{stats.running_jobs}</div>
                <div className="stat-label">Running</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body">
                <i className="bi bi-database text-warning mb-2" style={{fontSize: '2rem'}}></i>
                <div className="stat-number">{stats.total_results}</div>
                <div className="stat-label">Total Results</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Jobs */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <i className="bi bi-clock me-2"></i>
                Recent Jobs
              </h5>
              <Link to="/" className="btn btn-primary btn-sm">
                <i className="bi bi-plus me-1"></i>
                New Job
              </Link>
            </div>
            <div className="card-body">
              {jobs.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover results-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Progress</th>
                        <th>Results</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.map(job => (
                        <tr key={job.id}>
                          <td>
                            <small className="font-monospace">{job.id}</small>
                          </td>
                          <td>
                            <span className="badge bg-secondary">{job.type}</span>
                            {job.task_type && (
                              <><br/><small className="text-muted">{job.task_type}</small></>
                            )}
                          </td>
                          <td>
                            <span className={`badge ${getStatusBadgeClass(job.status)}`}>
                              {job.status}
                            </span>
                          </td>
                          <td>
                            <div className="progress" style={{height: '10px'}}>
                              <div 
                                className="progress-bar" 
                                style={{width: `${job.progress || 0}%`}}
                              ></div>
                            </div>
                            <small className="text-muted">{job.progress || 0}%</small>
                          </td>
                          <td>
                            <span className="text-success fw-bold">{job.results_count || 0}</span>
                          </td>
                          <td>
                            <small>{job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'}</small>
                          </td>
                          <td>
                            {job.status === 'completed' && (
                              <Link 
                                to={`/results/${job.id}`} 
                                className="btn btn-sm btn-outline-success" 
                                title="View Results"
                              >
                                <i className="bi bi-eye"></i>
                              </Link>
                            )}
                            {job.status === 'running' && (
                              <button 
                                className="btn btn-sm btn-outline-primary" 
                                title="Refreshing..."
                              >
                                <i className="bi bi-arrow-clockwise"></i>
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="bi bi-inbox" style={{fontSize: '3rem', opacity: 0.5}}></i>
                  <h6 className="text-muted mt-3">No jobs found</h6>
                  <p className="text-muted">Start your first scraping job to see results here</p>
                  <Link to="/" className="btn btn-primary">
                    <i className="bi bi-plus me-1"></i>
                    Create New Job
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard