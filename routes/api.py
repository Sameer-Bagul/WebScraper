from flask import Blueprint, jsonify, request, Response, current_app
from models import ScrapingJob, ScrapingResult, Analytics, DomainAdapter
from typing import Dict
import csv
import io
import json
import os
import logging

api_bp = Blueprint('api', __name__)

@api_bp.route('/scrape/jobs', methods=['POST'])
def start_job_scraping():
    """Start real-time job scraping"""
    try:
        data = request.json
        search_query = data.get('search_query', 'python developer')
        location = data.get('location', 'remote')
        max_results = data.get('max_results', 10)
        
        # Import here to avoid circular imports
        from real_time_scraper import RealTimeScraper
        scraper = RealTimeScraper(current_app.db)
        
        job_data = {
            'search_query': search_query,
            'location': location,
            'max_results': max_results,
            'urls': [],
            'total_urls': max_results
        }
        
        job_id = scraper.start_real_time_job_scraping(job_data)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Job scraping started for "{search_query}" in {location}',
            'status': 'running'
        })
        
    except Exception as e:
        logging.error(f"Job scraping failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/scrape/leads', methods=['POST'])
def start_lead_scraping():
    """Start real-time lead generation"""
    try:
        data = request.json
        target_domain = data.get('target_domain')
        industry = data.get('industry', 'technology')
        max_results = data.get('max_results', 20)
        
        if not target_domain:
            return jsonify({'success': False, 'error': 'target_domain is required'}), 400
        
        from real_time_scraper import RealTimeScraper
        scraper = RealTimeScraper(current_app.db)
        
        job_data = {
            'target_domain': target_domain,
            'industry': industry,
            'max_results': max_results,
            'urls': [target_domain],
            'total_urls': max_results
        }
        
        job_id = scraper.start_real_time_lead_scraping(job_data)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Lead generation started for {target_domain}',
            'status': 'running'
        })
        
    except Exception as e:
        logging.error(f"Lead scraping failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics/dashboard')
def get_dashboard_analytics():
    """Get dashboard analytics"""
    try:
        from models import Analytics
        analytics = Analytics(current_app.db)
        stats = analytics.get_dashboard_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logging.error(f"Analytics failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
    """Create a new real-time scraping job"""
    try:
        from real_time_scraper import RealTimeScraper
        
        data = request.json
        task_type = data.get('task_type', 'general')
        
        job_data = {
            'task_type': task_type,
            'adapter_name': data.get('adapter_name', 'default'),
            'search_query': data.get('query'),
            'urls': data.get('urls', []),
            'max_results': data.get('max_results', 50)
        }
        
        if current_app.db:
            # Start real-time scraping
            rt_scraper = RealTimeScraper(current_app.db)
            
            if task_type == 'job_scraping':
                job_id = rt_scraper.start_real_time_job_scraping(job_data)
            elif task_type == 'lead_generation':
                job_id = rt_scraper.start_real_time_lead_scraping(job_data)
            else:
                # Generic scraping
                scraping_job = ScrapingJob(current_app.db)
                job_id = scraping_job.create_job({**job_data, 'status': 'pending'})
                
                # Start generic scraping in background
                import threading
                threading.Thread(
                    target=_run_generic_scraping,
                    args=(job_id, job_data, current_app.db)
                ).start()
        else:
            # Fallback mock
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
    
def _run_generic_scraping(job_id: str, job_data: Dict, db):
    """Run generic scraping in background thread"""
    from scraper_engine import ScraperEngine, BatchScraper
    
    try:
        scraping_job_model = ScrapingJob(db)
        scraping_result_model = ScrapingResult(db)
        
        scraper = ScraperEngine()
        batch_scraper = BatchScraper(scraper)
        
        # Update job status
        scraping_job_model.update_job(job_id, {'status': 'running'})
        
        urls = job_data.get('urls', [])
        if not urls:
            # Search for URLs if none provided
            query = job_data.get('search_query', '')
            if query:
                search_results = scraper.search_duckduckgo(query, 10)
                urls = [r['url'] for r in search_results]
                scraping_job_model.update_job(job_id, {'urls': urls, 'total_urls': len(urls)})
        
        if urls:
            # Load adapter config
            adapter_name = job_data.get('adapter_name', 'default')
            adapter_config = _load_adapter_config(adapter_name)
            
            # Progress callback
            def progress_callback(progress, completed, results_count):
                scraping_job_model.update_job(job_id, {
                    'progress': int(progress),
                    'completed_urls': completed,
                    'results_count': results_count
                })
            
            # Scrape URLs
            results = batch_scraper.scrape_urls(urls, adapter_config, progress_callback)
            
            # Save results
            for result in results:
                if 'error' not in result:
                    scraping_result_model.save_result(job_id, result.get('url', ''), result, 'general')
            
            # Mark as completed
            scraping_job_model.update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'results_count': len([r for r in results if 'error' not in r])
            })
        else:
            scraping_job_model.update_job(job_id, {
                'status': 'failed',
                'error_message': 'No URLs found to scrape'
            })
            
    except Exception as e:
        logging.error(f"Generic scraping failed: {e}")
        scraping_job_model.update_job(job_id, {
            'status': 'failed',
            'error_message': str(e)
        })

def _load_adapter_config(adapter_name: str) -> Dict:
    """Load adapter configuration"""
    adapter_configs = {
        'default': {
            'selectors': {
                'title': {'selector': 'h1, title', 'attribute': 'text'},
                'content': {'selector': 'p', 'attribute': 'text', 'multiple': True}
            },
            'extract_links': True,
            'extract_text': True
        },
        'indeed': {
            'selectors': {
                'job_title': {'selector': '.jobsearch-JobInfoHeader-title', 'attribute': 'text'},
                'company': {'selector': '.icl-u-lg-mr--sm', 'attribute': 'text'},
                'location': {'selector': '.jobsearch-JobInfoHeader-subtitle', 'attribute': 'text'},
                'description': {'selector': '#jobDescriptionText', 'attribute': 'text'}
            }
        },
        'linkedin': {
            'selectors': {
                'job_title': {'selector': '.job-details-jobs-unified-top-card__job-title', 'attribute': 'text'},
                'company': {'selector': '.job-details-jobs-unified-top-card__company-name', 'attribute': 'text'},
                'location': {'selector': '.job-details-jobs-unified-top-card__bullet', 'attribute': 'text'}
            }
        }
    }
    
    return adapter_configs.get(adapter_name, adapter_configs['default'])

@api_bp.route('/job/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running job"""
    if not current_app.db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        scraping_job = ScrapingJob(current_app.db)
        scraping_job.update_job(job_id, {'status': 'cancelled'})
        return jsonify({'message': 'Job cancellation requested'})
    except Exception as e:
        logging.error(f"Job cancellation failed: {e}")
        return jsonify({'error': str(e)}), 404
