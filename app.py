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

# Initialize MongoDB
try:
    mongo_uri = os.environ.get("MONGODB_URI")
    if mongo_uri:
        # Add database name to URI if not present
        if '?' in mongo_uri and 'authSource=' in mongo_uri:
            # URI already has parameters, just add database if missing
            if not any(part.startswith('/') and not part.startswith('/?') for part in mongo_uri.split('mongodb.net')):
                mongo_uri = mongo_uri.replace('mongodb.net', 'mongodb.net/webscraper')
        else:
            # Add database name
            if 'mongodb.net' in mongo_uri and '/?' not in mongo_uri:
                mongo_uri = mongo_uri.replace('mongodb.net', 'mongodb.net/webscraper')
        
        # Try with standard SSL settings for Atlas
        mongo_client = MongoClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,  # Allow invalid certs for Replit environment
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        
        # Get the database - use webscraper as default name
        if 'webscraper' in mongo_uri:
            db = mongo_client.webscraper
        else:
            db = mongo_client.get_default_database()
            
        # Test connection
        mongo_client.admin.command('ping')
        logging.info("MongoDB connected successfully")
    else:
        raise Exception("MONGODB_URI not found in environment")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    logging.info("Application will use fallback mock data functionality")
    db = None

# Make db available to other modules
app.db = db

# Add CORS support for React frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Register API routes
from routes.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Register the unified app routes for the embedded React app
from unified_app import app as unified_app_bp
app.register_blueprint(unified_app_bp)
