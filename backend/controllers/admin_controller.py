from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from backend.models.database import get_collection
from backend.models.scraper_model import ScraperJob

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def dashboard():
    """Admin dashboard"""
    jobs = ScraperJob.find_all()
    stats = {
        'total_jobs': len(jobs),
        'completed_jobs': len([j for j in jobs if j.status == 'completed']),
        'failed_jobs': len([j for j in jobs if j.status == 'failed']),
        'running_jobs': len([j for j in jobs if j.status == 'running'])
    }
    return render_template('admin/dashboard.html', jobs=jobs, stats=stats)

@admin_bp.route('/jobs')
def jobs():
    """Manage scraping jobs"""
    jobs = ScraperJob.find_all()
    return render_template('admin/jobs.html', jobs=jobs)

@admin_bp.route('/adapters')
def adapters():
    """Manage scraping adapters"""
    return render_template('admin/adapters.html')

@admin_bp.route('/settings')
def settings():
    """System settings"""
    return render_template('admin/settings.html')

@admin_bp.route('/clear-data', methods=['POST'])
def clear_data():
    """Clear all scraping data"""
    try:
        jobs_collection = get_collection('scraping_jobs')
        results_collection = get_collection('scraping_results')
        
        jobs_collection.delete_many({})
        results_collection.delete_many({})
        
        return jsonify({'success': True, 'message': 'All data cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500