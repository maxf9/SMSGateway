from parser.config_builder import ConfigBuilder
from parser.argparser import ArgParser
from jsonschema import Draft4Validator
from os.path import dirname
from sys import exit
import json

class ConfigParser:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if ConfigParser._instance is None:
			ConfigParser._instance = object.__new__(cls)
		return ConfigParser._instance

	def __init__(self):
		self._validator = ConfigValidator()
		self._config_builder = ConfigBuilder()

	def parse_config(self):
		# Получаем путь к файлу конфигурации
		config_file = ArgParser().parse_arguments()
		# Десериализация и декодирование файла конфигурации
		content = JSONWorker.fetch_content(config_file)
		# Валидация полученных настроек 
		self._validator.validate_config(content)
		# Создание объекта класса Config, содержащего настройки SMS-шлюза
		return self._config_builder.build_config(content)

class ConfigValidator:

	_schema_file = dirname(__file__) + "/config_schema.json"
	_error_basis = "Config Error: configuration file is not valid. Details: "

	def __init__(self):
		self._schema = JSONWorker.fetch_content(ConfigValidator._schema_file) 

	def validate_config(self, content):
		errors = sorted(Draft4Validator(self._schema).iter_errors(content), key=lambda e: e.path)
		if errors:
			ConfigValidator._print_errors(errors)
			exit(1)

	@staticmethod
	def _print_errors(errors):
		for error in errors:
			if len(error.path) == 0:
				print(ConfigValidator._error_basis + error.message)
			elif len(error.path) == 1 or len(error.path) == 2:
				print(ConfigValidator._error_basis + "%s in section '%s'" % (error.message, error.path[0]))
			elif len(error.path) == 3:
				print(ConfigValidator._error_basis + "%s in section '%s' property '%s'" % (error.message, error.path[0], error.path[-1]))
			else:
				print(ConfigValidator._error_basis + "%s in section '%s' property '%s'" % (error.message, error.path[0], error.path[-2]))

class JSONWorker:

	@staticmethod
	def decode_json(content):
		try:
			decoded_content = json.loads(content)
		except json.decoder.JSONDecodeError as error:
			print("Config Error: can't parse the configuration file. Details: %s" % error)
			exit(1)
		return decoded_content

	@staticmethod
	def fetch_content(file):
		file_content = FileSystem.load_from(file)
		if file_content is None:
			print("Config Error: can't load the configuration file from path '%s'. Details: file does't exist or no permission to read it" % file)
			exit(1)
		return JSONWorker.decode_json(file_content)