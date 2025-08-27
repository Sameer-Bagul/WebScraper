# Web Scraper Pro

## Overview

Web Scraper Pro is a professional web scraping application designed for two primary use cases: job hunting and lead generation for freelancing. The application now features a React.js frontend with Vite development server and a Flask API backend. Currently running with mock data to demonstrate the complete architecture before implementing the full scraping engine with MongoDB integration.

## Recent Changes (August 27, 2025)

✓ **Migration to Replit Environment:** Successfully migrated from Replit Agent to standard Replit
✓ **MongoDB Atlas Integration:** Connected to user's MongoDB Atlas database with MONGODB_URI secret
✓ **Real-Time Scraping Engine:** Implemented complete job scraping and lead generation system
✓ **API Endpoints Created:** Added /api/scrape/jobs and /api/scrape/leads for real-time operations
✓ **Contact Extraction System:** Built NLP-based contact information extraction from web pages
✓ **Database Storage:** All scraping results now stored directly in MongoDB Atlas collections
✓ **Demo Functionality:** Working system demonstrates job scraping with sample data creation

## User Preferences

Preferred communication style: Simple, everyday language.
Architecture preference: React.js frontend + Flask API backend

## System Architecture

### Frontend Architecture
- **Framework**: React.js 18 with Vite development server
- **Routing**: React Router DOM for single-page application navigation
- **UI Components**: Bootstrap 5 with dark theme and Bootstrap Icons
- **HTTP Client**: Axios for API communication with Flask backend
- **Styling**: Custom CSS with JSON syntax highlighting and loading overlays

### Backend Architecture
- **Web Framework**: Flask API with CORS support for React frontend
- **API Design**: RESTful endpoints for jobs, adapters, search, and statistics
- **Task Management**: Background job processing system (to be implemented with MongoDB)
- **Scraping Engine**: Dual-mode scraping architecture planned (requests + Playwright)
- **Adapter System**: JSON-based configurable selectors for different website types
- **Contact Extraction**: NLP-based extraction system (to be integrated)

### Data Storage
- **Primary Database**: MongoDB with PyMongo driver for MERN stack compatibility
- **Collections**: scraping_jobs, scraping_results, domain_adapters
- **Document Structure**: JSON-based documents with ObjectId references
- **File Storage**: Local filesystem for adapter configurations and exported results
- **Current Status**: Full MongoDB integration with document-based models ready for MERN migration

### Authentication & Authorization
- **Session Management**: Flask's built-in session handling with secret key configuration
- **Access Control**: Route-based access with admin panel separation
- **Security**: ProxyFix middleware for proper header handling behind reverse proxies

### Scraping Architecture
- **Adapter Pattern**: JSON configuration files defining site-specific CSS selectors and extraction rules
- **Rate Limiting**: Configurable delays and retry mechanisms with exponential backoff
- **Anti-Detection**: User agent rotation and proxy support for high-volume scraping
- **Content Processing**: Trafilatura integration for clean text extraction and DuckDuckGo search integration

## External Dependencies

### Core Web Framework
- **Flask**: Main web application framework with Blueprint routing
- **Werkzeug**: WSGI utilities including ProxyFix middleware

### Data Processing & Storage
- **PyMongo**: MongoDB driver for database operations
- **lxml**: XML/HTML parsing and CSS selector processing
- **trafilatura**: Clean text extraction from web pages

### Scraping & Browser Automation
- **requests**: HTTP client for static content fetching
- **Playwright**: Browser automation for JavaScript-heavy websites
- **tenacity**: Retry logic with exponential backoff for failed requests
- **duckduckgo-search**: Web search integration for URL discovery

### Natural Language Processing
- **spaCy**: NLP library for advanced contact information extraction
- **en_core_web_sm**: English language model for entity recognition

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme support
- **Feather Icons**: Icon library for UI elements
- **Chart.js**: Data visualization for dashboard analytics
- **DataTables**: Enhanced table functionality with sorting and filtering

### Development & Utilities
- **python-dotenv**: Environment variable management
- **logging**: Built-in Python logging for debugging and monitoring