from random import randint

class SMPPBuilder:

	def __init__(self, system_id):
		self.system_id = system_id
		self._response_makers = self.define_response_makers()

	def define_response_makers(self):
		return {
		    "bind_transceiver" : self._make_bind_transceiver_resp,
		    "enquire_link" : self._make_enquire_link_resp,
		    "submit_sm" : self._make_submit_sm_resp,
		    "unbind" : self._make_unbind_resp
		}

	def _make_bind_transceiver_resp(self, request, response_status):
		command_id = (2147483657).to_bytes(4, byteorder="big")
		status = response_status.to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		system_id = self.system_id.encode() + b"\x00"
		length = (16 + len(system_id)).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence + system_id
		if response_status != 0:
			return (True, response)
		return (False, response)

	def _make_enquire_link_resp(self, request, response_status):
		command_id = (2147483669).to_bytes(4, byteorder="big")
		status = response_status.to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		length = (16).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence
		if response_status != 0:
			return (True, response)
		return (False, response)

	def _make_submit_sm_resp(self, request, response_status):
		command_id = (2147483652).to_bytes(4, byteorder="big")
		status = response_status.to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		if response_status == 0:
			message_id = ("mes" + str(randint(1, 10000))).encode() + b"\x00"
			close_indicator = False
		else:
			message_id = b""
			close_indicator = True
		length = (16 + len(message_id)).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence + message_id
		return (close_indicator, response)

	def _make_unbind_resp(self, request, response_status):
		command_id = (2147483654).to_bytes(4, byteorder="big")
		status = response_status.to_bytes(4, byteorder="big")
		sequence = request.sequence.to_bytes(4, byteorder="big")
		length = (16).to_bytes(4, byteorder="big")
		response = length + command_id + status + sequence
		return (True, response)

	def build_response_from(self, request, response_status):
		return self._response_makers[request.command](request, response_status)