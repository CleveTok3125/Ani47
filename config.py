import configparser, re

class Config:
	def __init__(self, config_file='config.ini'):
		self.config_file = config_file
		self.parser = configparser.ConfigParser()
		self.parser.read(self.config_file)

	def get(self, key, section='DEFAULT'):
		return self.parser.get(section, key)

	def get_bool(self, key, section='DEFAULT'):
		return self.parser.getboolean(section, key)

	def get_int(self, key, section='DEFAULT'):
		return self.parser.getint(section, key)

	def update_config(self, key, value, section='DEFAULT'):
		# Why not use parser? Because I want to keep the comments in the config file
		key, value, section = list(map(str, (key, value, section)))

		section_pattern = rf"\[{section}\]([\s\S.]*)"
		key_pattern = rf"({key}\s+=\s+)(.+)"

		with open(self.config_file, 'r+', encoding='utf-8') as file:
			content = file.read()

			section_match = re.search(section_pattern, content, re.IGNORECASE)
			
			if section_match:
				section_content = section_match.group(1)
				key_match = re.search(key_pattern, section_content, re.IGNORECASE)

				if key_match:
					content = content.replace(key_match.group(0), f"{key} = {value}")
				else:
					content = content.replace(section_content, f"{section_content}\n{key} = {value}")
			else:
				content += f"\n[{section}]\n{key} = {value}"

			file.seek(0)
			file.write(content)
			file.truncate()