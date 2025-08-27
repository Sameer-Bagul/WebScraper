from datetime import datetime
from typing import Dict, List, Optional, Any
from app import db
from sqlalchemy import Text, JSON
import json


class ScrapingJob(db.Model):
    __tablename__ = 'scraping_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='pending')
    task_type = db.Column(db.String(50), default='general')
    adapter_name = db.Column(db.String(100), default='default')
    search_query = db.Column(Text)
    urls = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)
    total_urls = db.Column(db.Integer, default=0)
    completed_urls = db.Column(db.Integer, default=0)
    failed_urls = db.Column(db.Integer, default=0)
    results_count = db.Column(db.Integer, default=0)
    error_message = db.Column(Text)
    
    # Relationship with results
    results = db.relationship('ScrapingResult', backref='job', cascade='all, delete-orphan', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'status': self.status,
            'task_type': self.task_type,
            'adapter_name': self.adapter_name,
            'search_query': self.search_query,
            'urls': self.urls or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'progress': self.progress,
            'total_urls': self.total_urls,
            'completed_urls': self.completed_urls,
            'failed_urls': self.failed_urls,
            'results_count': self.results_count,
            'error_message': self.error_message
        }
    
    @classmethod
    def create_job(cls, job_data: Dict) -> 'ScrapingJob':
        """Create a new scraping job"""
        job = cls(
            status=job_data.get('status', 'pending'),
            task_type=job_data.get('task_type', 'general'),
            adapter_name=job_data.get('adapter_name', 'default'),
            search_query=job_data.get('search_query'),
            urls=job_data.get('urls', []),
            progress=job_data.get('progress', 0),
            total_urls=job_data.get('total_urls', 0),
            completed_urls=job_data.get('completed_urls', 0),
            failed_urls=job_data.get('failed_urls', 0),
            results_count=job_data.get('results_count', 0),
            error_message=job_data.get('error_message')
        )
        db.session.add(job)
        db.session.commit()
        return job
    
    def update_job(self, update_data: Dict):
        """Update job status and progress"""
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_jobs(cls, limit: int = 50) -> List['ScrapingJob']:
        """Get recent jobs"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()


class ScrapingResult(db.Model):
    __tablename__ = 'scraping_results'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('scraping_jobs.id'), nullable=False)
    url = db.Column(Text, nullable=False)
    result_type = db.Column(db.String(50), default='general')
    data = db.Column(JSON)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'url': self.url,
            'result_type': self.result_type,
            'data': self.data,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
    
    @classmethod
    def save_result(cls, job_id: int, url: str, data: Dict, result_type: str = 'general'):
        """Save scraping result"""
        result = cls(
            job_id=job_id,
            url=url,
            result_type=result_type,
            data=data
        )
        db.session.add(result)
        db.session.commit()
        return result
    
    @classmethod
    def get_results(cls, job_id: int) -> List['ScrapingResult']:
        """Get results for a job"""
        return cls.query.filter_by(job_id=job_id).all()
    
    @classmethod
    def get_results_by_type(cls, job_id: int, result_type: str) -> List['ScrapingResult']:
        """Get results by type (job, lead, general)"""
        return cls.query.filter_by(job_id=job_id, result_type=result_type).all()


class DomainAdapter(db.Model):
    __tablename__ = 'domain_adapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    config = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def save_adapter(cls, name: str, config: Dict):
        """Save or update domain adapter"""
        adapter = cls.query.filter_by(name=name).first()
        if adapter:
            adapter.config = config
            adapter.updated_at = datetime.utcnow()
        else:
            adapter = cls(name=name, config=config)
            db.session.add(adapter)
        db.session.commit()
        return adapter
    
    @classmethod
    def get_adapter(cls, name: str) -> Optional['DomainAdapter']:
        """Get adapter by name"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_adapters(cls) -> List['DomainAdapter']:
        """Get all adapters"""
        return cls.query.all()
    
    def delete_adapter(self):
        """Delete adapter"""
        db.session.delete(self)
        db.session.commit()


class Analytics:
    @staticmethod
    def get_dashboard_stats() -> Dict:
        """Get dashboard statistics"""
        total_jobs = ScrapingJob.query.count()
        completed_jobs = ScrapingJob.query.filter_by(status='completed').count()
        failed_jobs = ScrapingJob.query.filter_by(status='failed').count()
        running_jobs = ScrapingJob.query.filter_by(status='running').count()
        
        total_results = ScrapingResult.query.count()
        
        # Recent job statistics
        recent_jobs = ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).limit(10).all()
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'running_jobs': running_jobs,
            'total_results': total_results,
            'recent_jobs': [job.to_dict() for job in recent_jobs]
        }
