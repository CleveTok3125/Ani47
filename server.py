import http.server
import socketserver
import socket

def start_server(PORT=8000, share=False):
	print(f'''Access player via "http://127.0.0.1:{PORT}"{" or IP address" if share else ""}''')
	if is_free_port(PORT):
		try:
			with socketserver.TCPServer(("" if share else "127.0.0.1", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
				print(f'Listening on: http://127.0.0.1:{PORT}')
				httpd.serve_forever()
		except OSError:
			PORT += 1
			print(f'{PORT-1} is in use, trying port {PORT}...')
			start_server(PORT=PORT, share=share)
	else:
		print(f"Reusing port: http://127.0.0.1:{PORT}")

def is_free_port(PORT, host='127.0.0.1'):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		result = s.connect_ex((host, PORT))
		if result == 0:
			return False
		else:
			return True