from _lib import *
from urllib.parse import urljoin
import time

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
			player(anime_name, video_url, self.hsize, self.wsize)

	def show_actions_menu(self):
		opts = menu(ask=f'{self.title}\nCurrent Episode: {self.ep_selected}', items=['Previous Episode', 'Next Episode', 'Search Anime'])
		if opts == 0:  # Previous
			self.previous_episode()
		elif opts == 1:  # Next
			self.next_episode()
		elif opts == 2:  # Search
			self.search_anime()
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
	hsize, wsize = (480, 640)

	if check_connection(f'https://{host}/'):
		time.sleep(0.5)
		clscr()
	else:
		return check_connection

	anime_player = AnimePlayer(host, hsize, wsize)
	anime_player.search_anime()
	anime_player.show_actions_menu()


if __name__ == '__main__':
	main()
