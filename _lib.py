from urllib.parse import urljoin, urlparse
from datetime import datetime
from copy import deepcopy
from time import sleep
import re, os, sys, json, threading

import requests
# import webview

from config import Config
from server import *
from vtt_tools import *

_config = Config()

def get_source(url):
	r = requests.get(url)
	try:
		return r.content.decode('utf-8')
	except UnicodeDecodeError:
		return r.text

def fetch(host, js_code):
	debug = _config.get_bool('DEBUG')
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
		response_text = response.content.decode('utf-8')
		
		sources = re.search(r'"sources":\s*(\[[^\]]*\])', response_text)
		tracks = re.search(r'tracks:\s*(\[[^\]]*\])', response_text)

		return_tracks = False
		if tracks != None:
			tracks = tracks.group(1)
			tracks = re.sub(r"([a-zA-Z0-9_]+):", r'"\1":', tracks)
			tracks = json.loads(tracks)
			if len(tracks) != 0:
				for track in tracks:
					track['file'] = urljoin(f'https://{host}', track['file'])
				# [{'file': 'https://{host}/subtitle/en.vtt', 'label': 'English', 'kind': 'subtitles', 'default': False}, {'file': 'https://{host}/subtitles/vi.vtt', 'label': 'Tiếng Việt', 'kind': 'subtitles', 'default': True}]
				return_tracks = True

		sources = json.loads(sources.group(1))
		sources = sources[0]

		if sources['type'] == 'hls':
			video_url = sources['file']
			return (anime_name, video_url, tracks if return_tracks else False)
		else:
			print("Video format not supported.")
			if debug:
				return response_text
			return False
	else:
		print("Request failed:", response.status_code)
		return False

class PLAYER:
	def __init__(self):
		abs_path = os.path.dirname(os.path.abspath(__file__))
		self.wv_supported = _config.get_bool('PYWEBVIEW')
		self.html_file = os.path.join(abs_path, './player.html') # main, lib and player must be in the same directory
		self.temp_html = os.path.normpath('./index.html')
		self.subtitles_path = os.path.normpath('./subtitles/')
		self.delete_subtitles = []
		
		if self.wv_supported:
			try:
				import webview
				self.webview = webview
			except ModuleNotFoundError:
				self.wv_supported = False

	def clean_cache(self):
		if os.path.exists(self.temp_html):
			def force_remove():
				try:
					os.remove(self.temp_html)
				except OSError as e:
					input(f'Please close all {os.path.join(os.getcwd(), self.temp_html)} related tasks.\n{e}\n')
					force_remove()

	def create_sub_path(self):
		if not os.path.exists(self.subtitles_path):
			os.mkdir(self.subtitles_path)

	def clean_session_cache(self):
		if os.path.exists(self.temp_html):
			os.remove(self.temp_html)
		for file in self.delete_subtitles:
			if os.path.exists(file):
				os.remove(file)

	def download_subtitles(self, track_lst_copy):
		# Download subtitles to avoid CORS
		for track in track_lst_copy:
			url = track['file']
			name = url.split('/')[-1]
			subtitles_file = os.path.join(os.getcwd(), self.subtitles_path, name)
			response = requests.get(url)
			with open(subtitles_file, 'wb') as f:
				f.write(response.content)
			self.delete_subtitles.append(subtitles_file)
			track['file'] = os.path.join('./', self.subtitles_path, name).replace('\\', '/')

		track_lst_copy = json.dumps(track_lst_copy)
		return track_lst_copy

	def create_html(self, track_lst_copy, video_url):
		with open(self.html_file, 'r', encoding='utf-8') as file:
			html_content = file.read()

		html_content = html_content.replace("{{video_url}}", video_url)

		if track_lst_copy == False:
			html_content = html_content.replace("{{track_lst}}", 'false')
		else:
			track_lst_copy = self.download_subtitles(track_lst_copy)
			html_content = html_content.replace("{{track_lst}}", track_lst_copy)

			# vtt-tools plugins here
			VTTplugins(self).apply_plugins()

		if (not self.wv_supported) and (not _config.get_bool('FORCE_GESTURE')):
			html_content = html_content.replace('controlsList="nofullscreen"', '')
			html_content = html_content.replace('var isFeatureEnabled = true', 'var isFeatureEnabled = false')
			
		with open(self.temp_html, 'w', encoding='utf-8') as file:
			file.write(html_content)

	def start_player(self, anime_name, hsize, wsize):
		PORT = _config.get('PORT')
		match = re.match(r"randint\(\s*(\d+)\s*,\s*(\d+)\s*\)", PORT)
		if match:
			from random import randint
			PORT = randint(int(match.group(1)), int(match.group(2)))
		else:
			PORT = int(PORT)
		share = _config.get_bool('LOCAL_SHARE')
		if not self.wv_supported:
			print('Pywebview is not supported.')

		if self.wv_supported:
			local_url = urljoin(f'http://127.0.0.1:{PORT}/', self.temp_html)
			server_thread = threading.Thread(target=lambda: start_server(PORT=PORT, share=share))
			server_thread.daemon = True
			self.webview.create_window(anime_name, local_url, width=wsize, height=hsize, resizable=True, easy_drag=True)

			server_thread.start()
			self.webview.start(debug=_config.get_bool('DEBUG'))
		else:
			print('Local server is running... (CTRL-C to stop)')
			try:
				start_server(PORT=PORT, share=share)
			except KeyboardInterrupt:
				pass

	def player(self, anime_name, video_url, track_lst, hsize, wsize):
		print(f'Playing {anime_name}...')

		# Work with copies to avoid changing the original
		track_lst_copy = deepcopy(track_lst)
		
		self.clean_cache()
		self.create_sub_path()

		self.create_html(track_lst_copy, video_url)

		self.start_player(anime_name, hsize, wsize)
		self.clean_session_cache()

	def openINwebview(self, url, anime_name, hsize, wsize):
		self.clean_session_cache()
		html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="refresh" content="0;url={url}">
	<title>Redirecting...</title>
