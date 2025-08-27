import asyncio
import logging
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
from models import ScrapingJob, ScrapingResult
from scraper_engine import ScraperEngine, BatchScraper
from contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

class RealTimeScraper:
    """Real-time scraping engine for jobs and leads"""
    
    def __init__(self, db):
        self.db = db
        self.scraper_engine = ScraperEngine()
        self.batch_scraper = BatchScraper(self.scraper_engine)
        self.contact_extractor = ContactExtractor()
        self.job_sources = {
            'indeed': {
                'search_url': 'https://www.indeed.com/jobs',
                'selectors': {
                    'job_title': {'selector': '.jobsearch-SerpJobCard-title a', 'attribute': 'text'},
                    'company': {'selector': '.company', 'attribute': 'text'},
                    'location': {'selector': '.location', 'attribute': 'text'},
                    'salary': {'selector': '.salary', 'attribute': 'text'},
                    'description': {'selector': '.summary', 'attribute': 'text'},
                    'url': {'selector': '.jobsearch-SerpJobCard-title a', 'attribute': 'href'}
                }
            },
            'linkedin': {
                'search_url': 'https://www.linkedin.com/jobs/search',
                'selectors': {
                    'job_title': {'selector': '.job-result-card__title', 'attribute': 'text'},
                    'company': {'selector': '.job-result-card__subtitle', 'attribute': 'text'},
                    'location': {'selector': '.job-result-card__location', 'attribute': 'text'},
                    'url': {'selector': '.job-result-card__title', 'attribute': 'href'}
                }
            }
        }
        
    def start_real_time_job_scraping(self, job_data: Dict) -> str:
        """Start real-time job scraping"""
        scraping_job_model = ScrapingJob(self.db)
        job_id = scraping_job_model.create_job({
            **job_data,
            'status': 'running',
            'task_type': 'job_scraping'
        })
        
        # Start scraping in background
        asyncio.create_task(self._scrape_jobs_async(job_id, job_data))
        return job_id
    
    def start_real_time_lead_scraping(self, job_data: Dict) -> str:
        """Start real-time lead generation scraping"""
        scraping_job_model = ScrapingJob(self.db)
        job_id = scraping_job_model.create_job({
            **job_data,
            'status': 'running',
            'task_type': 'lead_generation'
        })
        
        # Start scraping in background
        asyncio.create_task(self._scrape_leads_async(job_id, job_data))
        return job_id
    
    async def _scrape_jobs_async(self, job_id: str, job_data: Dict):
        """Async job scraping with real-time updates"""
        scraping_job_model = ScrapingJob(self.db)
        scraping_result_model = ScrapingResult(self.db)
        
        try:
            query = job_data.get('search_query', '')
            adapter_name = job_data.get('adapter_name', 'indeed')
            max_results = job_data.get('max_results', 50)
            
            logger.info(f"Starting job scraping for query: {query}")
            
            # Get job URLs from search
            if adapter_name in self.job_sources:
                job_urls = await self._search_job_urls(query, adapter_name, max_results)
            else:
                # Use DuckDuckGo search for generic job sites
                search_query = f"{query} jobs site:indeed.com OR site:linkedin.com"
                search_results = self.scraper_engine.search_duckduckgo(search_query, max_results)
                job_urls = [r['url'] for r in search_results]
            
            # Update job with URLs found
            scraping_job_model.update_job(job_id, {
                'urls': job_urls,
                'total_urls': len(job_urls),
                'status': 'processing'
            })
            
            # Scrape each job URL
            scraped_count = 0
            failed_count = 0
            
            for i, url in enumerate(job_urls):
                try:
                    logger.info(f"Scraping job {i+1}/{len(job_urls)}: {url}")
                    
                    # Get adapter config
                    adapter_config = self.job_sources.get(adapter_name, {
                        'selectors': {
                            'job_title': {'selector': 'h1, .job-title, .title', 'attribute': 'text'},
                            'company': {'selector': '.company, .employer', 'attribute': 'text'},
                            'location': {'selector': '.location, .job-location', 'attribute': 'text'},
                            'salary': {'selector': '.salary, .pay', 'attribute': 'text'},
                            'description': {'selector': '.description, .job-summary', 'attribute': 'text'}
                        }
                    })
                    
                    # Scrape the job page
                    result = self.scraper_engine.scrape_with_adapter(url, adapter_config)
                    
                    if 'error' not in result:
                        # Save job result
                        scraping_result_model.save_result(job_id, url, result, 'job')
                        scraped_count += 1
                        logger.info(f"Successfully scraped job: {result.get('scraped_data', {}).get('job_title', 'Unknown')}")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to scrape {url}: {result.get('error')}")
                    
                    # Update progress
                    progress = int(((i + 1) / len(job_urls)) * 100)
                    scraping_job_model.update_job(job_id, {
                        'progress': progress,
                        'completed_urls': i + 1,
                        'failed_urls': failed_count,
                        'results_count': scraped_count
                    })
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error scraping job URL {url}: {e}")
            
            # Mark job as completed
            scraping_job_model.update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'completed_urls': len(job_urls),
                'failed_urls': failed_count,
                'results_count': scraped_count
            })
            
            logger.info(f"Job scraping completed. Scraped: {scraped_count}, Failed: {failed_count}")
            
        except Exception as e:
            logger.error(f"Job scraping failed for job {job_id}: {e}")
            scraping_job_model.update_job(job_id, {
                'status': 'failed',
                'error_message': str(e)
            })
    
    async def _scrape_leads_async(self, job_id: str, job_data: Dict):
        """Async lead generation scraping with real-time updates"""
        scraping_job_model = ScrapingJob(self.db)
        scraping_result_model = ScrapingResult(self.db)
        
        try:
            query = job_data.get('search_query', '')
            max_results = job_data.get('max_results', 50)
            
            logger.info(f"Starting lead generation for query: {query}")
            
            # Search for business/lead URLs
            search_query = f"{query} contact email phone"
            search_results = self.scraper_engine.search_duckduckgo(search_query, max_results)
            lead_urls = [r['url'] for r in search_results]
            
            # Update job with URLs found
            scraping_job_model.update_job(job_id, {
                'urls': lead_urls,
                'total_urls': len(lead_urls),
                'status': 'processing'
            })
            
            # Scrape each lead URL
            scraped_count = 0
            failed_count = 0
            
            for i, url in enumerate(lead_urls):
                try:
                    logger.info(f"Scraping lead {i+1}/{len(lead_urls)}: {url}")
                    
                    # Get page content
                    content = self.scraper_engine.fetch_static(url)
                    if not content:
                        content = self.scraper_engine.fetch_dynamic(url)
                    
                    if content:
                        # Extract contact information
                        contacts = self.contact_extractor.extract_contacts(content, url)
                        
                        if contacts:
                            # Save lead result
                            lead_data = {
                                'url': url,
                                'contacts': contacts,
                                'scraped_data': {
                                    'company': self._extract_company_name(url, content),
                                    'contact_count': len(contacts),
                                    'emails': [c.get('email') for c in contacts if c.get('email')],
                                    'phones': [c.get('phone') for c in contacts if c.get('phone')]
                                }
                            }
                            
                            scraping_result_model.save_result(job_id, url, lead_data, 'lead')
                            scraped_count += 1
                            logger.info(f"Successfully extracted {len(contacts)} contacts from {url}")
                        else:
                            failed_count += 1
                            logger.warning(f"No contacts found on {url}")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to fetch content from {url}")
                    
                    # Update progress
                    progress = int(((i + 1) / len(lead_urls)) * 100)
                    scraping_job_model.update_job(job_id, {
                        'progress': progress,
                        'completed_urls': i + 1,
                        'failed_urls': failed_count,
                        'results_count': scraped_count
                    })
                    
                    # Rate limiting
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error scraping lead URL {url}: {e}")
            
            # Mark job as completed
            scraping_job_model.update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'completed_urls': len(lead_urls),
                'failed_urls': failed_count,
                'results_count': scraped_count
            })
            
            logger.info(f"Lead generation completed. Scraped: {scraped_count}, Failed: {failed_count}")
            
        except Exception as e:
            logger.error(f"Lead generation failed for job {job_id}: {e}")
            scraping_job_model.update_job(job_id, {
                'status': 'failed',
                'error_message': str(e)
            })
    
    async def _search_job_urls(self, query: str, platform: str, max_results: int) -> List[str]:
        """Search for job URLs on specific platforms"""
        urls = []
        
        try:
            if platform == 'indeed':
                # Search Indeed jobs
                search_url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&limit={max_results}"
                content = self.scraper_engine.fetch_static(search_url)
                
                if content:
                    from lxml import html
                    tree = html.fromstring(content)
                    job_links = tree.cssselect('.jobsearch-SerpJobCard-title a')
                    
                    for link in job_links:
                        href = link.get('href')
                        if href:
                            full_url = urljoin('https://www.indeed.com', href)
                            urls.append(full_url)
            
            elif platform == 'linkedin':
                # For LinkedIn, use DuckDuckGo search since direct scraping is restricted
                search_query = f"{query} jobs site:linkedin.com/jobs"
                search_results = self.scraper_engine.search_duckduckgo(search_query, max_results)
                urls = [r['url'] for r in search_results if 'linkedin.com/jobs' in r['url']]
            
        except Exception as e:
            logger.error(f"Error searching {platform}: {e}")
        
        return urls[:max_results]
    
    def _extract_company_name(self, url: str, content: str) -> str:
        """Extract company name from URL or content"""
        try:
            # Try to get from domain
            domain = urlparse(url).netloc
            if domain:
                company = domain.replace('www.', '').split('.')[0]
                return company.title()
            
            # Try to extract from content
            from lxml import html
            tree = html.fromstring(content)
            
            # Common selectors for company names
            selectors = [
                'title',
                '.company-name',
                '.brand',
                'h1',
                '.logo img[alt]'
            ]
            
            for selector in selectors:
                elements = tree.cssselect(selector)
                if elements:
                    text = elements[0].text_content().strip()
                    if text and len(text) < 100:
                        return text
            
        except Exception as e:
            logger.error(f"Error extracting company name: {e}")
        
        return "Unknown Company"