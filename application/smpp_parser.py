from re import match

class SMPPParser:

	_command_ids = {
		4 : "submit_sm",
	    6 : "unbind",
	    9 : "bind_transceiver",
	    21 : "enquire_link"
	}

	def __init__(self):
		self._parse_handlers = {
		   "bind_transceiver" : self._parse_bind_transceiver,
		   "enquire_link" : self._parse_enquire_link,
		   "submit_sm" : self._parse_submit_sm,
		   "unbind" : self._parse_unbind
		}

	@staticmethod
	def is_valid_phone_number(phone_number):
		if match(r"\d{11}", phone_number):
			return True
		else:
			return False

	def parse_request(self, data):
		try:
			command = SMPPParser._command_ids[int.from_bytes(data[4:8], byteorder="big")]
		except KeyError:
			return
		sequence = int.from_bytes(data[12:16], byteorder="big")
		return self._parse_handlers[command](sequence, data[16:])

	def _get_Coctet_string(byte_string, max_length):
		number = 0
		while number < max_length:
			try:
				if byte_string[number] == 0:
					return (number + 1, byte_string[:number])
				number += 1
			except IndexError:
				return
		return

	def _parse_bind_transceiver(self, sequence, data):
		request = BindTransceiver(sequence)
		result = SMPPParser._get_Coctet_string(data, max_length=16)
		if result:
			data = data[result[0]:]
			request.system_id = result[1].decode()
		else:
			request.parsed_status = 15  # Invalid system_id
			return request
		result = SMPPParser._get_Coctet_string(data, max_length=9)
		if result:
			data = data[result[0]:]
			request.password = result[1].decode()
		else:
			request.parsed_status = 14  # Invalid password
			return request
		return request

	def _parse_enquire_link(self, sequence, data):
		request = EnquireLink(sequence)
		return request

	def _parse_submit_sm(self, sequence, data):
		request = SubmitSM(sequence)
		phone_number = data[6:17].decode()
		if SMPPParser.is_valid_phone_number(phone_number):
			request.phone_number = phone_number
		else:
			request.parsed_status = 11   # Invalid Dest Addr
			return request
		request.encoding = int.from_bytes(data[41:42], byteorder="big")
		request.message = data[44:].decode("utf-16-be")
		Logger.info("Request for number %s\nMessage: %s" % (request.phone_number, request.message))
		return request

	def _parse_unbind(self, sequence, data):
		request = Unbind(sequence)
		return request

class PDU:

	def __init__(self, command, sequence):
		self.command = command
		self.sequence = sequence
		self.parsed_status = 0

class BindTransceiver(PDU):
	
	def __init__(self, sequence):
		super().__init__("bind_transceiver", sequence)
		self.system_id = None
		self.password = None

class EnquireLink(PDU):
	
	def __init__(self, sequence):
		super().__init__("enquire_link", sequence)

class SubmitSM(PDU):
	
	def __init__(self, sequence):
		super().__init__("submit_sm", sequence)
		self.phone_number = None
		self.encoding = None
		self.message = None

class Unbind(PDU):
	
	def __init__(self, sequence):
		super().__init__("unbind", sequence)