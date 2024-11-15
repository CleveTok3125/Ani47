from urllib.parse import urlparse
from urllib.parse import urljoin
import requests, re, ast, webview, os

def get_source(url):
	r = requests.get(url)
	return r.content.decode('utf-8')

def fetch(host, js_code):
	anime_name = None
	match = re.search(r'<title>(.*?)</title>', js_code)
	if match:
		anime_name = match.group(1)

	macdinh = re.search(r'var macdinh = (\d+);', js_code)
	sv_phu = re.search(r'var sv_phu = (\d+);', js_code)
	id_ep = re.search(r'var id_ep = (\d+);', js_code)

	data = {
		'ID': int(id_ep.group(1)) if id_ep else None,
		'SV': int(macdinh.group(1)) if macdinh else None,
		'SV4': int(sv_phu.group(1)) if sv_phu else None
	}

	response = requests.post(f'https://{host}/player/player.php', data=data)

	if response.status_code == 200:
		match = re.search(r'https?://.*?\.m3u8', response.text)
		if match:
			video_url = match.group(0)
			return (anime_name, video_url)
		else:
			print("Video format not supported.")
			return False
	else:
		print("Request failed:", response.status_code)
		return False

def player(anime_name, video_url, hsize, wsize):
	html_file = os.path.normpath('./player.html')
	temp_html = os.path.normpath('./temp.player.html')

	with open(html_file, 'r', encoding='utf-8') as file:
		html_content = file.read()
	html_content = html_content.replace("{{video_url}}", video_url)

	with open(temp_html, 'w', encoding='utf-8') as file:
		file.write(html_content)

	window = webview.create_window(anime_name, temp_html, width=wsize, height=hsize, resizable=True, easy_drag=True)
	webview.start()

	os.remove(temp_html)

def search(host, query):
	def search_by_query(query):
		for title, href in movie_dict.items():
			if query.lower() in title.lower():
				return {title: href}
		return None

	pattern = r'<a\s+class="movie-item\s+m-block"[^>]*\s+title="([^"]+)"\s+href="([^"]+)"[^>]*>'
	url = f'https://{host}/tim-nang-cao/?keyword={query}'
	source = get_source(url)
	matches = re.findall(pattern, source)
	movie_dict = {match[0]: match[1] for match in matches}
	result = search_by_query(query)
	if result:
		for title, href in result.items():
			return title, href
	else:
		return False

def eps(host, path):
	base = f'https://{host}/'
	url = urljoin(base, path)
	sauce = get_source(url)
	pattern = r"episodePlay\s*=\s*'([^']+)'"
	match = re.search(pattern, sauce)
	if match:
		ep1 = match.group(1)
	else:
		print("Episode not found.")
		return False
	url = urljoin(base, ep1)
	sauce = get_source(url)
	pattern = r'''<a\s+href="([^"]+)"[^>]*(?=\s+class="[^"]*(?:active\s+)?btn-episode[^"]*")[^>]*>(.*?)<\/a>'''
	episodes = {}
	matches = re.findall(pattern, sauce)
	for href, episode in matches:
		episodes[episode] = urljoin(base, href)
	return episodes