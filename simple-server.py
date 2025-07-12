#!/usr/bin/env python3
"""
Simple HTTP server for Butay Parlor website
This serves the static HTML file and handles basic review storage
"""

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
import cgi

PORT = 8000

class ButayParlorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/home.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/api/reviews':
            self.handle_review_submission()
        else:
            self.send_error(404, "Not found")
    
    def handle_review_submission(self):
        # Read the request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            name = data.get('name', '').strip()
            review = data.get('review', '').strip()
            rating = data.get('rating', '').strip()
            
            if not name or not review or not rating:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing fields'}).encode())
                return
            
            # Load existing reviews
            reviews = []
            if os.path.exists('reviews.json'):
                try:
                    with open('reviews.json', 'r', encoding='utf-8') as f:
                        reviews = json.load(f)
                except:
                    reviews = []
            
            # Add new review
            new_review = {
                'name': name,
                'review': review,
                'rating': rating,
                'date': json.dumps({'$date': '2024-01-01T00:00:00.000Z'})
            }
            reviews.insert(0, new_review)
            
            # Save reviews
            with open('reviews.json', 'w', encoding='utf-8') as f:
                json.dump(reviews, f, indent=2, ensure_ascii=False)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    print(f"Starting Butay Parlor server on http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    with socketserver.TCPServer(("", PORT), ButayParlorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.") 