</head>
<body>
	<p>If you are not redirected, <a href="{url}">click here</a>.</p>
</body>
</html>"""
		with open(self.temp_html, 'w', encoding='utf-8') as file:
			file.write(html_content)

		self.start_player(anime_name, hsize, wsize)
		self.clean_session_cache()

class VTTplugins:
	def __init__(self, Player):
		self.Player = Player
		self.plugins = [self.safe_adfilter]

	def apply_plugins(self):
		for plugin in self.plugins:
			plugin()

	def safe_adfilter(self):
		if _config.get_bool('ADFILTER'):
			for file in self.Player.delete_subtitles:
				bak_file = backupfile(file)
				if adfilter(bak_file):
					applybackup(bak_file)

def search(host, query):
	def search_by_query(query, movie_dict):
		result = {title: href for title, href in movie_dict.items() if query.lower() in title.lower()}
		return result

	pattern = r'<a\s+class="movie-item\s+m-block"[^>]*\s+title="([^"]+)"\s+href="([^"]+)"[^>]*>'
	url = f'https://{host}/tim-nang-cao/?keyword={query}'
	source = get_source(url)
	matches = re.findall(pattern, source)
	movie_dict = {match[0]: match[1] for match in matches}
	result = search_by_query(query, movie_dict)
	if result:
		return result
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
	li_items = re.findall(r'<li><a.*?<\/a><\/li>', sauce, re.DOTALL)
	pattern = r'''<a[^>]*\s+href="([^"]+)"[^>]*(?=\s+class="[^"]*(?:active\s+)?btn-episode[^"]*")[^>]*>(.*?)<\/a>'''
	episodes = {}
	matches = {}
	for li in li_items:
		match = re.findall(pattern, li)
		if match:
			if len(match) != 0:
				match = match[0]
				matches[match[0]] = match[1]
	for href, episode in matches.items():
		ep_id = href.split('/')[-1].split('.')[0]
		episodes[f'{episode} - {ep_id}'] = urljoin(base, href)
	return episodes

def clscr():
	if sys.platform == "win32":
		os.system("cls")
	else:
		os.system("clear")

def exit(n=0):
	return os._exit(n)

def which():
	return os.getcwd(), os.path.dirname(os.path.abspath(__file__))

def where():
	return which()

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

def menudict(items, ask=None, presel=False, default='Ep ', reback=True):
	items = list(items.items())
	length = len(items)
	while True:
		clscr()
		if ask != None:
			print(ask)
		if presel == False:
			if reback == True:
				print('0. Back')
			for i in range(length):
				key, value = items[i]
				print(f'{i+1}. {default}{key}')
		try:
			ans = int(input('Select one: ')) if presel == False else presel
			if 1 <= ans <= length:
				key, value = items[ans - 1]
				return value, ans, length
			elif ans == 0 and reback == True:
				return value, -1, length
			else:
				input('Invalid choice')
		except ValueError:
			input('Invalid input. Please enter a number')

def check_connection(url, backup=False):
	bak_host = _config.get('BACKUP_HOST')
	redirect = _config.get_bool('REDIRECT')

	print('Checking connection...')
	try:
		if backup >= 2:
			bak_host = False
		if bak_host and redirect:
			url = bak_host
			print('Using BACKUP_HOST...')

		response = requests.get(url, timeout=5, allow_redirects=redirect)
		
		if response.status_code == 200:
			print("Connection successful!")

			if not redirect:
				return True
			
			original_domain = urlparse(url).netloc
			final_domain = urlparse(response.url).netloc

			if original_domain != final_domain and 'anime47' in str(final_domain):
				_config.update_config('HOST', str(final_domain))
				print(f'Redirected to new domain {final_domain}.\nUpdated in configuration file.')
				sleep(2.5)
			elif 'anime47' not in str(final_domain):
				print('The redirected domain is suspicious.')
				print(f'Check "{final_domain}" and update manually via configuration file if it is valid.')
				print('Change the "REDIRECT" configuration to "False" if you do not want to change the HOST')
				sleep(4.5)
				return False
			return True
		else:
			print(f"Error: Status code {response.status_code}")
	except requests.ConnectionError:
		print("Unable to connect to the network.")
		
		if bak_host and backup < 2 and redirect:
			backup += 1
			check_connection(url, backup=backup)

	except requests.Timeout:
		print("Connection timed out.")
	except requests.RequestException as e:
		print(f"An error occurred: {e}")
	return False

class HistoryHandler:
	def __init__(self):
		self.filename = os.path.normpath("./history.json")

	def handle_anime_history(self, anime_name, ep_list, ep_selected, code):
		if not _config.get_bool('HISTORY'):
			return 'History is disabled'

		ep_list = list(ep_list.keys())
		watching = ep_list[ep_selected - 1]
		
		try:
			with open(self.filename, "r", encoding="utf-8") as file:
				anime_dict = json.load(file)
		except FileNotFoundError:
			anime_dict = {}

		existing_anime = next((anime for anime in anime_dict.values() if anime["Code"] == code), None)

		if existing_anime is None:
			anime_info = {
				"Name": anime_name,
				"Code": code,
				"Watching": watching,
				"Episodes": ep_list,
				"Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			}
			anime_dict[len(anime_dict)] = anime_info
		else:
			if existing_anime["Watching"] != watching:
				existing_anime["Watching"] = watching
			existing_anime["Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		with open(self.filename, "w", encoding="utf-8") as file:
			json.dump(anime_dict, file, ensure_ascii=False, indent=4)

	def get_watching_status(self, code):
		anime_dict = self.read_history()
		if anime_dict != None:
			for anime in anime_dict.values():
				if anime["Code"] == code:
					return anime["Watching"]
		return None

	def last_viewed(self):
		anime_data = self.read_history()
		if anime_data != None:
			max_index = max(anime_data.values(), key=lambda x: datetime.strptime(x["Time"], "%Y-%m-%d %H:%M:%S"))
			return max_index
		return None

	def read_history(self):
		try:
			with open(self.filename, "r", encoding="utf-8") as file:
				anime_dict = json.load(file)
			return anime_dict
		except FileNotFoundError:
			return None

	def delete_history(self):
		if os.path.exists(self.filename):
			os.remove(self.filename)

def ClearAllCache(custom_delete=[]):
	PLAYER().clean_session_cache()
	os.rmdir(PLAYER().subtitles_path)
	HistoryHandler().delete_history()
	for file in custom_delete:
		if os.path.exists(file):
			os.remove(file)