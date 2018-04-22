from os import access, R_OK
from os.path import isfile

class FileSystem:

	@staticmethod
	def load_from(file):
		if isfile(file) and access(file, R_OK):
			with open(file, "r", encoding="utf-8") as f:
				content = f.read()
				return content