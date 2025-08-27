import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { scraperAPI } from '../services/api'

function Results() {
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResults()
  }, [jobId])

  const loadResults = async () => {
    try {
      const response = await scraperAPI.getJobResults(jobId)
      setJob(response.data.job)
      setResults(response.data.results || [])
    } catch (error) {
      console.error('Error loading results:', error)
    }
    setLoading(false)
  }

  const exportResults = () => {
    if (results.length === 0) {
      alert('No results to export')
      return
    }

    let csv = 'Title,Company,Location,Email,Phone,URL,Description\n'
    results.forEach(result => {
      const row = [
        result.title || '',
        result.company || '',
        result.location || '',
        result.contact_info?.email || '',
        result.contact_info?.phone || '',
        result.url || '',
        (result.description || '').replace(/"/g, '""')
      ]
      csv += '"' + row.join('","') + '"\n'
    })

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scraping_results_${jobId}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed': return 'bg-success'
      case 'running': return 'bg-warning text-dark'
      case 'failed': return 'bg-danger'
      default: return 'bg-secondary'
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
        <div>
          <h2><i className="bi bi-list-check"></i> Scraping Results</h2>
          {job && (
            <p className="text-muted mb-0">
              Job: <strong>{job.query}</strong>{' '}
              <span className={`badge ${job.job_type === 'jobs' ? 'bg-success' : 'bg-info'}`}>
                {job.job_type === 'jobs' ? 'Jobs' : 'Leads'}
              </span>
            </p>
          )}
        </div>
        <div>
          <Link to="/jobs" className="btn btn-secondary">
            <i className="bi bi-arrow-left"></i> Back to Jobs
          </Link>
        </div>
      </div>

      {job && (
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card">
              <div className="card-body text-center">
                <h5 className="card-title">Status</h5>
                <span className={`badge ${getStatusBadgeClass(job.status)} fs-6`}>
                  {job.status}
                </span>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body text-center">
                <h5 className="card-title">Results Found</h5>
                <h3 className="text-primary">{results.length}</h3>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body text-center">
                <h5 className="card-title">Created</h5>
                <small>{job.created_at ? new Date(job.created_at).toLocaleString() : 'N/A'}</small>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body text-center">
                <h5 className="card-title">Updated</h5>
                <small>{job.updated_at ? new Date(job.updated_at).toLocaleString() : 'N/A'}</small>
              </div>
            </div>
          </div>
        </div>
      )}

      {results.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <div className="d-flex justify-content-between align-items-center">
              <h5><i className="bi bi-table"></i> Results ({results.length})</h5>
              <button className="btn btn-sm btn-outline-success" onClick={exportResults}>
                <i className="bi bi-download"></i> Export CSV
              </button>
            </div>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-dark table-striped">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Contact Info</th>
                    <th>Scraped</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr key={index}>
                      <td>
                        <strong>{result.title}</strong>
                        {result.description && (
                          <><br /><small className="text-muted">
                            {result.description.length > 100 
                              ? `${result.description.substring(0, 100)}...` 
                              : result.description}
                          </small></>
                        )}
                      </td>
                      <td>{result.company || 'N/A'}</td>
                      <td>{result.location || 'N/A'}</td>
                      <td>
                        {result.contact_info ? (
                          <div>
                            {result.contact_info.email && (
                              <div><i className="bi bi-envelope"></i> {result.contact_info.email}</div>
                            )}
                            {result.contact_info.phone && (
                              <div><i className="bi bi-telephone"></i> {result.contact_info.phone}</div>
                            )}
                            {result.contact_info.website && (
                              <div>
                                <i className="bi bi-globe"></i>{' '}
                                <a href={result.contact_info.website} target="_blank" rel="noopener noreferrer" className="text-info">
                                  Website
                                </a>
                              </div>
                            )}
                          </div>
                        ) : (
                          <small className="text-muted">No contact info</small>
                        )}
                      </td>
                      <td>{result.scraped_at ? new Date(result.scraped_at).toLocaleString() : 'N/A'}</td>
                      <td>
                        {result.url && (
                          <a href={result.url} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-outline-primary">
                            <i className="bi bi-box-arrow-up-right"></i> View
                          </a>
                        )}
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
            <h4 className="mt-3">No Results Found</h4>
            <p className="text-muted">
              {job && job.status === 'running' ? (
                'This job is still running. Check back in a few moments.'
              ) : job && job.status === 'failed' ? (
                'This job failed to complete. Please try running it again.'
              ) : (
                'No results were found for this job.'
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Results