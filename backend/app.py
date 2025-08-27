import os
import logging
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Initialize database connection
    from backend.models.database import init_db
    init_db(app)
    
    # Register blueprints
    from backend.controllers.scraper_controller import scraper_bp
    from backend.controllers.admin_controller import admin_bp
    from backend.controllers.api_controller import api_bp
    
    app.register_blueprint(scraper_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

app = create_app()