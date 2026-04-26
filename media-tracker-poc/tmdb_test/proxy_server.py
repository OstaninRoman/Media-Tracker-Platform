#!/usr/bin/env python3
"""
TMDB Proxy Server - обход DNS блокировки
Проксирует запросы к TMDB API с подменой DNS
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import socket
import json
from urllib.parse import urlparse, parse_qs

# TMDB API Configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_HOST = "api.themoviedb.org"
TMDB_IPS = ["3.170.19.94", "3.170.19.97", "3.170.19.104", "3.170.19.106"]
TMDB_API_KEY = "858e37ef0424fed70858d44465fc3a71"

# Save original getaddrinfo
_original_getaddrinfo = socket.getaddrinfo

def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Patch socket.getaddrinfo to use real TMDB IPs instead of blocked DNS"""
    if host == TMDB_HOST:
        ip = TMDB_IPS[0]
        return _original_getaddrinfo(ip, port, family, type, proto, flags)
    return _original_getaddrinfo(host, port, family, type, proto, flags)

# Apply the patch
socket.getaddrinfo = _patched_getaddrinfo

class TMDBProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path.startswith('/proxy/tmdb/'):
            # Extract TMDB path and query
            tmdb_path = parsed.path.replace('/proxy/tmdb/', '')
            query_params = parse_qs(parsed.query)

            # Add API key if not present
            if 'api_key' not in query_params:
                query_params['api_key'] = [TMDB_API_KEY]

            # Build TMDB URL
            tmdb_url = f"{TMDB_BASE_URL}/{tmdb_path}"

            try:
                response = requests.get(tmdb_url, params=query_params, timeout=15)

                # Send response
                self.send_response(response.status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.content)

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            # Serve static files
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    server = HTTPServer(('localhost', port), TMDBProxyHandler)
    print(f"Proxy server running at http://localhost:{port}")
    print(f"TMDB API proxy: http://localhost:{port}/proxy/tmdb/{{endpoint}}")
    print("Press Ctrl+C to stop")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
