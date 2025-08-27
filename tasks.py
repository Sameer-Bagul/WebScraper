import threading
import logging
from typing import Dict, List, Callable
from datetime import datetime
from scraper_engine import ScraperEngine, BatchScraper
from contact_extractor import ContactExtractor
from adapters import AdapterManager

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, db):
        self.db = db
        self.running_tasks = {}
        self.scraper_engine = ScraperEngine()
        self.batch_scraper = BatchScraper(self.scraper_engine)
        self.contact_extractor = ContactExtractor()
        self.adapter_manager = AdapterManager()
    
    def start_scraping_task(self, job_id: str, urls: List[str], adapter_name: str, 
                           task_type: str = 'general') -> str:
        """Start a scraping task in background thread"""
        from models import ScrapingJob, ScrapingResult
        
        job_model = ScrapingJob(self.db)
        result_model = ScrapingResult(self.db)
        
        # Update job status
        job_model.update_job(job_id, {
            'status': 'running',
            'total_urls': len(urls),
            'started_at': datetime.utcnow()
        })
        
        # Create progress callback
        def progress_callback(progress: float, completed: int, successful: int):
            job_model.update_job(job_id, {
                'progress': progress,
                'completed_urls': completed,
                'results_count': successful
            })
        
        # Start scraping in background thread
        thread = threading.Thread(
            target=self._run_scraping_task,
            args=(job_id, urls, adapter_name, task_type, job_model, result_model, progress_callback)
        )
        thread.daemon = True
        thread.start()
        
        self.running_tasks[job_id] = thread
        return job_id
    
    def _run_scraping_task(self, job_id: str, urls: List[str], adapter_name: str, 
                          task_type: str, job_model, result_model, progress_callback):
        """Run the actual scraping task"""
        try:
            # Load adapter configuration
            adapter_config = self.adapter_manager.load_adapter(adapter_name)
            
            # Scrape URLs
            results = self.batch_scraper.scrape_urls(urls, adapter_config, progress_callback)
            
            # Process and save results
            successful_results = 0
            failed_results = 0
            
            for result in results:
                if 'error' not in result:
                    # Extract contacts if it's a lead generation task
                    if task_type in ['lead', 'job']:
                        scraped_data = result.get('scraped_data', {})
                        
                        # Get HTML content for contact extraction
                        url = result['url']
                        html_content = self.scraper_engine.fetch_static(url)
                        
                        if html_content:
                            if task_type == 'lead':
                                contacts = self.contact_extractor.extract_from_html(html_content)
                                lead_score = self.contact_extractor.score_lead_quality(contacts)
                                scraped_data['contacts'] = contacts
                                scraped_data['lead_score'] = lead_score
                            elif task_type == 'job':
                                job_details = self.contact_extractor.extract_job_details(html_content)
                                scraped_data.update(job_details)
                        
                        result['scraped_data'] = scraped_data
                    
                    # Save result
                    result_model.save_result(job_id, result['url'], result['scraped_data'], task_type)
                    successful_results += 1
                else:
                    failed_results += 1
                    logger.error(f"Failed to scrape {result.get('url', 'unknown')}: {result.get('error')}")
            
            # Update job completion
            job_model.update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'completed_urls': len(urls),
                'results_count': successful_results,
                'failed_urls': failed_results,
                'completed_at': datetime.utcnow()
            })
            
            logger.info(f"Scraping task {job_id} completed: {successful_results} successful, {failed_results} failed")
            
        except Exception as e:
            logger.error(f"Scraping task {job_id} failed: {e}")
            job_model.update_job(job_id, {
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.utcnow()
            })
        finally:
            # Remove from running tasks
            if job_id in self.running_tasks:
                del self.running_tasks[job_id]
    
    def start_search_task(self, job_id: str, query: str, max_results: int = 20) -> str:
        """Start a DuckDuckGo search task"""
        from models import ScrapingJob
        
        job_model = ScrapingJob(self.db)
        
        # Update job status
        job_model.update_job(job_id, {
            'status': 'running',
            'started_at': datetime.utcnow()
        })
        
        # Start search in background thread
        thread = threading.Thread(
            target=self._run_search_task,
            args=(job_id, query, max_results, job_model)
        )
        thread.daemon = True
        thread.start()
        
        self.running_tasks[job_id] = thread
        return job_id
    
    def _run_search_task(self, job_id: str, query: str, max_results: int, job_model):
        """Run the actual search task"""
        try:
            # Perform search
            search_results = self.scraper_engine.search_duckduckgo(query, max_results)
            
            # Update job with results
            job_model.update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'results_count': len(search_results),
                'search_results': search_results,
                'completed_at': datetime.utcnow()
            })
            
            logger.info(f"Search task {job_id} completed with {len(search_results)} results")
            
        except Exception as e:
            logger.error(f"Search task {job_id} failed: {e}")
            job_model.update_job(job_id, {
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.utcnow()
            })
        finally:
            # Remove from running tasks
            if job_id in self.running_tasks:
                del self.running_tasks[job_id]
    
    def get_task_status(self, job_id: str) -> Dict:
        """Get status of a running task"""
        from models import ScrapingJob
        
        job_model = ScrapingJob(self.db)
        job = job_model.get_job(job_id)
        
        if job:
            job['is_running'] = job_id in self.running_tasks
        
        return job
    
    def cancel_task(self, job_id: str) -> bool:
        """Cancel a running task"""
        if job_id in self.running_tasks:
            # Note: Python threads can't be forcibly terminated
            # This would require a more sophisticated cancellation mechanism
            logger.warning(f"Task {job_id} cancellation requested (graceful stop not implemented)")
            return True
        return False
