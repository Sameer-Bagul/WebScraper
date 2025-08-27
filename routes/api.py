from flask import Blueprint, jsonify, request
from models import ScrapingJob, ScrapingResult
from tasks import TaskManager
from adapters import AdapterManager
import csv
import io
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/job/<job_id>/status')
def get_job_status(job_id):
    """Get job status via API"""
    from app import db
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    task_manager = TaskManager(db)
    job = task_manager.get_task_status(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)

@api_bp.route('/job/<job_id>/results')
def get_job_results(job_id):
    """Get job results via API"""
    from app import db
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    result_model = ScrapingResult(db)
    results = result_model.get_results(job_id)
    
    return jsonify({'results': results})

@api_bp.route('/job/<job_id>/export/<format>')
def export_job_results(job_id, format):
    """Export job results in CSV or JSON format"""
    from app import db
    from flask import Response
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    result_model = ScrapingResult(db)
    results = result_model.get_results(job_id)
    
    if format.lower() == 'csv':
        # Create CSV export
        output = io.StringIO()
        
        if results:
            # Get all unique keys from results
            all_keys = set()
            for result in results:
                data = result.get('data', {})
                if isinstance(data, dict):
                    all_keys.update(data.keys())
            
            all_keys = ['url'] + sorted(list(all_keys))
            
            writer = csv.DictWriter(output, fieldnames=all_keys)
            writer.writeheader()
            
            for result in results:
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
            json.dumps({'job_id': job_id, 'results': results}, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=job_{job_id}_results.json'}
        )
    
    else:
        return jsonify({'error': 'Unsupported format. Use csv or json'}), 400

@api_bp.route('/adapters')
def list_adapters():
    """List all available adapters"""
    adapter_manager = AdapterManager()
    adapters = adapter_manager.list_adapters()
    return jsonify({'adapters': adapters})

@api_bp.route('/adapter/<name>')
def get_adapter(name):
    """Get specific adapter configuration"""
    adapter_manager = AdapterManager()
    config = adapter_manager.load_adapter(name)
    return jsonify({'name': name, 'config': config})

@api_bp.route('/search', methods=['POST'])
def search_urls():
    """Search for URLs using DuckDuckGo"""
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 20)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    from scraper_engine import ScraperEngine
    scraper = ScraperEngine()
    
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
