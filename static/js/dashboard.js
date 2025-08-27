// Dashboard-specific JavaScript functionality
class DashboardManager {
    constructor() {
        this.refreshInterval = null;
        this.charts = {};
        this.initializePolling();
        this.setupEventListeners();
    }

    initializePolling() {
        // Auto-refresh for running jobs
        const runningJobs = document.querySelectorAll('[data-status="running"]');
        if (runningJobs.length > 0) {
            this.startPolling();
        }
    }

    startPolling(interval = 5000) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.refreshJobStatuses();
        }, interval);
    }

    stopPolling() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    refreshJobStatuses() {
        const runningJobElements = document.querySelectorAll('[data-job-id][data-status="running"]');
        
        if (runningJobElements.length === 0) {
            this.stopPolling();
            return;
        }

        runningJobElements.forEach(element => {
            const jobId = element.getAttribute('data-job-id');
            this.updateJobStatus(jobId);
        });
    }

    async updateJobStatus(jobId) {
        try {
            const response = await fetch(`/api/job/${jobId}/status`);
            const job = await response.json();
            
            if (job.error) {
                console.error('Error fetching job status:', job.error);
                return;
            }

            this.updateJobDisplay(job);
            
            // Stop polling if job is completed
            if (job.status !== 'running') {
                this.stopPolling();
                
                // Show completion notification
                if (job.status === 'completed') {
                    showNotification(`Job ${jobId.substring(0, 8)}... completed successfully!`, 'success');
                } else if (job.status === 'failed') {
                    showNotification(`Job ${jobId.substring(0, 8)}... failed.`, 'error');
                }
                
                // Refresh page after a short delay to show updated results
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to update job status:', error);
        }
    }

    updateJobDisplay(job) {
        // Update progress bar
        const progressBar = document.querySelector(`[data-job-id="${job._id}"] .progress-bar`);
        if (progressBar) {
            progressBar.style.width = `${job.progress || 0}%`;
            progressBar.textContent = `${job.progress || 0}%`;
        }

        // Update status badge
        const statusBadge = document.querySelector(`[data-job-id="${job._id}"] .status-badge`);
        if (statusBadge) {
            statusBadge.className = `badge bg-${this.getStatusColor(job.status)}`;
            statusBadge.textContent = job.status.charAt(0).toUpperCase() + job.status.slice(1);
        }

        // Update statistics
        const completedEl = document.querySelector(`[data-job-id="${job._id}"] .completed-count`);
        if (completedEl) {
            completedEl.textContent = job.completed_urls || 0;
        }

        const resultsEl = document.querySelector(`[data-job-id="${job._id}"] .results-count`);
        if (resultsEl) {
            resultsEl.textContent = job.results_count || 0;
        }

        const failedEl = document.querySelector(`[data-job-id="${job._id}"] .failed-count`);
        if (failedEl) {
            failedEl.textContent = job.failed_urls || 0;
        }

        // Update error message if present
        const errorEl = document.querySelector(`[data-job-id="${job._id}"] .error-message`);
        if (errorEl) {
            if (job.error_message) {
                errorEl.innerHTML = `
                    <div class="alert alert-danger">
                        <i data-feather="alert-circle" class="me-2"></i>
                        ${job.error_message}
                    </div>
                `;
                feather.replace();
            } else {
                errorEl.innerHTML = '';
            }
        }
    }

    getStatusColor(status) {
        const statusColors = {
            'pending': 'secondary',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'warning'
        };
        return statusColors[status] || 'secondary';
    }

    setupEventListeners() {
        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.export-btn, .export-btn *')) {
                const button = e.target.closest('.export-btn');
                const jobId = button.getAttribute('data-job-id');
                const format = button.getAttribute('data-format');
                this.exportResults(jobId, format, button);
            }
        });

        // Cancel job buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.cancel-job-btn, .cancel-job-btn *')) {
                const button = e.target.closest('.cancel-job-btn');
                const jobId = button.getAttribute('data-job-id');
                this.cancelJob(jobId);
            }
        });

        // Refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-btn, .refresh-btn *')) {
                this.refreshDashboard();
            }
        });
    }

    async exportResults(jobId, format, button) {
        try {
            setLoadingState(button, true);
            
            const response = await fetch(`/api/job/${jobId}/export/${format}`);
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `job_${jobId}_results.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification(`Results exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            console.error('Export failed:', error);
            showNotification(`Export failed: ${error.message}`, 'error');
        } finally {
            setLoadingState(button, false);
        }
    }

    async cancelJob(jobId) {
        if (!confirm('Are you sure you want to cancel this job?')) {
            return;
        }

        try {
            const response = await fetch(`/api/job/${jobId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                showNotification(result.message, 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification(result.error || 'Failed to cancel job', 'error');
            }
        } catch (error) {
            console.error('Cancel request failed:', error);
            showNotification('Failed to cancel job', 'error');
        }
    }

    refreshDashboard() {
        window.location.reload();
    }

    // Chart management
    createChart(canvasId, type, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        color: '#fff'
                    }
                }
            },
            scales: type !== 'doughnut' && type !== 'pie' ? {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            } : {}
        };

        const mergedOptions = this.deepMerge(defaultOptions, options);

        this.charts[canvasId] = new Chart(ctx, {
            type: type,
            data: data,
            options: mergedOptions
        });

        return this.charts[canvasId];
    }

    deepMerge(target, source) {
        const result = { ...target };
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = this.deepMerge(result[key] || {}, source[key]);
            } else {
                result[key] = source[key];
            }
        }
        return result;
    }
}

// Real-time updates for job statistics
class StatsManager {
    constructor() {
        this.updateInterval = null;
        this.setupRealTimeUpdates();
    }

    setupRealTimeUpdates() {
        // Update stats every 30 seconds if there are active jobs
        const hasActiveJobs = document.querySelector('[data-status="running"]');
        if (hasActiveJobs) {
            this.updateInterval = setInterval(() => {
                this.updateStats();
            }, 30000);
        }
    }

    async updateStats() {
        try {
            // This would require an API endpoint to get current stats
            // For now, we'll just update the timestamp
            this.updateLastRefresh();
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    updateLastRefresh() {
        const timestamp = new Date().toLocaleTimeString();
        const refreshElements = document.querySelectorAll('.last-refresh');
        refreshElements.forEach(el => {
            el.textContent = `Last updated: ${timestamp}`;
        });
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardManager = new DashboardManager();
    window.statsManager = new StatsManager();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (window.dashboardManager) {
            window.dashboardManager.stopPolling();
        }
        if (window.statsManager) {
            window.statsManager.destroy();
        }
    });
});

// Global dashboard functions
window.refreshStatus = function() {
    if (window.dashboardManager) {
        window.dashboardManager.refreshDashboard();
    }
};

window.cancelJob = function(jobId) {
    if (window.dashboardManager) {
        window.dashboardManager.cancelJob(jobId);
    }
};

// Job filtering functionality
window.filterJobs = function(status) {
    const rows = document.querySelectorAll('tbody tr[data-status]');
    const buttons = document.querySelectorAll('.filter-btn');
    
    // Update button states
    buttons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    const activeButton = document.querySelector(`[onclick="filterJobs('${status}')"]`);
    if (activeButton) {
        activeButton.classList.remove('btn-outline-primary');
        activeButton.classList.add('btn-primary');
    }
    
    // Filter rows
    rows.forEach(row => {
        const rowStatus = row.getAttribute('data-status');
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
};
