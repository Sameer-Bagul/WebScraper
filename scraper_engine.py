import requests
import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from lxml import html
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt, wait_exponential
from duckduckgo_search import DDGS
from config import Config
import trafilatura

logger = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with headers and configuration"""
        self.session.headers.update({
            'User-Agent': Config.DEFAULT_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.session.headers['User-Agent'] = random.choice(user_agents)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_static(self, url: str) -> Optional[str]:
        """Fetch page content using requests (static scraping)"""
        try:
            self.rotate_user_agent()
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Static scraping failed for {url}: {e}")
            return None
    
    def fetch_dynamic(self, url: str, wait_time: int = 3) -> Optional[str]:
        """Fetch page content using Playwright (dynamic scraping)"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle')
                time.sleep(wait_time)  # Wait for dynamic content
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            logger.error(f"Dynamic scraping failed for {url}: {e}")
            return None
    
    def extract_text_content(self, url: str) -> Optional[str]:
        """Extract clean text content using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded)
            return text
        except Exception as e:
            logger.error(f"Text extraction failed for {url}: {e}")
            return None
    
    def scrape_with_adapter(self, url: str, adapter_config: Dict, use_dynamic: bool = False) -> Dict:
        """Scrape URL using adapter configuration"""
        # Fetch content
        if use_dynamic:
            content = self.fetch_dynamic(url)
        else:
            content = self.fetch_static(url)
            if not content and adapter_config.get('fallback_to_dynamic', True):
                logger.info(f"Falling back to dynamic scraping for {url}")
                content = self.fetch_dynamic(url)
        
        if not content:
            return {'error': 'Failed to fetch content'}
        
        # Parse content
        try:
            tree = html.fromstring(content)
            result = {'url': url, 'scraped_data': {}}
            
            # Extract data using selectors
            selectors = adapter_config.get('selectors', {})
            for field, selector_config in selectors.items():
                extracted_value = self.extract_field(tree, selector_config)
                if extracted_value:
                    result['scraped_data'][field] = extracted_value
            
            # Extract links if specified
            if adapter_config.get('extract_links', False):
                links = self.extract_links(tree, url)
                result['scraped_data']['links'] = links
            
            # Extract text content if specified
            if adapter_config.get('extract_text', False):
                text_content = self.extract_text_content(url)
                if text_content:
                    result['scraped_data']['text_content'] = text_content
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing content for {url}: {e}")
            return {'error': f'Parsing failed: {str(e)}'}
    
    def extract_field(self, tree, selector_config) -> Optional[str]:
        """Extract field using selector configuration"""
        try:
            selector = selector_config.get('selector')
            attribute = selector_config.get('attribute', 'text')
            multiple = selector_config.get('multiple', False)
            
            if not selector:
                return None
            
            # Use CSS or XPath selector
            if selector.startswith('//') or selector.startswith('.//'):
                elements = tree.xpath(selector)
            else:
                elements = tree.cssselect(selector)
            
            if not elements:
                return None
            
            # Extract value(s)
            values = []
            for element in elements:
                if attribute == 'text':
                    value = element.text_content().strip()
                else:
                    value = element.get(attribute, '').strip()
                
                if value:
                    values.append(value)
            
            if not values:
                return None
            
            if multiple:
                return values
            else:
                return values[0] if values else None
            
        except Exception as e:
            logger.error(f"Error extracting field: {e}")
            return None
    
    def extract_links(self, tree, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        try:
            link_elements = tree.cssselect('a[href]')
            for element in link_elements:
                href = element.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    links.append(absolute_url)
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return list(set(links))  # Remove duplicates
    
    def search_duckduckgo(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search DuckDuckGo for URLs"""
        try:
            ddgs = DDGS()
            results = []
            
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'description': result.get('body', '')
                })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
    
    def rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(Config.RATE_LIMIT_DELAY + random.uniform(0, 1))

class BatchScraper:
    def __init__(self, scraper_engine: ScraperEngine):
        self.scraper = scraper_engine
        
    def scrape_urls(self, urls: List[str], adapter_config: Dict, 
                   progress_callback=None) -> List[Dict]:
        """Scrape multiple URLs with progress tracking"""
        results = []
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Scraping {i+1}/{total_urls}: {url}")
                
                # Apply rate limiting
                if i > 0:
                    self.scraper.rate_limit()
                
                # Scrape URL
                result = self.scraper.scrape_with_adapter(url, adapter_config)
                results.append(result)
                
                # Update progress
                if progress_callback:
                    progress = ((i + 1) / total_urls) * 100
                    progress_callback(progress, i + 1, len([r for r in results if 'error' not in r]))
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append({'url': url, 'error': str(e)})
        
        return results
