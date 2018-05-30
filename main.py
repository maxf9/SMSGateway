#!/usr/bin/env python3
from parser.config_parser import ConfigParser
from application.smpp_core import SMPPApplication
from application.sms_worker import SMSWorker
from file_system import FileSystem
from network import TCPServer
from signal import signal, SIGINT
from logger import Logger
from sys import exit
import os

# Добавление статического класса файловой системы в пространство имен __builtins__
setattr(__builtins__, 'FileSystem', FileSystem)
setattr(__builtins__, 'Logger', Logger)

def main():

	def signal_handler(signal, frame):
		tcp_server.stop()
		Logger.warning("Server was immediately stopped")
		exit(1)

	# Установка трапа на обработку SIGINT
	signal(SIGINT, signal_handler)
	# Загрузка и чтение настроек из файла конфигурациии
	config = ConfigParser().parse_config()
	Logger.info("Сonfig was successfully created")
	# Создание и настройка SMS клиента для работы с адаптером 3G/GSM
	sms_worker = SMSWorker(config.gw_settings.sms_adapter)
	# Создание и настройка приложения SMPP для обмена служебными сообщениями с WLC
	smpp = SMPPApplication(config.gw_settings.smpp, config.auth_base, sms_worker)
	# Создание и настройка асинхронного TCP-сервера
	tcp_server = TCPServer(config.gw_settings.network, application=smpp)
	# Запуск TCP-сервера
	Logger.info("Start serving")
	tcp_server.start()

if __name__ == "__main__":
	main()