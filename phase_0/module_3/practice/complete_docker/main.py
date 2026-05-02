import os
import time
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from Docker!\n")


def log_heartbeat():
    counter = 0
    while True:
        print(f"[{datetime.now()}] Heartbeat #{counter}", flush=True)
        counter += 1
        time.sleep(2)


def main():
    print("Starting application...\n")

    # Print environment variables
    print("PYTHONDONTWRITEBYTECODE =", os.getenv("PYTHONDONTWRITEBYTECODE"))
    print("PYTHONUNBUFFERED =", os.getenv("PYTHONUNBUFFERED"))
    print()

    # Start logging thread
    t = threading.Thread(target=log_heartbeat, daemon=True)
    t.start()

    # Start HTTP server
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running on port 8000...\n")

    server.serve_forever()


if __name__ == "__main__":
    main()