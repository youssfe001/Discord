import threading
import http.server
import socketserver

PORT = 8080

def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Keep-alive server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()
print("✅ Keep-alive server started.")
