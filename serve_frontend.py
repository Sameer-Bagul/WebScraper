#!/usr/bin/env python3
"""
Simple static file server for React frontend development
This serves the React frontend files while Flask API runs on port 5000
"""

import os
import http.server
import socketserver
from pathlib import Path

# Change to frontend directory
frontend_dir = Path(__file__).parent / 'frontend'
if frontend_dir.exists():
    os.chdir(frontend_dir)
    print(f"Serving React frontend from: {frontend_dir}")
else:
    print(f"Frontend directory not found: {frontend_dir}")
    exit(1)

PORT = 3000
Handler = http.server.SimpleHTTPRequestHandler

class CustomHTTPRequestHandler(Handler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # For React Router, serve index.html for non-file requests
        if not self.path.startswith('/src/') and not '.' in self.path.split('/')[-1]:
            self.path = '/'
        super().do_GET()

print(f"Starting development server on http://localhost:{PORT}")
print("Frontend files will be served from this directory")
print("Flask API is available on http://localhost:5000")

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()