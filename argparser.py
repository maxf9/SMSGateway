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
		self._parser.add_argument("--ip_address", action="store", type=str, dest="ip_address", required=True)
		self._parser.add_argument("--port", action="store", type=int, dest="port", required=True)
		self._parser.add_argument("--serial_port", action="store", type=str, dest="serial_port", required=True)
		self._parser.add_argument("--system_id", action="store", type=str, default="SMSC", dest="system_id")

	def parse_arguments(self):
		namespace = self._parser.parse_args()
		return (namespace.ip_address, namespace.port, namespace.serial_port, namespace.system_id)