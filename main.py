from _lib import *
from urllib.parse import urljoin
import time, os, logging
from config import Config

def pre_action(func):
	def wrapper(self, *args, **kwargs):
		self.log_info()
		return func(self, *args, **kwargs)
	return wrapper

class AnimePlayer:
	def __init__(self, host, hsize, wsize, debug):
		self.host = host
		self.hsize = hsize
		self.wsize = wsize
		self.debug = debug
		self.ep_selected = 1
		self.total_ep = 0
		self.title = ''
		self.ep_list = []
		self.code = ''
		self.anime_name = ''
		self.video_url = ''
		self.track_lst = False
		self.url = ''
		self.js_code = ''

	def log_info(self, custom_message="", custom_title=""):
		if self.debug:
			logging.basicConfig(filename='anime_player.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
			logging.debug("\n" + "="*50)
			logging.debug("Host: %s", self.host)
			logging.debug("Hsize: %s", self.hsize)
			logging.debug("Wsize: %s", self.wsize)
			logging.debug("Debug: %s", self.debug)
			logging.debug("Ep Selected: %d", self.ep_selected)
			logging.debug("Total Ep: %d", self.total_ep)
			logging.debug("Title: %s", self.title)
			logging.debug("Ep List: %s", self.ep_list)
			logging.debug("Code: %s", self.code)
			logging.debug("Anime Name: %s", self.anime_name)
			logging.debug("Video URL: %s", self.video_url)
			logging.debug("Tracks list: %s", self.track_lst)
			logging.debug("URL: %s", self.url)
			#logging.debug("JS Code: %s", self.js_code)

			if custom_message:
				logging.debug(f"{custom_title}\n### BEGIN CODE ###\n{custom_message}\n### END CODE ###")

	@pre_action
	def get_info(self):
		try:
			response = fetch(self.host, self.js_code)
			if response == False:
				raise ValueError(404)
			if type(response) != bool:
				self.log_info(response, "Data returned from fetch():")
			self.anime_name, self.video_url, self.track_lst = response
		except Exception as e:
			input(f'URL: {self.url}\n{e}\n')
			os._exit(404)

	@pre_action
	def search_anime(self):
		query = str(input('Search Anime: '))
		self.log_info()
		result = search(self.host, query)
		if result != False:
			if len(result) == 1:
			  self.title, href = next(iter(result.items()))
			else:
				href, self.title, _ = menudict(items=result, default='')
				if self.title == -1:
				  clscr()
				  self.search_anime()
				self.title = list(result.keys())[self.title-1]
			self.code = href.split('/')[-1].split('.')[0]
			self.ep_list = eps(self.host, href)
			watched = get_watching_status(self.code)
			self.url, self.ep_selected, self.total_ep = menudict(ask=f'{self.title}\nLast watched episode: {watched}' if watched != None else self.title, items=self.ep_list)
			if self.ep_selected == -1:
				clscr()
				self.search_anime()
			self.url = urljoin(f'https://{self.host}/', self.url)
			self.js_code = get_source(self.url)
			self.get_info()
			clscr()
			print('''Video player gesture instructions:
- Play/Pause: double click (S)
- Backward 10s: click left side (A)
- Forward 10s: click right side (D)
- Fast forward x2: Hold (1sec) right side (Hold F)
- Forward 85s (skip OP/EN): click top side (W)
- Move window: drag down side''')
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.track_lst, self.hsize, self.wsize)
			self.show_actions_menu()
		else:
			print('Anime not found.')
			self.search_anime()
		self.log_info()

	@pre_action
	def show_actions_menu(self):
		self.log_info()
		opts = menu(ask=f'{self.title}\nCurrent Episode: {self.ep_selected} ({get_watching_status(self.code)})', items=['Next Episode', 'Previous Episode', 'Replay', 'Search Anime', 'Exit'])
		if opts == 0:  # Next
			self.next_episode()
		elif opts == 1:  # Previous
			self.previous_episode()
		elif opts == 2:  # Replay
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.track_lst, self.hsize, self.wsize)
			self.show_actions_menu()
		elif opts == 3:  # Search
			self.search_anime()
		elif opts == 4:
			os._exit(0)
		else:
			self.show_actions_menu()

	@pre_action
	def previous_episode(self):
		if self.ep_selected == 1:
			input('No previous episode')
			self.show_actions_menu()
		else:
			self.ep_selected -= 1
			self.url, self.ep_selected, self.total_ep = menudict(ask=None, items=self.ep_list, presel=self.ep_selected)
			self.url = urljoin(f'https://{self.host}/', self.url)
			self.js_code = get_source(self.url)
			self.get_info()
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.track_lst, self.hsize, self.wsize)
			self.show_actions_menu()

	@pre_action
	def next_episode(self):
		if self.ep_selected == self.total_ep:
			input('No next episode')
			self.show_actions_menu()
		else:
			self.ep_selected += 1
			self.url, self.ep_selected, self.total_ep = menudict(ask=None, items=self.ep_list, presel=self.ep_selected)
			self.url = urljoin(f'https://{self.host}/', self.url)
			self.js_code = get_source(self.url)
			self.get_info()
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.track_lst, self.hsize, self.wsize)
			self.show_actions_menu()

def main():
	config = Config()
	host = config.get('HOST')
	hsize = config.get_int('HSIZE')
	wsize = config.get_int('WSIZE')
	debug = config.get_bool('DEBUG')

	if check_connection(f'https://{host}/'):
		time.sleep(0.5)
		clscr()
	else:
		return check_connection

	anime_player = AnimePlayer(host, hsize, wsize, debug=debug)
	in4 = last_viewed()
	if in4:
		print(f'''Last watched: {in4['Name']}\nEpisode: {in4['Watching']}\nTime: {in4['Time']}''')
	anime_player.search_anime()
	logging.shutdown()

if __name__ == '__main__':
	main()
