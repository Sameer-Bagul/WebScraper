import { useState, useEffect } from 'react'
import { scraperAPI } from '../services/api'

function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    job_type: 'jobs',
    query: '',
    max_results: 100
  })

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
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (formData.job_type === 'jobs') {
        await scraperAPI.scrapeJobs(formData)
      } else {
        await scraperAPI.scrapeLeads(formData)
      }
      
      alert(`Scraping started for "${formData.query}"`)
      setFormData({ ...formData, query: '' })
      loadData()
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || error.message))
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

  return (
    <div>
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h5><i className="bi bi-play-circle"></i> Start New Scraping Job</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Job Type</label>
                      <select 
                        className="form-select"
                        value={formData.job_type}
                        onChange={(e) => setFormData({...formData, job_type: e.target.value})}
                      >
                        <option value="jobs">Job Hunting</option>
                        <option value="leads">Lead Generation</option>
                      </select>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Max Results</label>
                      <input 
                        type="number" 
                        className="form-control"
                        value={formData.max_results}
                        onChange={(e) => setFormData({...formData, max_results: parseInt(e.target.value)})}
                        min="1" 
                        max="1000"
                      />
                    </div>
                  </div>
                </div>
                <div className="mb-3">
                  <label className="form-label">Search Query</label>
                  <input 
                    type="text" 
                    className="form-control"
                    value={formData.query}
                    onChange={(e) => setFormData({...formData, query: e.target.value})}
                    placeholder="e.g., Python Developer, Digital Marketing Agency"
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Starting...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-search"></i> Start Scraping
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5><i className="bi bi-bar-chart"></i> Quick Stats</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Total Jobs:</strong> {stats.total_jobs || 0}
              </div>
              <div className="mb-3">
                <strong>Completed:</strong> {stats.completed_jobs || 0}
              </div>
              <div className="mb-3">
                <strong>Total Results:</strong> {stats.total_results || 0}
              </div>
              <div className="mb-3">
                <strong>Success Rate:</strong> {Math.round(stats.success_rate || 0)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5><i className="bi bi-list"></i> Recent Jobs</h5>
            </div>
            <div className="card-body">
              {jobs.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-dark table-striped">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Query</th>
                        <th>Status</th>
                        <th>Results</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.slice(0, 10).map((job, index) => (
                        <tr key={index}>
                          <td>
                            <span className={`badge ${job.job_type === 'jobs' ? 'bg-success' : 'bg-info'}`}>
                              {job.job_type === 'jobs' ? 'Jobs' : 'Leads'}
                            </span>
                          </td>
                          <td>{job.query}</td>
                          <td>
                            <span className={`badge ${getStatusBadgeClass(job.status)}`}>
                              {job.status}
                            </span>
                          </td>
                          <td>{job.results_count}</td>
                          <td>{job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'}</td>
                          <td>
                            <a href={`/results/${job._id || index}`} className="btn btn-sm btn-outline-primary">
                              <i className="bi bi-eye"></i> View
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted">No scraping jobs yet. Start your first job above!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard