from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Sample data for now
adapters = [
    {"name": "default", "display_name": "Default General Scraper", "description": "General purpose scraper for any website"},
    {"name": "indeed", "display_name": "Indeed Job Board", "description": "Scraper for Indeed job listings"},
    {"name": "linkedin", "display_name": "LinkedIn Jobs", "description": "Scraper for LinkedIn job listings"},
    {"name": "business_directory", "display_name": "Business Directory", "description": "Scraper for business directories"}
]

jobs = []
job_counter = 1

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Web Scraper API is running'})

@app.route('/api/adapters', methods=['GET'])
def list_adapters():
    return jsonify({'adapters': adapters})

@app.route('/api/search', methods=['POST'])
def search_urls():
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 20)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Mock search results
    results = [
        {'title': f'Sample result {i+1} for "{query}"', 'url': f'https://example{i+1}.com', 'description': f'Description for result {i+1}'}
        for i in range(min(max_results, 5))
    ]
    
    return jsonify({'results': results})

@app.route('/api/jobs', methods=['POST'])
def create_job():
    global job_counter
    data = request.json
    
    job = {
        'id': str(job_counter),
        'type': data.get('type', 'scrape'),
        'status': 'completed',
        'progress': 100,
        'created_at': '2024-01-01T00:00:00Z',
        'query': data.get('query'),
        'urls': data.get('urls', []),
        'adapter_name': data.get('adapter_name'),
        'task_type': data.get('task_type'),
        'results_count': 3
    }
    
    jobs.append(job)
    job_counter += 1
    
    return jsonify({'job_id': job['id'], 'status': 'started'})

@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/api/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    # Mock results
    results = [
        {
            'url': 'https://example1.com',
            'data': {'title': 'Sample Title 1', 'description': 'Sample description'},
            'scraped_at': '2024-01-01T00:00:00Z'
        },
        {
            'url': 'https://example2.com', 
            'data': {'title': 'Sample Title 2', 'description': 'Another description'},
            'scraped_at': '2024-01-01T00:01:00Z'
        }
    ]
    return jsonify({'results': results})

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    return jsonify({'jobs': jobs})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_jobs': len(jobs),
        'completed_jobs': len([j for j in jobs if j['status'] == 'completed']),
        'running_jobs': len([j for j in jobs if j['status'] == 'running']),
        'failed_jobs': len([j for j in jobs if j['status'] == 'failed']),
        'total_results': sum(j.get('results_count', 0) for j in jobs)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)