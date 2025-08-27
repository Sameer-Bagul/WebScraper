import os
import json

class Config:
    # MongoDB Configuration
    MONGODB_URI = "mongodb://localhost:27017/"
    DATABASE_NAME = "web_scraper"
    
    # Scraping Configuration
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RATE_LIMIT_DELAY = 1  # seconds between requests
    
    # Proxy Configuration
    USE_PROXIES = False
    PROXY_LIST = []  # Add proxy URLs here if needed
    
    # Contact Extraction
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_REGEX = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    # File paths
    ADAPTERS_DIR = "adapters"
    RESULTS_DIR = "results"
    
    # Create directories if they don't exist
    @staticmethod
    def init_directories():
        import os
        for directory in [Config.ADAPTERS_DIR, Config.RESULTS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    # Load adapter configurations
    @staticmethod
    def load_adapters():
        Config.init_directories()
        adapters = {}
        adapter_files = [f for f in os.listdir(Config.ADAPTERS_DIR) if f.endswith('.json')]
        
        for filename in adapter_files:
            adapter_name = filename[:-5]  # Remove .json extension
            try:
                with open(os.path.join(Config.ADAPTERS_DIR, filename), 'r') as f:
                    adapters[adapter_name] = json.load(f)
            except Exception as e:
                print(f"Error loading adapter {filename}: {e}")
        
        return adapters

# Initialize directories on import
Config.init_directories()
