from flask import Blueprint, request, jsonify
from backend.services.scraper_service import ScraperService
from backend.models.scraper_model import ScraperJob, ScraperResult

api_bp = Blueprint('api', __name__)
scraper_service = ScraperService()

@api_bp.route('/scrape/jobs', methods=['POST'])
def scrape_jobs():
    """API endpoint for job scraping"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 100)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = scraper_service.scrape_jobs(query, max_results)
        
        return jsonify({
            'success': True,
            'message': f'Found {len(results)} job results',
            'results': [result.to_dict() for result in results]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scrape/leads', methods=['POST'])
def scrape_leads():
    """API endpoint for lead generation"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 100)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = scraper_service.scrape_leads(query, max_results)
        
        return jsonify({
            'success': True,
            'message': f'Found {len(results)} lead results',
            'results': [result.to_dict() for result in results]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all scraping jobs"""
    try:
        jobs = ScraperJob.find_all()
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get results for a specific job"""
    try:
        job = ScraperJob.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        results = ScraperResult.find_by_job_id(job_id)
        
        return jsonify({
            'success': True,
            'job': job.to_dict(),
            'results': [result.to_dict() for result in results]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get scraping statistics"""
    try:
        jobs = ScraperJob.find_all()
        total_jobs = len(jobs)
        completed_jobs = len([j for j in jobs if j.status == 'completed'])
        total_results = sum(j.results_count for j in jobs)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'total_results': total_results,
                'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500