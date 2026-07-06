#!/usr/bin/env python3
"""Simple HTTP server that serves static files AND proxies CoverageMap API requests to avoid CORS."""
import http.server
import json
import urllib.request
import urllib.error
import ssl
import os

# Create SSL context that doesn't verify certs (for proxying HTTPS APIs)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

COVERAGEMAP_KEY = '075561175ee04c3192b153251a8ad541'
PORT = 8000

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Proxy CoverageMap API requests
        if self.path.startswith('/api/coveragemap?'):
            self.proxy_coveragemap()
        else:
            super().do_GET()

    def proxy_coveragemap(self):
        try:
            # Extract query string
            qs = self.path.split('?', 1)[1] if '?' in self.path else ''
            url = f'https://enterprise.coveragemap.com/api/v1/signal-strength/lookup?{qs}'
            
            req = urllib.request.Request(url, headers={
                'Authorization': f'Bearer {COVERAGEMAP_KEY}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                data = resp.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        # Suppress noisy logs, only show API proxy calls
        if '/api/coveragemap' in str(args[0]):
            super().log_message(format, *args)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.HTTPServer(('', PORT), ProxyHandler) as httpd:
        print(f'Serving on http://localhost:{PORT}')
        print(f'CoverageMap proxy at /api/coveragemap?latitude=...&longitude=...')
        httpd.serve_forever()
