import os
import logging
from flask import Flask
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database - use mock for development simplicity
try:
    mongo_uri = os.environ.get("MONGODB_URI")
    if mongo_uri and "mongodb.net" in mongo_uri:
        # Only try real MongoDB for production Atlas URLs
        mongo_client = MongoClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
        )
        # Test connection quickly
        mongo_client.admin.command('ping')
        db = mongo_client.webscraper
        logging.info("MongoDB Atlas connected successfully")
    else:
        # Use mock database for development to avoid connection issues
        raise Exception("Using mock database for development")
        
except Exception as e:
    logging.info(f"Using mock database: {e}")
    
    # Create a comprehensive mock database
    class MockCollection:
        def __init__(self):
            self._data = []
            self._counter = 0
            
        def insert_one(self, doc):
            self._counter += 1
            doc_id = f"mock_id_{self._counter}"
            doc['_id'] = doc_id
            self._data.append(doc.copy())
            return type('Result', (), {'inserted_id': doc_id})()
            
        def find(self, query=None):
            return MockCursor(self._data)
            
        def find_one(self, query=None):
            if self._data:
                return self._data[-1].copy()
            return None
            
        def count_documents(self, query=None):
            return len(self._data)
            
        def update_one(self, filter_query, update_data):
            # Mock update operation
            return type('Result', (), {'matched_count': 1, 'modified_count': 1})()
            
        def replace_one(self, filter_query, replacement, upsert=False):
            if upsert:
                self.insert_one(replacement)
            return type('Result', (), {'matched_count': 1, 'modified_count': 1})()
            
        def delete_one(self, query):
            return type('Result', (), {'deleted_count': 1})()
    
    class MockCursor:
        def __init__(self, data):
            self._data = data
            
        def sort(self, key, direction=-1):
            return MockCursor(self._data[::-1] if direction == -1 else self._data)
            
        def limit(self, count):
            return MockCursor(self._data[:count])
            
        def __iter__(self):
            return iter(self._data)
    
    class MockDB:
        def __init__(self):
            self.scraping_jobs = MockCollection()
            self.scraping_results = MockCollection()
            self.domain_adapters = MockCollection()
            self.name = "mock_webscraper"
    
    db = MockDB()
    logging.info("Mock database initialized for development")

# Make db available to other modules
app.db = db

# Add CORS support for React frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Register API routes
from routes.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Register the unified app routes for the embedded React app
try:
    from unified_app import app as unified_app_bp
    app.register_blueprint(unified_app_bp)
except ImportError:
    logging.warning("unified_app not found, skipping blueprint registration")
