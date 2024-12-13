import http.server
import socketserver

def start_server(PORT=8000):
	with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
		httpd.serve_forever()