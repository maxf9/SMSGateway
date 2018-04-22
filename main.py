#!/usr/bin/env python3
from parser.config_parser import ConfigParser
from file_system import FileSystem
from smpp import SMPPApplication
from sms_worker import SMSWorker
from network import TCPServer

# Добавление статического класса файловой системы в пространство имен __builtins__
setattr(__builtins__, 'FileSystem', FileSystem)

def main():
	# Загрузка и чтение настроек из файла конфигурациии
    config = ConfigParser().parse_config()
    # Создание и настройка SMS клиента для работы с адаптером 3G/GSM 
    sms_worker = SMSWorker(config.gw_settings.sms_adapter)
    # Создание и настройка приложения SMPP для обмена служебными сообщениями с WLC
    smpp = SMPPApplication(config.gw_settings.smpp, config.auth_base, sms_worker)
    # Создание, настройка и запуск асинхронного TCP-сервера
    TCPServer(config.gw_settings.network, application=smpp).start()

if __name__ == "__main__":
	main()