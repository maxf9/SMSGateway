# SMSGateway
Простая реализация SMS-шлюза на Python3 для взаимодействия с продуктом Eltex SoftWLC.
# Установка зависимостей
```
pip3 install pyserial jsonschema
```
# Запуск сервера
Для запуска сервера требуется запустить файл main.py с конфигурационным файлом формата json:

```
./main.py -c config_file.json
``` 
или
```
./main.py --config config_file.json
```
# Структура конфигурационного файла
Пример конфигурационного файла для запуска сервера:

```

	"GatewaySettings" : {
		"Network" : {
			"ip_address" : "172.16.0.112",
			"port" : 3700,
			"listen_backlog" : 5
		},
		"SMPP" : {
			"system_id" : "SMSGW"
		},
		"MobileAdapter" : {
			"serial_port" : "/dev/ttyUSB0",
			"baudrate" : 9600,
			"data_bits" : 8,
			"stop_bits" : 1,
			"parity" : "None",
			"flow_control" : "None"
		}
	},
	"AuthBase" : {
		"test" : "test" 
	}
```

Содержимое конфигурационного файла записывается в формате JSON. Файл имеет две обязательных секции:

1. GatewaySettings - здесь описываются настройки компонентов сервера SMSGateway. В данную секцию входит 3 обязательных подсекции:

   + Network - содержит параметры TCP-сервера: 

     - **ip_address** и **port** - ip-адрес и порт, на которых открывается слушающий сокет TCP-сервера;
     - listen_backlog - длина очереди подключений, значение по умолчанию: 0.

   + SMPP - содержит параметры протокола SMPP:

     - **system_id** - идентификатор SMS-шлюза, который используется в сообщениях BindTransceiver протокола SMPP.

   + MobileAdapter - содержит параметры подключения по COM-порту к адаптеру мобильной сети:

     - **serial_port** - путь к файлу COM-порта;

     - baudrate - скорость подключения. По умолчанию 9600 бит/с;

     - data_bits - количество информационных битов. Принимает значения 5, 6, 7, 8. По умолчанию 8;

     - stop_bits - количество стоповых битов. Принимает значения 1, 1.5, 2. По умолчанию 1;

     - parity - контроль четности. Принимает значения "None", "Even", "Odd", "Mark", "Space". По умолчанию "None";

     - flow_control - контроль потока. Принимает значения "None", "XON/XOFF", "RTS/CTS", "DSR/DTR". По умолчанию "None".

2. AuthBase - словарь логинов и паролей пользователей SMS-шлюза.

**Все обязательные параметры секций выделены жирным шрифтом.**
