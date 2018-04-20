from smpplib.smpp import parse_pdu
from random import randint

class SMPPApplication:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if SMPPApplication._instance is None:
			SMPPApplication._instance = object.__new__(cls)
		return SMPPApplication._instance

	def __init__(self, system_id, sms_client):
		self._builder = _Builder(system_id)
		self._parser = _Parser()
		self._sms_client = sms_client

	def build_response(self, request_data):
		request = self._parser.parse_request(request_data)
		if request.command == "submit_sm":
			status = self._sms_client.send_sms(request.phone_number, request.message)
			return self._builder.build_response_from(request, status)
		return self._builder.build_response_from(request)

class _Parser:

	def parse_request(self, data):
		try:
			request = parse_pdu(data)
		except AttributeError:
			request = _Parser._parse_submit_sm(data)
		return request

	@staticmethod
	def _parse_submit_sm(data):
		command = "submit_sm"
		sequence = int.from_bytes(data[12:16], byteorder="big")
		phone_number = data[22:33].decode()
		message = data[60:].decode("utf-16-be")
		print("Get it! Phone number is %s" % phone_number)
		print("Message: %s" % message)
		return _Parser.PDU(command, sequence, phone_number, message)

	class PDU:

		def __init__(self, command, sequence, phone_number, message):
			self.command = command
			self.sequence = sequence
			self.phone_number = phone_number
			self.message = message

class _Builder:

	def __init__(self, system_id):
		self.system_id = system_id
		self._resp_makers = {"bind_transceiver" : self._make_bind_transceiver_resp,
		                     "enquire_link" : self._make_enquire_link_resp,
		                     "submit_sm" : self._make_submit_sm_resp,
		                     "unbind" : self._make_unbind_resp}

	def _make_bind_transceiver_resp(self, request):
		command_id = (2147483657).to_bytes(4, byteorder="big")
		status = (0).to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		system_id = self.system_id.encode() + b"\x00"
		length = (16 + len(system_id)).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence + system_id
		return (False, response)

	def _make_enquire_link_resp(self, request):
		command_id = (2147483669).to_bytes(4, byteorder="big")
		status = (0).to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		length = (16).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence
		return (False, response)

	def _make_submit_sm_resp(self, request, status):
		command_id = (2147483652).to_bytes(4, byteorder="big")
		status = (0 if status else 8).to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		message_id = ("mes" + str(randint(1, 10000))).encode() + b"\x00"
		length = (16 + len(message_id)).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence + message_id
		return (False, response)

	def _make_unbind_resp(self, request):
		command_id = (2147483654).to_bytes(4, byteorder="big")
		status = (0).to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		length = (16).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence
		return (True, response)

	def build_response_from(self, request, status=None):
		if status is None:
			return self._resp_makers[request.command](request)
		return self._resp_makers[request.command](request, status)