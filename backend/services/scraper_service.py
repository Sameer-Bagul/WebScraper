import requests
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from backend.models.scraper_model import ScraperJob, ScraperResult
from backend.services.contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.contact_extractor = ContactExtractor()
    
    def scrape_jobs(self, query, max_results=100):
        """Scrape job listings"""
        logger.info(f"Starting job scrape for query: {query}")
        
        # Create scraper job
        job = ScraperJob('jobs', query, max_results)
        job.status = 'running'
        job.save()
        
        try:
            results = []
            
            # Sample job data for demonstration
            sample_jobs = [
                {
                    'title': f'{query} Developer - Senior Position',
                    'company': 'TechCorp Solutions',
                    'location': 'San Francisco, CA',
                    'url': 'https://example.com/job1',
                    'description': f'We are looking for an experienced {query} developer to join our team...'
                },
                {
                    'title': f'{query} Engineer - Remote',
                    'company': 'Innovation Labs',
                    'location': 'Remote',
                    'url': 'https://example.com/job2',
                    'description': f'Remote {query} position with competitive salary and benefits...'
                },
                {
                    'title': f'Lead {query} Architect',
                    'company': 'Enterprise Systems Inc',
                    'location': 'New York, NY',
                    'url': 'https://example.com/job3',
                    'description': f'Leadership role for {query} architecture and system design...'
                }
            ]
            
            for i, job_data in enumerate(sample_jobs):
                if i >= max_results:
                    break
                    
                # Add some contact information
                contact_info = {
                    'email': f'hr@{job_data["company"].lower().replace(" ", "")}.com',
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}'
                }
                
                result = ScraperResult(
                    job_id=job._id,
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    url=job_data['url'],
                    description=job_data['description'],
                    contact_info=contact_info
                )
                result.save()
                results.append(result)
                
                # Simulate processing time
                time.sleep(0.5)
            
            # Update job status
            job.status = 'completed'
            job.results_count = len(results)
            job.updated_at = datetime.utcnow()
            job.save()
            
            logger.info(f"Job scrape completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during job scraping: {e}")
            job.status = 'failed'
            job.save()
            raise
    
    def scrape_leads(self, query, max_results=100):
        """Scrape business leads"""
        logger.info(f"Starting lead generation for query: {query}")
        
        # Create scraper job
        job = ScraperJob('leads', query, max_results)
        job.status = 'running'
        job.save()
        
        try:
            results = []
            
            # Sample lead data
            sample_leads = [
                {
                    'title': f'{query} Agency - Digital Marketing',
                    'company': 'Creative Solutions LLC',
                    'location': 'Los Angeles, CA',
                    'url': 'https://example.com/lead1',
                    'description': f'Full-service {query} agency providing comprehensive solutions...'
                },
                {
                    'title': f'{query} Consulting Firm',
                    'company': 'Strategy Partners Inc',
                    'location': 'Chicago, IL',
                    'url': 'https://example.com/lead2',
                    'description': f'Professional {query} consulting with 10+ years experience...'
                },
                {
                    'title': f'{query} Startup - Series A',
                    'company': 'NextGen Innovations',
                    'location': 'Austin, TX',
                    'url': 'https://example.com/lead3',
                    'description': f'Fast-growing {query} startup looking for partnerships...'
                }
            ]
            
            for i, lead_data in enumerate(sample_leads):
                if i >= max_results:
                    break
                    
                # Add comprehensive contact information
                contact_info = {
                    'email': f'contact@{lead_data["company"].lower().replace(" ", "")}.com',
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'website': lead_data['url'],
                    'linkedin': f'https://linkedin.com/company/{lead_data["company"].lower().replace(" ", "-")}'
                }
                
                result = ScraperResult(
                    job_id=job._id,
                    title=lead_data['title'],
                    company=lead_data['company'],
                    location=lead_data['location'],
                    url=lead_data['url'],
                    description=lead_data['description'],
                    contact_info=contact_info
                )
                result.save()
                results.append(result)
                
                # Simulate processing time
                time.sleep(0.5)
            
            # Update job status
            job.status = 'completed'
            job.results_count = len(results)
            job.updated_at = datetime.utcnow()
            job.save()
            
            logger.info(f"Lead generation completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during lead generation: {e}")
            job.status = 'failed'
            job.save()
            raise
    
    def get_job_status(self, job_id):
        """Get job status"""
        job = ScraperJob.find_by_id(job_id)
        if job:
            results = ScraperResult.find_by_job_id(job_id)
            return {
                'job': job.to_dict(),
                'results': [r.to_dict() for r in results]
            }
        return None