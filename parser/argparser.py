from argparse import ArgumentParser

class ArgParser:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if ArgParser._instance is None:
			ArgParser._instance = object.__new__(cls)
		return ArgParser._instance

	def __init__(self):
		self._parser = ArgumentParser()  
		self._define_args()

	def _define_args(self):
		self._parser.add_argument("-c", "--config", action="store", type=str, dest="config", required=True)

	def parse_arguments(self):
		namespace = self._parser.parse_args()
		return namespace.config