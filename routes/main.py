from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import ScrapingJob, ScrapingResult, Analytics
from tasks import TaskManager
from adapters import AdapterManager

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with job overview and statistics"""
    from app import db
    
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('main.index'))
    
    analytics = Analytics(db)
    stats = analytics.get_dashboard_stats()
    
    job_model = ScrapingJob(db)
    recent_jobs = job_model.get_jobs(limit=10)
    
    return render_template('dashboard.html', stats=stats, recent_jobs=recent_jobs)

@main_bp.route('/results/<job_id>')
def view_results(job_id):
    """View results for a specific job"""
    from app import db
    
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('main.dashboard'))
    
    job_model = ScrapingJob(db)
    result_model = ScrapingResult(db)
    
    job = job_model.get_job(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('main.dashboard'))
    
    results = result_model.get_results(job_id)
    
    return render_template('results.html', job=job, results=results)

@main_bp.route('/new_job', methods=['GET', 'POST'])
def new_job():
    """Create a new scraping job"""
    from app import db, app
    
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('main.index'))
    
    adapter_manager = AdapterManager()
    adapters = adapter_manager.list_adapters()
    
    if request.method == 'POST':
        job_type = request.form.get('job_type', 'scrape')
        
        if job_type == 'search':
            # DuckDuckGo search job
            query = request.form.get('query', '').strip()
            max_results = int(request.form.get('max_results', 20))
            
            if not query:
                flash('Search query is required', 'error')
                return render_template('index.html', adapters=adapters)
            
            # Create job
            job_model = ScrapingJob(db)
            job_id = job_model.create_job({
                'type': 'search',
                'query': query,
                'max_results': max_results
            })
            
            # Start search task
            task_manager = TaskManager(db)
            task_manager.start_search_task(job_id, query, max_results)
            
            flash('Search job started successfully', 'success')
            return redirect(url_for('main.job_status', job_id=job_id))
        
        else:
            # Scraping job
            urls_text = request.form.get('urls', '').strip()
            adapter_name = request.form.get('adapter', 'default')
            task_type = request.form.get('task_type', 'general')
            
            if not urls_text:
                flash('URLs are required', 'error')
                return render_template('index.html', adapters=adapters)
            
            # Parse URLs
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            if not urls:
                flash('No valid URLs provided', 'error')
                return render_template('index.html', adapters=adapters)
            
            # Create job
            job_model = ScrapingJob(db)
            job_id = job_model.create_job({
                'type': 'scrape',
                'urls': urls,
                'adapter_name': adapter_name,
                'task_type': task_type
            })
            
            # Start scraping task
            task_manager = TaskManager(db)
            task_manager.start_scraping_task(job_id, urls, adapter_name, task_type)
            
            flash('Scraping job started successfully', 'success')
            return redirect(url_for('main.job_status', job_id=job_id))
    
    return render_template('index.html', adapters=adapters)

@main_bp.route('/job/<job_id>/status')
def job_status(job_id):
    """Job status page with real-time updates"""
    from app import db
    
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('main.dashboard'))
    
    task_manager = TaskManager(db)
    job = task_manager.get_task_status(job_id)
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('dashboard.html', current_job=job)
