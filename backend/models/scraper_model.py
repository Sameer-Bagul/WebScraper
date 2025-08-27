from datetime import datetime
from bson import ObjectId
from backend.models.database import get_collection

class ScraperJob:
    def __init__(self, job_type, query, max_results=100, adapters=None):
        self.job_type = job_type
        self.query = query
        self.max_results = max_results
        self.adapters = adapters or []
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.results_count = 0
        
    def to_dict(self):
        return {
            'job_type': self.job_type,
            'query': self.query,
            'max_results': self.max_results,
            'adapters': self.adapters,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'results_count': self.results_count
        }
    
    @classmethod
    def from_dict(cls, data):
        # Handle both old and new data formats
        job_type = data.get('job_type') or data.get('task_type', 'jobs')
        if job_type == 'job_scraping':
            job_type = 'jobs'
        elif job_type == 'lead_generation':
            job_type = 'leads'
        
        query = data.get('query') or data.get('search_query', 'Unknown')
        
        job = cls(
            job_type,
            query,
            data.get('max_results', 100),
            data.get('adapters', [])
        )
        job.status = data.get('status', 'pending')
        job.created_at = data.get('created_at', datetime.utcnow())
        job.updated_at = data.get('updated_at', datetime.utcnow())
        job.results_count = data.get('results_count', 0)
        return job
    
    def save(self):
        """Save job to database"""
        collection = get_collection('scraping_jobs')
        if hasattr(self, '_id'):
            # Update existing
            result = collection.update_one(
                {'_id': self._id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new
            result = collection.insert_one(self.to_dict())
            self._id = result.inserted_id
            return True
    
    @classmethod
    def find_all(cls):
        """Get all jobs"""
        collection = get_collection('scraping_jobs')
        jobs = []
        for doc in collection.find().sort('created_at', -1):
            job = cls.from_dict(doc)
            job._id = doc['_id']
            jobs.append(job)
        return jobs
    
    @classmethod
    def find_by_id(cls, job_id):
        """Find job by ID"""
        collection = get_collection('scraping_jobs')
        doc = collection.find_one({'_id': ObjectId(job_id)})
        if doc:
            job = cls.from_dict(doc)
            job._id = doc['_id']
            return job
        return None

class ScraperResult:
    def __init__(self, job_id, title, company=None, location=None, url=None, 
                 description=None, contact_info=None, scraped_at=None):
        self.job_id = ObjectId(job_id) if isinstance(job_id, str) else job_id
        self.title = title
        self.company = company
        self.location = location
        self.url = url
        self.description = description
        self.contact_info = contact_info or {}
        self.scraped_at = scraped_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'url': self.url,
            'description': self.description,
            'contact_info': self.contact_info,
            'scraped_at': self.scraped_at
        }
    
    def save(self):
        """Save result to database"""
        collection = get_collection('scraping_results')
        result = collection.insert_one(self.to_dict())
        self._id = result.inserted_id
        return True
    
    @classmethod
    def find_by_job_id(cls, job_id):
        """Find results by job ID"""
        collection = get_collection('scraping_results')
        results = []
        
        # Try both job_id and task_id for compatibility
        query = {'$or': [{'job_id': ObjectId(job_id)}, {'task_id': ObjectId(job_id)}]}
        
        for doc in collection.find(query):
            # Handle different field names from legacy data
            title = doc.get('title') or doc.get('name', 'Unknown')
            company = doc.get('company') or doc.get('organization')
            
            result = cls(
                doc.get('job_id') or doc.get('task_id'),
                title,
                company,
                doc.get('location'),
                doc.get('url') or doc.get('link'),
                doc.get('description'),
                doc.get('contact_info', {}),
                doc.get('scraped_at') or doc.get('created_at')
            )
            result._id = doc['_id']
            results.append(result)
        return results