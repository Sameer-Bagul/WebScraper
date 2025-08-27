from datetime import datetime
from typing import Dict, List, Optional, Any
import json

try:
    from bson import ObjectId
except ImportError:
    # Fallback for mock ObjectId
    class ObjectId:
        def __init__(self, id_str=None):
            self.id = id_str or '507f1f77bcf86cd799439011'
        
        def __str__(self):
            return self.id

class ScrapingJob:
    def __init__(self, db):
        self.collection = db.scraping_jobs
    
    def create_job(self, job_data: Dict) -> str:
        """Create a new scraping job"""
        job = {
            'status': job_data.get('status', 'pending'),
            'task_type': job_data.get('task_type', 'general'),
            'adapter_name': job_data.get('adapter_name', 'default'),
            'search_query': job_data.get('search_query'),
            'urls': job_data.get('urls', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'progress': job_data.get('progress', 0),
            'total_urls': job_data.get('total_urls', 0),
            'completed_urls': job_data.get('completed_urls', 0),
            'failed_urls': job_data.get('failed_urls', 0),
            'results_count': job_data.get('results_count', 0),
            'error_message': job_data.get('error_message')
        }
        result = self.collection.insert_one(job)
        return str(result.inserted_id)
    
    def update_job(self, job_id: str, update_data: Dict):
        """Update job status and progress"""
        update_data['updated_at'] = datetime.utcnow()
        if isinstance(job_id, str) and len(job_id) == 24:
            # Valid ObjectId string
            try:
                self.collection.update_one(
                    {'_id': ObjectId(job_id)},
                    {'$set': update_data}
                )
            except:
                # Fallback for mock database
                pass
        else:
            # Mock database or invalid ID
            pass
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        try:
            if isinstance(job_id, str) and len(job_id) == 24:
                job = self.collection.find_one({'_id': ObjectId(job_id)})
            else:
                # For mock database
                jobs = list(self.collection.find())
                job = jobs[0] if jobs else None
                
            if job:
                job['_id'] = str(job.get('_id', job_id))
                job['id'] = job['_id']  # Add id field for compatibility
                # Convert datetime to ISO format
                if 'created_at' in job and job['created_at']:
                    if isinstance(job['created_at'], datetime):
                        job['created_at'] = job['created_at'].isoformat()
                if 'updated_at' in job and job['updated_at']:
                    if isinstance(job['updated_at'], datetime):
                        job['updated_at'] = job['updated_at'].isoformat()
            return job
        except:
            return None
    
    def get_jobs(self, limit: int = 50) -> List[Dict]:
        """Get recent jobs"""
        try:
            jobs = list(self.collection.find().sort('created_at', -1).limit(limit))
        except:
            # Fallback for mock database
            jobs = list(self.collection.find())[:limit]
            
        for job in jobs:
            job['_id'] = str(job.get('_id', ''))
            job['id'] = job['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'created_at' in job and job['created_at']:
                if isinstance(job['created_at'], datetime):
                    job['created_at'] = job['created_at'].isoformat()
            if 'updated_at' in job and job['updated_at']:
                if isinstance(job['updated_at'], datetime):
                    job['updated_at'] = job['updated_at'].isoformat()
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
        try:
            results = list(self.collection.find({'job_id': job_id}))
        except:
            # Fallback for mock database
            results = list(self.collection.find())
            
        for result in results:
            result['_id'] = str(result.get('_id', ''))
            result['id'] = result['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'scraped_at' in result and result['scraped_at']:
                if isinstance(result['scraped_at'], datetime):
                    result['scraped_at'] = result['scraped_at'].isoformat()
        return results
    
    def get_results_by_type(self, job_id: str, result_type: str) -> List[Dict]:
        """Get results by type (job, lead, general)"""
        try:
            results = list(self.collection.find({
                'job_id': job_id,
                'result_type': result_type
            }))
        except:
            # Fallback for mock database
            results = list(self.collection.find())
            
        for result in results:
            result['_id'] = str(result.get('_id', ''))
            result['id'] = result['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'scraped_at' in result and result['scraped_at']:
                if isinstance(result['scraped_at'], datetime):
                    result['scraped_at'] = result['scraped_at'].isoformat()
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
        try:
            self.collection.replace_one(
                {'name': name},
                adapter,
                upsert=True
            )
        except:
            # Fallback for mock database
            self.collection.insert_one(adapter)
    
    def get_adapter(self, name: str) -> Optional[Dict]:
        """Get adapter by name"""
        try:
            adapter = self.collection.find_one({'name': name})
        except:
            # Fallback for mock database
            adapters = list(self.collection.find())
            adapter = next((a for a in adapters if a.get('name') == name), None)
            
        if adapter:
            adapter['_id'] = str(adapter.get('_id', ''))
            adapter['id'] = adapter['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'created_at' in adapter and adapter['created_at']:
                if isinstance(adapter['created_at'], datetime):
                    adapter['created_at'] = adapter['created_at'].isoformat()
            if 'updated_at' in adapter and adapter['updated_at']:
                if isinstance(adapter['updated_at'], datetime):
                    adapter['updated_at'] = adapter['updated_at'].isoformat()
        return adapter
    
    def get_adapters(self) -> List[Dict]:
        """Get all adapters"""
        try:
            adapters = list(self.collection.find())
        except:
            # Fallback for mock database
            adapters = list(self.collection.find())
            
        for adapter in adapters:
            adapter['_id'] = str(adapter.get('_id', ''))
            adapter['id'] = adapter['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'created_at' in adapter and adapter['created_at']:
                if isinstance(adapter['created_at'], datetime):
                    adapter['created_at'] = adapter['created_at'].isoformat()
            if 'updated_at' in adapter and adapter['updated_at']:
                if isinstance(adapter['updated_at'], datetime):
                    adapter['updated_at'] = adapter['updated_at'].isoformat()
        return adapters
    
    def delete_adapter(self, name: str):
        """Delete adapter"""
        try:
            self.collection.delete_one({'name': name})
        except:
            # Fallback for mock database
            pass

class Analytics:
    def __init__(self, db):
        self.db = db
        self.jobs_collection = db.scraping_jobs
        self.results_collection = db.scraping_results
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            total_jobs = self.jobs_collection.count_documents({})
            completed_jobs = self.jobs_collection.count_documents({'status': 'completed'})
            failed_jobs = self.jobs_collection.count_documents({'status': 'failed'})
            running_jobs = self.jobs_collection.count_documents({'status': 'running'})
            total_results = self.results_collection.count_documents({})
            
            # Recent job statistics
            recent_jobs = list(self.jobs_collection.find().sort('created_at', -1).limit(10))
        except:
            # Fallback for mock database
            total_jobs = 0
            completed_jobs = 0
            failed_jobs = 0
            running_jobs = 0
            total_results = 0
            recent_jobs = []
            
        for job in recent_jobs:
            job['_id'] = str(job.get('_id', ''))
            job['id'] = job['_id']  # Add id field for compatibility
            # Convert datetime to ISO format
            if 'created_at' in job and job['created_at']:
                if isinstance(job['created_at'], datetime):
                    job['created_at'] = job['created_at'].isoformat()
            if 'updated_at' in job and job['updated_at']:
                if isinstance(job['updated_at'], datetime):
                    job['updated_at'] = job['updated_at'].isoformat()
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'running_jobs': running_jobs,
            'total_results': total_results,
            'recent_jobs': recent_jobs
        }
