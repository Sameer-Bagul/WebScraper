import os
import logging
from flask import Flask
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.secret_key = "web-scraper-secret-key-2024"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import config
from config import Config
app.config.from_object(Config)

# Initialize MongoDB
try:
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    db = mongo_client[app.config['DATABASE_NAME']]
    # Test connection
    mongo_client.admin.command('ismaster')
    logging.info("MongoDB connected successfully")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    db = None

# Make db available to other modules
app.db = db

# Register API blueprints only (React frontend will handle UI)
from routes.api import api_bp

app.register_blueprint(api_bp, url_prefix='/api')

# Add CORS support for React frontend
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
