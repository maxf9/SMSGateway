from application.smpp_builder import SMPPBuilder
from application.smpp_parser import SMPPParser

class SMPPApplication:

	_instance = None

	def __new__(cls, *args, **kwargs):
		if SMPPApplication._instance is None:
			SMPPApplication._instance = object.__new__(cls)
		return SMPPApplication._instance

	def __init__(self, smpp_config, auth_base, sms_worker):
		self._builder = SMPPBuilder(smpp_config.system_id)
		self._parser = SMPPParser()
		self._sms_worker = sms_worker
		self._auth_base = auth_base
		self._registered = {}
		self._actions = self.define_actions()

	def define_actions(self):
		return {
		    "bind_transceiver" : self._take_bind_transceiver_action,
		    "enquire_link" : self._take_enquire_link_action,
		    "submit_sm" : self._take_sumit_sm_action,
		    "unbind" : self._take_unbind_action
		}

	def deregister_address(self, address):
		if address in self._registered:
			del self._registered[address]

	def _take_bind_transceiver_action(self, request, address):
		if request.parsed_status != 0:
			return request.parsed_status
		if request.system_id in self._auth_base:
			if request.password == self._auth_base[request.system_id]:
				self._registered[address] = request.system_id
				return 0  # OK
			return 13     # Bind failed
		return 13

	def _take_enquire_link_action(self, request, address):
		if request.parsed_status != 0:
			return request.parsed_status
		if address not in self._registered:
			return 13
		return 0

	def _take_sumit_sm_action(self, request, address):
		if request.parsed_status != 0:
			return request.parsed_status
		if address not in self._registered:
			return 13
		return self._sms_worker.send_sms(request.phone_number, request.encoding, request.message)

	def _take_unbind_action(self, request, address):
		if request.parsed_status != 0:
			return request.parsed_status
		if address not in self._registered:
			return 13
		del self._registered[address]
		return 0

	def build_response(self, request_data, address):
		request = self._parser.parse_request(request_data)
		if request is None:
			return
		response_status = self._actions[request.command](request, address)
		return self._builder.build_response_from(request, response_status)