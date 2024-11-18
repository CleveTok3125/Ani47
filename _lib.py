from urllib.parse import urlparse
from urllib.parse import urljoin
import requests, re, ast, os, sys

try:
	import webview
	wv_supported = True
except:
	wv_supported = False

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
			print("This is a warning, not an error when running the program: Video format not supported.")
			return False
	else:
		print("Request failed:", response.status_code)
		return False

def player(anime_name, video_url, hsize, wsize):
	html_file = os.path.normpath('./player.html')
	temp_html = os.path.normpath('./temp.player.html')

	if os.path.exists(temp_html):
		os.remove(temp_html)

	with open(html_file, 'r', encoding='utf-8') as file:
		html_content = file.read()
	html_content = html_content.replace("{{video_url}}", video_url)
	if not wv_supported:
		html_content = html_content.replace('controlsList="nofullscreen"', '')
		html_content = html_content.replace('var isFeatureEnabled = true', 'var isFeatureEnabled = false')
		
	with open(temp_html, 'w', encoding='utf-8') as file:
		file.write(html_content)

	if wv_supported:
		window = webview.create_window(anime_name, temp_html, width=wsize, height=hsize, resizable=True, easy_drag=True)
		webview.start()
	else:
		print(f'Pywebview is not supported. Access player via "{temp_html}"')
		input('Press Enter to end session')
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
	pattern = r'''<a[^>]*\s+href="([^"]+)"[^>]*(?=\s+class="[^"]*(?:active\s+)?btn-episode[^"]*")[^>]*>(.*?)<\/a>'''
	episodes = {}
	matches = re.findall(pattern, sauce)
	for href, episode in matches:
		episodes[episode] = urljoin(base, href)
	return episodes

def clscr():
	if sys.platform == "win32":
		os.system("cls")
	else:
		os.system("clear")

def menu(items, ask=None):
	items = list(items)
	length = len(items)
	items = [f"{index}. {item}" for index, item in enumerate(items, start=1)]
	while True:
		clscr()
		if ask != None:
			print(ask)
		print('\n'.join(items))
		try:
			ans = int(input('Select one: '))
			if ans > 0 and ans <= length:
				return ans-1
			else:
				input('Invalid choice')
		except ValueError:
			input('Invalid input. Please enter a number')

def menudict(items, ask=None, presel=False):
	items = list(items.items())
	length = len(items)
	while True:
		clscr()
		if ask != None:
			print(ask)
		if presel == False:
			for i in range(length):
				key, value = items[i]
				print(f'{i+1}. Ep {key}')
		try:
			ans = int(input('Select one: ')) if presel == False else presel
			if 1 <= ans <= length:
				key, value = items[ans - 1]
				return value, ans, length
			else:
				input('Invalid choice')
		except ValueError:
			input('Invalid input. Please enter a number')

def check_connection(url):
	print('Checking connection...')
	try:
		response = requests.get(url, timeout=5)
		if response.status_code == 200:
			print("Connection successful!")
			return True
		else:
			print(f"Error: Status code {response.status_code}")
	except requests.ConnectionError:
		print("Unable to connect to the network.")
	except requests.Timeout:
		print("Connection timed out.")
	except requests.RequestException as e:
		print(f"An error occurred: {e}")
	return False
