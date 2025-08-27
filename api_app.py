import os
import logging
from flask import Flask, jsonify
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.secret_key = "web-scraper-secret-key-2024"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add CORS support for React frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "web_scraper"

# Initialize MongoDB
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[DATABASE_NAME]
    # Test connection
    mongo_client.admin.command('ismaster')
    logging.info("MongoDB connected successfully")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    db = None

# Make db available to other modules
app.db = db

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db else 'disconnected',
        'message': 'Web Scraper API is running'
    })

@app.route('/api/adapters', methods=['GET'])
def list_adapters():
    """List all available scraping adapters"""
    try:
        from adapters import AdapterManager
        adapter_manager = AdapterManager()
        adapters = adapter_manager.list_adapters()
        return jsonify({'adapters': adapters})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_urls():
    """Search for URLs using DuckDuckGo"""
    from flask import request
    
    try:
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 20)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        from scraper_engine import ScraperEngine
        scraper = ScraperEngine()
        results = scraper.search_duckduckgo(query, max_results)
        
        return jsonify({'results': results})
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new scraping job"""
    from flask import request
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        job_type = data.get('type', 'scrape')
        
        from models import ScrapingJob
        from tasks import TaskManager
        
        job_model = ScrapingJob(db)
        task_manager = TaskManager(db)
        
        if job_type == 'search':
            query = data.get('query', '')
            max_results = data.get('max_results', 20)
            
            if not query:
                return jsonify({'error': 'Search query is required'}), 400
            
            job_id = job_model.create_job({
                'type': 'search',
                'query': query,
                'max_results': max_results
            })
            
            task_manager.start_search_task(job_id, query, max_results)
            
        else:
            urls = data.get('urls', [])
            adapter_name = data.get('adapter_name', 'default')
            task_type = data.get('task_type', 'general')
            
            if not urls:
                return jsonify({'error': 'URLs are required'}), 400
            
            job_id = job_model.create_job({
                'type': 'scrape',
                'urls': urls,
                'adapter_name': adapter_name,
                'task_type': task_type
            })
            
            task_manager.start_scraping_task(job_id, urls, adapter_name, task_type)
        
        return jsonify({'job_id': job_id, 'status': 'started'})
        
    except Exception as e:
        logging.error(f"Job creation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        from tasks import TaskManager
        task_manager = TaskManager(db)
        job = task_manager.get_task_status(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job)
    except Exception as e:
        logging.error(f"Status check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get job results"""
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        from models import ScrapingResult
        result_model = ScrapingResult(db)
        results = result_model.get_results(job_id)
        
        return jsonify({'results': results})
    except Exception as e:
        logging.error(f"Results fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        from models import Analytics
        analytics = Analytics(db)
        stats = analytics.get_dashboard_stats()
        
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Stats fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)