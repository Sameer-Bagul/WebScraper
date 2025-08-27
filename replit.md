# Web Scraper Pro

## Overview

Web Scraper Pro is a professional web scraping application designed for two primary use cases: job hunting and lead generation for freelancing. The application now features a React.js frontend with Vite development server and a Flask API backend. Currently running with mock data to demonstrate the complete architecture before implementing the full scraping engine with MongoDB integration.

## Recent Changes (August 27, 2025)

✓ Converted from Flask templates to React.js frontend with Vite
✓ Created API-only Flask backend with CORS support
✓ Built responsive React components with Bootstrap dark theme
✓ Implemented job management dashboard with real-time updates
✓ Added URL search functionality and direct scraping interface
✓ Created adapter selection system for different website types
✓ Resolved BSON package conflicts by using pymongo's bson module

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
- **Primary Database**: MongoDB integration planned (currently using mock data)
- **Collections**: Will store jobs, results, and system metrics
- **File Storage**: Local filesystem for adapter configurations and exported results
- **Current Status**: Mock data endpoints for frontend development and testing

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