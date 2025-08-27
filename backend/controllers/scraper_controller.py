from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from backend.services.scraper_service import ScraperService
from backend.models.scraper_model import ScraperJob, ScraperResult

scraper_bp = Blueprint('scraper', __name__)
scraper_service = ScraperService()

@scraper_bp.route('/')
def index():
    """Main dashboard"""
    jobs = ScraperJob.find_all()
    return render_template('index.html', jobs=jobs)

@scraper_bp.route('/jobs')
def jobs():
    """Jobs page"""
    jobs = ScraperJob.find_all()
    return render_template('jobs.html', jobs=jobs)

@scraper_bp.route('/results/<job_id>')
def results(job_id):
    """Results page"""
    job = ScraperJob.find_by_id(job_id)
    results = ScraperResult.find_by_job_id(job_id) if job else []
    return render_template('results.html', job=job, results=results)

@scraper_bp.route('/start-scraping', methods=['POST'])
def start_scraping():
    """Start scraping job"""
    try:
        job_type = request.form.get('job_type', 'jobs')
        query = request.form.get('query', '')
        max_results = int(request.form.get('max_results', 100))
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Start scraping in background (simplified for demo)
        if job_type == 'jobs':
            results = scraper_service.scrape_jobs(query, max_results)
        else:
            results = scraper_service.scrape_leads(query, max_results)
        
        return jsonify({
            'success': True,
            'message': f'Scraping started for "{query}"',
            'results_count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500