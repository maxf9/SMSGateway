from serial.serialutil import SerialException
from binascii import hexlify
from serial import Serial

class SMSClient:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if SMSClient._instance is None:
			SMSClient._instance = object.__new__(cls)
		return SMSClient._instance

	def __init__(self, serial_port):
		self._serial_port = serial_port

	@staticmethod
	def _encode_phone_number(phone_number):
		if phone_number[0] == "+":
			phone_number = phone_number[1:]
		number_length = hexlify((len(phone_number)).to_bytes(1, byteorder="big")).upper()
		if len(phone_number) % 2 != 0:
			phone_number += "F"
		number = ""
		for i in range(0,len(phone_number),2):
			number += phone_number[i+1] + phone_number[i]
		encoded_number = number.encode()
		return (number_length, encoded_number)

	@staticmethod
	def _encode_message(message):
		encoded_message = hexlify(message.encode('utf-16-be')).decode('utf-8').upper().encode()
		message_length = hexlify((len(encoded_message) // 2).to_bytes(1, byteorder="big")).upper()
		return (message_length, encoded_message)

	@staticmethod
	def _encode_sms(phone_number, message):
		number_length, encoded_number = SMSClient._encode_phone_number(phone_number)
		message_length, encoded_message = SMSClient._encode_message(message)
		encoded_sms = b"001100" + number_length +  b"91" + encoded_number + b"0008FF" + message_length + encoded_message
		tpdu_length = len(encoded_sms[2:]) // 2
		return (tpdu_length, encoded_sms)

	def send_sms(self, phone_number, message):
		try:
			tpdu_length, encoded_sms = SMSClient._encode_sms(phone_number, message)
			com = Serial(self._serial_port)
			com.write(b'AT+CSCS="UCS2"\r')
			com.write(b"AT+CMGF=0\r")
			com.write(('AT+CMGS=' + str(tpdu_length) + '\r').encode())
			com.write(encoded_sms + bytes([26]))
		except SerialException as error:
			print("Modem Error:", error)
			return False
		com.close()
		return True
