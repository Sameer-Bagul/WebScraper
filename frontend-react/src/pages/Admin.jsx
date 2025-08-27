import { useState, useEffect } from 'react'
import { scraperAPI } from '../services/api'

function Admin() {
  const [jobs, setJobs] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [jobsRes, statsRes] = await Promise.all([
        scraperAPI.getJobs(),
        scraperAPI.getStats()
      ])
      setJobs(jobsRes.data.jobs || [])
      setStats(statsRes.data.stats || {})
    } catch (error) {
      console.error('Error loading data:', error)
    }
    setLoading(false)
  }

  const clearAllData = async () => {
    if (!confirm('Are you sure you want to clear all scraping data? This cannot be undone.')) {
      return
    }

    try {
      await scraperAPI.clearData()
      alert('All data cleared successfully')
      loadData()
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || error.message))
    }
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
        <h2><i className="bi bi-gear"></i> Admin Dashboard</h2>
      </div>

      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <h3 className="text-primary">{stats.total_jobs || 0}</h3>
              <p>Total Jobs</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <h3 className="text-success">{stats.completed_jobs || 0}</h3>
              <p>Completed</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <h3 className="text-info">{stats.total_results || 0}</h3>
              <p>Total Results</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <h3 className="text-warning">{Math.round(stats.success_rate || 0)}%</h3>
              <p>Success Rate</p>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h5><i className="bi bi-activity"></i> Recent Activity</h5>
            </div>
            <div className="card-body">
              {jobs.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-dark table-sm">
                    <thead>
                      <tr>
                        <th>Job</th>
                        <th>Status</th>
                        <th>Results</th>
                        <th>Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.slice(0, 10).map((job, index) => (
                        <tr key={index}>
                          <td>{job.query}</td>
                          <td>
                            <span className={`badge ${
                              job.status === 'completed' ? 'bg-success' :
                              job.status === 'running' ? 'bg-warning text-dark' :
                              'bg-danger'
                            }`}>
                              {job.status}
                            </span>
                          </td>
                          <td>{job.results_count}</td>
                          <td>
                            {job.created_at ? 
                              new Date(job.created_at).toLocaleDateString() : 
                              'N/A'
                            }
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted">No jobs yet.</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5><i className="bi bi-tools"></i> Admin Actions</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-danger" onClick={clearAllData}>
                  <i className="bi bi-trash"></i> Clear All Data
                </button>
                <div className="card bg-dark mt-3">
                  <div className="card-header">
                    <h6><i className="bi bi-info-circle"></i> System Info</h6>
                  </div>
                  <div className="card-body">
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Database:</strong> MongoDB Atlas</p>
                    <p><strong>Status:</strong> <span className="badge bg-success">Online</span></p>
                    <p><strong>Environment:</strong> Development</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Admin