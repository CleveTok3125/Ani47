import configparser

class Config:
	def __init__(self, config_file='config.ini'):
		self.parser = configparser.ConfigParser()
		self.parser.read(config_file)

	def get(self, key, section='DEFAULT'):
		return self.parser.get(section, key)

	def get_bool(self, key, section='DEFAULT'):
		return self.parser.getboolean(section, key)

	def get_int(self, key, section='DEFAULT'):
		return self.parser.getint(section, key)
