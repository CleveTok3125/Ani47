import re
from shutil import copy
from os import rename, remove, path

def adfilter(vtt_path):
	try:
		with open(vtt_path, 'r+', encoding='utf-8') as f:
			vtt_content = f.read()
			pattern = r"(\d{2}:)?(\d{2}:)?\d{2}\.\d{3}( )?-->( )?(\d{2}:)?(\d{2}:)?\d{2}\.\d{3}(?: .*)?\n.*anime47.*(\n+)?"
			vtt_content = re.sub(pattern, "", vtt_content)
			f.seek(0)
			f.write(vtt_content)
			f.truncate()
			return True
	except FileNotFoundError:
		return False

def backupfile(file_src):
	file_des = file_src + '.bak'
	copy(file_src, file_des)
	return file_des

def applybackup(file_src):
	file_des = file_src.removesuffix('.bak')
	if path.exists(file_src) and path.exists(file_des) and file_src != file_des:
		remove(file_des)
		rename(file_src, file_des)
		return True
	return False