from _lib import *
from urllib.parse import urljoin
import time, os

class AnimePlayer:
	def __init__(self, host, hsize, wsize):
		self.host = host
		self.hsize = hsize
		self.wsize = wsize
		self.ep_selected = 1
		self.total_ep = 0
		self.title = ''
		self.ep_list = []
		self.code = ''
		self.anime_name = ''
		self.video_url = ''
		self.url = ''
		
	def search_anime(self):
		query = str(input('Search Anime: '))
		result = search(self.host, query)
		if result != False:
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
			js_code = get_source(self.url)
			try:
				self.anime_name, self.video_url = fetch(self.host, js_code)
			except:
				input(f'URL: {self.url}\n')
				os._exit(404)
			clscr()
			print('''Video player gesture instructions:
- Play/Pause: double click (S)
- Backward 10s: click left side (A)
- Forward 10s: click right side (D)
- Fast forward x2: Hold (1sec) right side (Hold F)
- Forward 85s (skip OP/EN): click top side (W)
- Move window: drag down side''')
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.hsize, self.wsize)
			self.show_actions_menu()

	def show_actions_menu(self):
		opts = menu(ask=f'{self.title}\nCurrent Episode: {self.ep_selected}', items=['Previous Episode', 'Next Episode', 'Replay', 'Search Anime', 'Exit'])
		if opts == 0:  # Previous
			self.previous_episode()
		elif opts == 1:  # Next
			self.next_episode()
		elif opts == 2:  # Replay
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.hsize, self.wsize)
			self.show_actions_menu()
		elif opts == 3:  # Search
			self.search_anime()
		elif opts == 4:
			os._exit(0)
		else:
			self.show_actions_menu()

	def previous_episode(self):
		if self.ep_selected == 1:
			input('No previous episode')
			self.show_actions_menu()
		else:
			self.ep_selected -= 1
			self.url, self.ep_selected, self.total_ep = menudict(ask=None, items=self.ep_list, presel=self.ep_selected)
			self.url = urljoin(f'https://{self.host}/', self.url)
			js_code = get_source(self.url)
			try:
				self.anime_name, self.video_url = fetch(self.host, js_code)
			except:
				input(f'URL: {self.url}\n')
				os._exit(404)
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.hsize, self.wsize)
			self.show_actions_menu()

	def next_episode(self):
		if self.ep_selected == self.total_ep:
			input('No next episode')
			self.show_actions_menu()
		else:
			self.ep_selected += 1
			self.url, self.ep_selected, self.total_ep = menudict(ask=None, items=self.ep_list, presel=self.ep_selected)
			self.url = urljoin(f'https://{self.host}/', self.url)
			js_code = get_source(self.url)
			try:
				self.anime_name, self.video_url = fetch(self.host, js_code)
			except:
				input(f'URL: {self.url}\n')
				os._exit(404)
			clscr()
			handle_anime_history(self.title, self.ep_list, self.ep_selected, self.code)
			player(self.anime_name, self.video_url, self.hsize, self.wsize)
			self.show_actions_menu()

def main():
	host = 'anime47.cam'
	hsize, wsize = (545, 900)

	if check_connection(f'https://{host}/'):
		time.sleep(0.5)
		clscr()
	else:
		return check_connection

	anime_player = AnimePlayer(host, hsize, wsize)
	in4 = last_viewed()
	if in4:
		print(f'''Last watched: {in4['Name']}\nEpisode: {in4['Watching']}\nTime: {in4['Time']}''')
	anime_player.search_anime()

if __name__ == '__main__':
	main()