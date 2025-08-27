import json
import os
from typing import Dict, List
from config import Config

class AdapterManager:
    def __init__(self):
        self.adapters_dir = Config.ADAPTERS_DIR
        self.ensure_adapters_dir()
        self.load_default_adapters()
    
    def ensure_adapters_dir(self):
        """Ensure adapters directory exists"""
        if not os.path.exists(self.adapters_dir):
            os.makedirs(self.adapters_dir)
    
    def load_default_adapters(self):
        """Load default adapters if they don't exist"""
        default_adapters = {
            'default': self.get_default_adapter(),
            'indeed': self.get_indeed_adapter(),
            'linkedin': self.get_linkedin_adapter(),
            'business_directory': self.get_business_directory_adapter()
        }
        
        for name, config in default_adapters.items():
            adapter_file = os.path.join(self.adapters_dir, f"{name}.json")
            if not os.path.exists(adapter_file):
                self.save_adapter(name, config)
    
    def get_default_adapter(self) -> Dict:
        """Default general-purpose adapter"""
        return {
            "name": "Default General Scraper",
            "description": "General purpose scraper for any website",
            "selectors": {
                "title": {
                    "selector": "title",
                    "attribute": "text"
                },
                "headings": {
                    "selector": "h1, h2, h3",
                    "attribute": "text",
                    "multiple": True
                },
                "links": {
                    "selector": "a[href]",
                    "attribute": "href",
                    "multiple": True
                },
                "paragraphs": {
                    "selector": "p",
                    "attribute": "text",
                    "multiple": True
                }
            },
            "extract_links": True,
            "extract_text": True,
            "fallback_to_dynamic": True
        }
    
    def get_indeed_adapter(self) -> Dict:
        """Indeed job board adapter"""
        return {
            "name": "Indeed Job Board",
            "description": "Scraper for Indeed job listings",
            "selectors": {
                "job_title": {
                    "selector": "[data-jk] h2 a span",
                    "attribute": "text"
                },
                "company": {
                    "selector": "[data-jk] .companyName",
                    "attribute": "text"
                },
                "location": {
                    "selector": "[data-jk] .companyLocation",
                    "attribute": "text"
                },
                "salary": {
                    "selector": "[data-jk] .salary-snippet",
                    "attribute": "text"
                },
                "summary": {
                    "selector": "[data-jk] .job-snippet",
                    "attribute": "text"
                },
                "job_url": {
                    "selector": "[data-jk] h2 a",
                    "attribute": "href"
                }
            },
            "extract_links": False,
            "extract_text": False,
            "fallback_to_dynamic": True
        }
    
    def get_linkedin_adapter(self) -> Dict:
        """LinkedIn adapter (basic structure)"""
        return {
            "name": "LinkedIn Jobs",
            "description": "Scraper for LinkedIn job listings",
            "selectors": {
                "job_title": {
                    "selector": ".job-search-card__title",
                    "attribute": "text"
                },
                "company": {
                    "selector": ".job-search-card__subtitle-link",
                    "attribute": "text"
                },
                "location": {
                    "selector": ".job-search-card__location",
                    "attribute": "text"
                },
                "job_url": {
                    "selector": ".job-search-card__title-link",
                    "attribute": "href"
                }
            },
            "extract_links": False,
            "extract_text": False,
            "fallback_to_dynamic": True
        }
    
    def get_business_directory_adapter(self) -> Dict:
        """Business directory adapter for lead generation"""
        return {
            "name": "Business Directory",
            "description": "Scraper for business directories and company listings",
            "selectors": {
                "business_name": {
                    "selector": ".business-name, .company-name, h1, h2",
                    "attribute": "text"
                },
                "address": {
                    "selector": ".address, .location, [class*='address']",
                    "attribute": "text"
                },
                "phone": {
                    "selector": ".phone, .tel, [class*='phone']",
                    "attribute": "text"
                },
                "email": {
                    "selector": "a[href^='mailto:']",
                    "attribute": "href"
                },
                "website": {
                    "selector": ".website, a[class*='website']",
                    "attribute": "href"
                },
                "description": {
                    "selector": ".description, .about, p",
                    "attribute": "text",
                    "multiple": True
                }
            },
            "extract_links": True,
            "extract_text": True,
            "fallback_to_dynamic": False
        }
    
    def save_adapter(self, name: str, config: Dict):
        """Save adapter configuration to file"""
        adapter_file = os.path.join(self.adapters_dir, f"{name}.json")
        with open(adapter_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_adapter(self, name: str) -> Dict:
        """Load adapter configuration from file"""
        adapter_file = os.path.join(self.adapters_dir, f"{name}.json")
        if os.path.exists(adapter_file):
            with open(adapter_file, 'r') as f:
                return json.load(f)
        return self.get_default_adapter()
    
    def list_adapters(self) -> List[Dict]:
        """List all available adapters"""
        adapters = []
        if os.path.exists(self.adapters_dir):
            for filename in os.listdir(self.adapters_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]  # Remove .json extension
                    try:
                        config = self.load_adapter(name)
                        adapters.append({
                            'name': name,
                            'display_name': config.get('name', name),
                            'description': config.get('description', ''),
                            'filename': filename
                        })
                    except Exception as e:
                        print(f"Error loading adapter {filename}: {e}")
        return adapters
    
    def delete_adapter(self, name: str) -> bool:
        """Delete adapter file"""
        adapter_file = os.path.join(self.adapters_dir, f"{name}.json")
        if os.path.exists(adapter_file) and name not in ['default']:  # Don't delete default
            os.remove(adapter_file)
            return True
        return False
