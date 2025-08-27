import os
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Global database connection
db = None
mongo_client = None

def init_db(app):
    """Initialize database connection"""
    global db, mongo_client
    
    try:
        mongo_uri = os.environ.get("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable not set")
            
        mongo_client = MongoClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        
        # Test connection
        mongo_client.admin.command('ping')
        db = mongo_client.webscraper
        logger.info("MongoDB Atlas connected successfully")
        
        # Store in app context
        app.config['DATABASE'] = db
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_db():
    """Get database instance"""
    return db

def get_collection(name):
    """Get a specific collection"""
    if db is None:
        raise RuntimeError("Database not initialized")
    return db[name]