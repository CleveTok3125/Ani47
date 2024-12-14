import http.server
import socketserver

def start_server(PORT=8000, share=False):
	with socketserver.TCPServer(("" if share else "127.0.0.1", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
		httpd.serve_forever()