# Simple HTTP server
# This runs a web server inside the container on port 8000
import http.server
import socketserver
import os

PORT = 8000

# Change to the current directory
os.chdir('/app')

# Create a simple handler
Handler = http.server.SimpleHTTPRequestHandler

# Create the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on port {PORT}...")
    httpd.serve_forever()
