# Web Scraper Pro

A professional web scraping application built with React.js frontend and Flask API backend, designed for job hunting and lead generation.

## Architecture

- **Frontend**: React.js with Vite, Bootstrap 5 dark theme
- **Backend**: Flask API with CORS support
- **Database**: MongoDB (planned integration)
- **Scraping**: Requests + Playwright for static and dynamic content

## Current Status

✅ **Completed**:
- React.js frontend with responsive UI
- Flask API backend with mock data
- Job management dashboard
- URL search and direct scraping interfaces
- Adapter system for different website types

🔄 **In Progress**:
- MongoDB integration
- Real scraping engine implementation
- Contact extraction system

## Quick Start

### Backend (Flask API)
The Flask API is running on port 5000 and provides these endpoints:

- `GET /api/health` - Health check
- `GET /api/adapters` - List available scraping adapters
- `POST /api/search` - Search for URLs using DuckDuckGo
- `POST /api/jobs` - Create new scraping jobs
- `GET /api/jobs/{id}/status` - Get job status
- `GET /api/jobs/{id}/results` - Get job results
- `GET /api/stats` - Dashboard statistics

### Frontend (React)
The React frontend includes:

- **Home Page**: Create new scraping jobs with search or direct URL input
- **Dashboard**: View job statistics and recent jobs with real-time updates
- **Results Page**: View detailed scraping results with JSON data display

## Key Features

1. **Smart URL Discovery**: Search engines integration for finding relevant URLs
2. **Flexible Adapters**: JSON-based configuration for different website types
3. **Real-time Updates**: Live job status monitoring and progress tracking
4. **Responsive Design**: Mobile-friendly Bootstrap interface with dark theme
5. **Contact Extraction**: Automatic email, phone, and social media extraction (planned)

## Development Notes

- All API endpoints are tested and working with mock data
- React components are responsive and follow Bootstrap conventions
- CORS is properly configured for frontend-backend communication
- Architecture is ready for MongoDB and real scraping implementation

## Next Steps

1. Integrate MongoDB for data persistence
2. Implement real web scraping with requests and Playwright
3. Add contact extraction using spaCy and regex
4. Deploy React frontend with proper build process
5. Add authentication and user management