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
    mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
    db = mongo_client.get_default_database()  # Use default database from URI
    # Test connection
    mongo_client.admin.command('ping')
    logging.info("MongoDB connected successfully")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
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
