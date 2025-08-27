import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { scraperAPI } from '../services/api'

function Jobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await scraperAPI.getJobs()
      setJobs(response.data.jobs || [])
    } catch (error) {
      console.error('Error loading jobs:', error)
    }
    setLoading(false)
  }

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed': return 'bg-success'
      case 'running': return 'bg-warning text-dark'
      case 'failed': return 'bg-danger'
      default: return 'bg-secondary'
    }
  }

  const getTypeBadgeClass = (type) => {
    return type === 'jobs' ? 'bg-success' : 'bg-info'
  }

  if (loading) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2><i className="bi bi-briefcase"></i> Scraping Jobs</h2>
        <Link to="/" className="btn btn-primary">
          <i className="bi bi-plus"></i> New Job
        </Link>
      </div>

      {jobs.length > 0 ? (
        <div className="card">
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-dark table-striped">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Query</th>
                    <th>Status</th>
                    <th>Results</th>
                    <th>Max Results</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job, index) => (
                    <tr key={job._id || index}>
                      <td>
                        <span className={`badge ${getTypeBadgeClass(job.job_type)}`}>
                          {job.job_type === 'jobs' ? 'Jobs' : 'Leads'}
                        </span>
                      </td>
                      <td>{job.query}</td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass(job.status)}`}>
                          {job.status}
                        </span>
                      </td>
                      <td><strong>{job.results_count}</strong></td>
                      <td>{job.max_results}</td>
                      <td>
                        {job.created_at ? new Date(job.created_at).toLocaleString() : 'N/A'}
                      </td>
                      <td>
                        <div className="btn-group">
                          <Link 
                            to={`/results/${job._id || index}`} 
                            className="btn btn-sm btn-outline-primary"
                          >
                            <i className="bi bi-eye"></i> Results
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-body text-center">
            <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
            <h4 className="mt-3">No Jobs Yet</h4>
            <p className="text-muted">Start your first scraping job to see results here.</p>
            <Link to="/" className="btn btn-primary">
              <i className="bi bi-plus"></i> Create First Job
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default Jobs