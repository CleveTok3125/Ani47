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

	def search_anime(self):
		query = str(input('Search Anime: '))
		result = search(self.host, query)
		if result != False:
			self.title, href = result
			self.ep_list = eps(self.host, href)
			self.url, self.ep_selected, self.total_ep = menudict(ask=self.title, items=self.ep_list)
			self.url = urljoin(f'https://{self.host}/', self.url)
			js_code = get_source(self.url)
			anime_name, video_url = fetch(self.host, js_code)
			clscr()
			print('''Video player gesture instructions:
- Play/Pause: double click
- Skip forward 10s: click on the left
- Skip forward 10s: click on the right
- Skip forward 85s (skip OP/EN): click on the top
- Move window: drag the rest''')
			player(anime_name, video_url, self.hsize, self.wsize)
			self.show_actions_menu()

	def show_actions_menu(self):
		opts = menu(ask=f'{self.title}\nCurrent Episode: {self.ep_selected}', items=['Previous Episode', 'Next Episode', 'Search Anime', 'Exit'])
		if opts == 0:  # Previous
			self.previous_episode()
		elif opts == 1:  # Next
			self.next_episode()
		elif opts == 2:  # Search
			self.search_anime()
		elif opts == 3:
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
			anime_name, video_url = fetch(self.host, js_code)
			clscr()
			player(anime_name, video_url, self.hsize, self.wsize)
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
			anime_name, video_url = fetch(self.host, js_code)
			clscr()
			player(anime_name, video_url, self.hsize, self.wsize)
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
	anime_player.search_anime()

if __name__ == '__main__':
	main()
