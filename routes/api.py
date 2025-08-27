from flask import Blueprint, jsonify, request, Response, current_app
from models import ScrapingJob, ScrapingResult, Analytics, DomainAdapter
import csv
import io
import json
import os
import logging

api_bp = Blueprint('api', __name__)

@api_bp.route('/job/<job_id>/status')
def get_job_status(job_id):
    """Get job status via API"""
    if not current_app.db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    scraping_job = ScrapingJob(current_app.db)
    job = scraping_job.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)

@api_bp.route('/job/<job_id>/results')
def get_job_results(job_id):
    """Get job results via API"""
    if not current_app.db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    scraping_result = ScrapingResult(current_app.db)
    results = scraping_result.get_results(job_id)
    return jsonify({'results': results})

@api_bp.route('/job/<job_id>/export/<format>')
def export_job_results(job_id, format):
    """Export job results in CSV or JSON format"""
    if not current_app.db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    scraping_result = ScrapingResult(current_app.db)
    results_data = scraping_result.get_results(job_id)
    
    if format.lower() == 'csv':
        # Create CSV export
        output = io.StringIO()
        
        if results_data:
            # Get all unique keys from results
            all_keys = set()
            for result in results_data:
                data = result.get('data', {})
                if isinstance(data, dict):
                    all_keys.update(data.keys())
            
            all_keys = ['url'] + sorted(list(all_keys))
            
            writer = csv.DictWriter(output, fieldnames=all_keys)
            writer.writeheader()
            
            for result in results_data:
                row = {'url': result.get('url', '')}
                data = result.get('data', {})
                if isinstance(data, dict):
                    for key in all_keys[1:]:  # Skip 'url'
                        value = data.get(key, '')
                        # Convert lists and dicts to string
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value)
                        row[key] = str(value)
                writer.writerow(row)
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=job_{job_id}_results.csv'}
        )
    
    elif format.lower() == 'json':
        # JSON export
        return Response(
            json.dumps({'job_id': job_id, 'results': results_data}, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=job_{job_id}_results.json'}
        )
    
    else:
        return jsonify({'error': 'Unsupported format. Use csv or json'}), 400

@api_bp.route('/adapters')
def list_adapters():
    """List all available adapters"""
    if not current_app.db:
        # Return default adapters if no database connection
        default_adapters = [
            {"name": "default", "display_name": "Default General Scraper", "description": "General purpose scraper for any website"},
            {"name": "indeed", "display_name": "Indeed Job Board", "description": "Scraper for Indeed job listings"},
            {"name": "linkedin", "display_name": "LinkedIn Jobs", "description": "Scraper for LinkedIn job listings"},
            {"name": "business_directory", "display_name": "Business Directory", "description": "Scraper for business directories"}
        ]
        return jsonify({'adapters': default_adapters})
    
    domain_adapter = DomainAdapter(current_app.db)
    adapters = domain_adapter.get_adapters()
    
    # Add default adapters if none exist in database
    if not adapters:
        default_adapters = [
            {"name": "default", "display_name": "Default General Scraper", "description": "General purpose scraper for any website"},
            {"name": "indeed", "display_name": "Indeed Job Board", "description": "Scraper for Indeed job listings"},
            {"name": "linkedin", "display_name": "LinkedIn Jobs", "description": "Scraper for LinkedIn job listings"},
            {"name": "business_directory", "display_name": "Business Directory", "description": "Scraper for business directories"}
        ]
        return jsonify({'adapters': default_adapters})
    
    return jsonify({'adapters': adapters})

@api_bp.route('/adapter/<name>')
def get_adapter(name):
    """Get specific adapter configuration"""
    if not current_app.db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    domain_adapter = DomainAdapter(current_app.db)
    adapter = domain_adapter.get_adapter(name)
    
    if not adapter:
        return jsonify({'error': 'Adapter not found'}), 404
    
    return jsonify(adapter)

@api_bp.route('/search', methods=['POST'])
def search_urls():
    """Search for URLs using DuckDuckGo"""
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 20)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'description': result.get('body', '')
                })
        
        return jsonify({'results': results})
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs', methods=['POST'])
def create_job():
    """Create a new scraping job"""
    try:
        data = request.json
        job_type = data.get('type', 'scrape')
        
        job_data = {
            'task_type': data.get('task_type', 'general'),
            'adapter_name': data.get('adapter_name', 'default'),
            'search_query': data.get('query'),
            'urls': data.get('urls', [])
        }
        
        # Set initial status as completed for demo
        job_data['status'] = 'completed'
        job_data['progress'] = 100
        job_data['total_urls'] = len(job_data.get('urls', []))
        job_data['completed_urls'] = job_data['total_urls']
        job_data['results_count'] = 3
        
        if current_app.db:
            # Use MongoDB if available
            scraping_job = ScrapingJob(current_app.db)
            job_id = scraping_job.create_job(job_data)
        else:
            # Use mock job ID for fallback
            import uuid
            job_id = str(uuid.uuid4())
            logging.info(f"Created fallback job with ID: {job_id}")
        
        return jsonify({'job_id': job_id, 'status': 'started'})
        
    except Exception as e:
        logging.error(f"Job creation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    if not current_app.db:
        return jsonify({'jobs': []})
    
    scraping_job = ScrapingJob(current_app.db)
    jobs = scraping_job.get_jobs()
    return jsonify({'jobs': jobs})

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        if not current_app.db:
            return jsonify({
                'total_jobs': 0,
                'completed_jobs': 0,
                'failed_jobs': 0,
                'running_jobs': 0,
                'total_results': 0,
                'recent_jobs': []
            })
        
        analytics = Analytics(current_app.db)
        stats = analytics.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Stats fetch failed: {e}")
        return jsonify({'error': str(e)}), 500
    
    try:
        results = scraper.search_duckduckgo(query, max_results)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/job/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running job"""
    from app import db
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    task_manager = TaskManager(db)
    success = task_manager.cancel_task(job_id)
    
    if success:
        return jsonify({'message': 'Job cancellation requested'})
    else:
        return jsonify({'error': 'Job not found or not running'}), 404
