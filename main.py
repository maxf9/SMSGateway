#!/usr/bin/env python3
from parser.config_parser import ConfigParser
from file_system import FileSystem
from smpp import SMPPApplication
from sms_worker import SMSWorker
from network import TCPServer
from signal import signal, SIGINT
from sys import exit
import os

# Добавление статического класса файловой системы в пространство имен __builtins__
setattr(__builtins__, 'FileSystem', FileSystem)

def main():

	def signal_handler(signal, frame):
		print("Stop working")
		tcp_server.stop()
		exit(1)

	# Установка трапа на обработку SIGINT
	signal(SIGINT, signal_handler)
	# Загрузка и чтение настроек из файла конфигурациии
	config = ConfigParser().parse_config()
	# Создание и настройка SMS клиента для работы с адаптером 3G/GSM
	sms_worker = SMSWorker(config.gw_settings.sms_adapter)
	# Создание и настройка приложения SMPP для обмена служебными сообщениями с WLC
	smpp = SMPPApplication(config.gw_settings.smpp, config.auth_base, sms_worker)
	# Создание и настройка асинхронного TCP-сервера
	tcp_server = TCPServer(config.gw_settings.network, application=smpp)
	# Запуск TCP-сервера
	tcp_server.start()

if __name__ == "__main__":
	main()