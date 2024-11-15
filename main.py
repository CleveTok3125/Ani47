from _lib import *
from urllib.parse import urljoin
import os, sys

def clscr():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

'''
def menu(ask, items):
	items = list(items)
	length = len(items)
	items = [f"{index}. {item}" for index, item in enumerate(items, start=1)]
	while True:
		clscr()
		print(ask)
		print('\n'.join(items))
		try:
			ans = int(input('Select one: '))
			if ans > 0 and ans <= length:
				return ans
			else:
				input('Invalid choice')
		except ValueError:
			input('Invalid input. Please enter a number')
'''

def menudict(ask, items):
    items = list(items.items())
    length = len(items)
    while True:
        clscr()
        print(ask)
        for i in range(length):
            key, value = items[i]
            print(f'{i+1}. Episode {key}')
        try:
            ans = int(input('Select one: '))
            if 1 <= ans <= length:
                key, value = items[ans - 1]
                return value
            else:
                input('Invalid choice')
        except ValueError:
            input('Invalid input. Please enter a number')

def main():
	#####################
	host = 'anime47.dev'#
	#####################
	
	query = str(input('Search anime: '))
	result = search(host, query)
	if result != False:
		title, href = result
	ep_list = eps(host, href)
	url = menudict(title, ep_list)
	url = urljoin(f'https://{host}/', url)
	js_code = get_source(url)
	anime_name, video_url = fetch(host, js_code)
	clscr()
	player(anime_name, video_url, 480, 640)

if __name__ == '__main__':
	main()