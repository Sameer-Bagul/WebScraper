# Windows Development Setup Guide

## Prerequisites

### 1. Install Python 3.11+
- Download from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation
- Verify installation:
```bash
python --version
pip --version
```

### 2. Install Node.js 18+
- Download from [nodejs.org](https://nodejs.org/)
- Verify installation:
```bash
node --version
npm --version
```

### 3. Install Git
- Download from [git-scm.com](https://git-scm.com/download/win)
- Use default settings during installation

## Project Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-directory>
```

### 2. Backend Setup (Flask API)

#### Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install flask flask-cors flask-login flask-sqlalchemy
pip install pymongo beautifulsoup4 requests lxml trafilatura
pip install playwright spacy tenacity duckduckgo-search
pip install email-validator ratelimit gunicorn psycopg2-binary
pip install werkzeug
```

#### Environment Variables
Create a `.env` file in the root directory:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/webscraper
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Frontend Setup (React)

#### Install Node.js Dependencies
```bash
cd frontend-react
npm install
```

#### Start Development Server
```bash
npm run dev
```
The frontend will run on http://localhost:3000

### 4. Backend Server

#### Start Flask API
```bash
# From project root directory
python main.py
```
The API will run on http://localhost:5000

## Running Both Servers

### Option 1: Two Terminal Windows
**Terminal 1 (Backend):**
```bash
venv\Scripts\activate
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend-react
npm run dev
```

### Option 2: Using PowerShell Script
Create `start-dev.ps1`:
```powershell
# Start backend in background
Start-Process powershell -ArgumentList "-Command", "venv\Scripts\activate; python main.py"

# Wait a moment then start frontend
Start-Sleep -Seconds 3
cd frontend-react
npm run dev
```

Run: `powershell -ExecutionPolicy Bypass -File start-dev.ps1`

## Database Setup

### MongoDB Atlas (Recommended)
1. Create account at [mongodb.com](https://www.mongodb.com/)
2. Create a new cluster
3. Get connection string
4. Update `MONGODB_URI` in `.env` file

### Local MongoDB (Alternative)
1. Download from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Install with default settings
3. Use connection string: `mongodb://localhost:27017/webscraper`

## Browser Requirements

### Chrome/Chromium (for Playwright)
```bash
# Install browser dependencies
python -m playwright install chromium
```

## Troubleshooting

### Common Issues

#### Python not found
- Ensure Python is added to PATH
- Restart command prompt after Python installation

#### Permission errors
- Run command prompt as Administrator
- Use `--user` flag: `pip install --user package-name`

#### Port already in use
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <process-id> /F
```

#### Virtual environment issues
```bash
# Deactivate current environment
deactivate

# Remove and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
```

### Module import errors
```bash
# Ensure you're in the correct directory
cd project-root

# Activate virtual environment
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

## Development Workflow

### 1. Daily Startup
```bash
# Activate Python environment
venv\Scripts\activate

# Start backend (Terminal 1)
python main.py

# Start frontend (Terminal 2)
cd frontend-react
npm run dev
```

### 2. Adding New Dependencies

**Python packages:**
```bash
venv\Scripts\activate
pip install package-name
pip freeze > requirements.txt
```

**Node.js packages:**
```bash
cd frontend-react
npm install package-name
```

### 3. Database Operations
- Use MongoDB Compass for GUI database management
- Download from [mongodb.com/products/compass](https://www.mongodb.com/products/compass)

## Production Deployment

### Windows Server Setup
1. Install IIS with Python support
2. Configure reverse proxy for Flask app
3. Use pm2 or Windows Service for process management
4. Set up SSL certificates

### Alternative: Docker
Create `Dockerfile` in project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

## IDE Recommendations

### VS Code (Recommended)
**Extensions:**
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- MongoDB for VS Code
- Thunder Client (API testing)

### PyCharm Professional
- Built-in Python support
- Database tools
- Web development features

## Testing

### Backend Tests
```bash
venv\Scripts\activate
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend-react
npm test
```

## Performance Optimization

### Python
- Use `gunicorn` for production
- Enable Redis for caching
- Configure connection pooling

### React
- Build production bundle: `npm run build`
- Serve with nginx or IIS

## Security Notes

### Development
- Never commit `.env` files
- Use different secrets for development/production
- Regularly update dependencies

### Production
- Use HTTPS only
- Configure CORS properly
- Set up proper authentication
- Monitor for vulnerabilities

## Support

If you encounter issues:
1. Check error logs in both terminal windows
2. Verify all dependencies are installed
3. Ensure database connection is working
4. Check firewall settings for ports 3000 and 5000

For MongoDB connection issues, verify:
- Database URL is correct
- Network access is allowed
- Database user has proper permissions

## Next Steps

1. ✅ Set up development environment
2. ✅ Start both servers
3. ✅ Test database connection
4. 🔄 Begin development work
5. 🔄 Deploy to production

Your web scraper is now ready for Windows development!