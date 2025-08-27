from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from bson import ObjectId
except ImportError:
    from pymongo import ObjectId

class ScrapingJob:
    def __init__(self, db):
        self.collection = db.scraping_jobs
    
    def create_job(self, job_data: Dict) -> str:
        """Create a new scraping job"""
        job = {
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'progress': 0,
            'total_urls': 0,
            'completed_urls': 0,
            'failed_urls': 0,
            'results_count': 0,
            'error_message': None,
            **job_data
        }
        result = self.collection.insert_one(job)
        return str(result.inserted_id)
    
    def update_job(self, job_id: str, update_data: Dict):
        """Update job status and progress"""
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': update_data}
        )
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        job = self.collection.find_one({'_id': ObjectId(job_id)})
        if job:
            job['_id'] = str(job['_id'])
        return job
    
    def get_jobs(self, limit: int = 50) -> List[Dict]:
        """Get recent jobs"""
        jobs = list(self.collection.find().sort('created_at', -1).limit(limit))
        for job in jobs:
            job['_id'] = str(job['_id'])
        return jobs

class ScrapingResult:
    def __init__(self, db):
        self.collection = db.scraping_results
    
    def save_result(self, job_id: str, url: str, data: Dict, result_type: str = 'general'):
        """Save scraping result"""
        result = {
            'job_id': job_id,
            'url': url,
            'result_type': result_type,
            'data': data,
            'scraped_at': datetime.utcnow()
        }
        return self.collection.insert_one(result)
    
    def get_results(self, job_id: str) -> List[Dict]:
        """Get results for a job"""
        results = list(self.collection.find({'job_id': job_id}))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def get_results_by_type(self, job_id: str, result_type: str) -> List[Dict]:
        """Get results by type (job, lead, general)"""
        results = list(self.collection.find({
            'job_id': job_id,
            'result_type': result_type
        }))
        for result in results:
            result['_id'] = str(result['_id'])
        return results

class DomainAdapter:
    def __init__(self, db):
        self.collection = db.domain_adapters
    
    def save_adapter(self, name: str, config: Dict):
        """Save or update domain adapter"""
        adapter = {
            'name': name,
            'config': config,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        self.collection.replace_one(
            {'name': name},
            adapter,
            upsert=True
        )
    
    def get_adapter(self, name: str) -> Optional[Dict]:
        """Get adapter by name"""
        return self.collection.find_one({'name': name})
    
    def get_adapters(self) -> List[Dict]:
        """Get all adapters"""
        adapters = list(self.collection.find())
        for adapter in adapters:
            adapter['_id'] = str(adapter['_id'])
        return adapters
    
    def delete_adapter(self, name: str):
        """Delete adapter"""
        self.collection.delete_one({'name': name})

class Analytics:
    def __init__(self, db):
        self.db = db
        self.jobs_collection = db.scraping_jobs
        self.results_collection = db.scraping_results
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        total_jobs = self.jobs_collection.count_documents({})
        completed_jobs = self.jobs_collection.count_documents({'status': 'completed'})
        failed_jobs = self.jobs_collection.count_documents({'status': 'failed'})
        running_jobs = self.jobs_collection.count_documents({'status': 'running'})
        
        total_results = self.results_collection.count_documents({})
        
        # Recent job statistics
        recent_jobs = list(self.jobs_collection.find().sort('created_at', -1).limit(10))
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'running_jobs': running_jobs,
            'total_results': total_results,
            'recent_jobs': recent_jobs
        }
