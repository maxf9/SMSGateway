from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE

class ConfigBuilder:

	_instance = None
	_parity_definitions = {
	    "None" : PARITY_NONE,
		"Even" : PARITY_EVEN,
		"Odd" : PARITY_ODD,
		"Mark" : PARITY_MARK,
		"Space" : PARITY_SPACE
    }

	def __new__(cls, *args, **kwargs):
		if ConfigBuilder._instance is None:
			ConfigBuilder._instance = object.__new__(cls)
		return ConfigBuilder._instance

	def __init__(self):
		self._config = Config()               
		self._makers = self._define_makers()

	def _define_makers(self):
		return {"GatewaySettings" : self._make_gw_settings,
		        "AuthBase" : self._make_auth_base}

	def _make_gw_settings(self, sample):
		gw_settings = Config.GatewaySettings()
		gw_settings.network = ConfigBuilder._build_network(sample["Network"])
		gw_settings.smpp = ConfigBuilder._build_smpp(sample["SMPP"])
		gw_settings.sms_adapter = ConfigBuilder._build_mobile_adapter(sample["MobileAdapter"])
		self._config.gw_settings = gw_settings

	@staticmethod
	def _build_network(fabric):
		network = Config.Network(fabric["ip_address"], fabric["port"])
		if "listen_backlog" in fabric:
			network.listen_backlog = fabric["listen_backlog"]
		return network

	@staticmethod
	def _build_smpp(fabric):
		smpp = Config.SMPP(fabric["system_id"])
		return smpp

	@staticmethod
	def _build_mobile_adapter(fabric):
		sms_adapter = Config.MobileAdapter(fabric["serial_port"])
		for field in ("baudrate", "data_bits", "stop_bits", "parity", "flow_control"):
			try:
				if field == "baudrate":
					sms_adapter.baudrate = fabric[field]
				elif field == "data_bits":
					sms_adapter.data_bits = fabric[field]
				elif field == "stop_bits":
					sms_adapter.stop_bits = fabric[field]
				elif field == "parity":
					sms_adapter.parity = ConfigBuilder._parity_definitions[fabric[field]]
				elif field == "flow_control":
					sms_adapter.flow_control = fabric[field]
			except KeyError:
				pass
		return sms_adapter

	def _make_auth_base(self, sample):
		self._config.auth_base = sample

	def build_config(self, content):
		for component in content:
			self._makers[component](content[component])
		return self._config

class Config:

	def __init__(self):
		self.gw_settings = None
		self.auth_base = None

	class GatewaySettings:

		def __init__(self):
			self.network = None
			self.smpp = None
			self.sms_adapter = None

	class Network:
		
		def __init__(self, ip_address, port):
			self.ip_address = ip_address
			self.port = port
			self.listen_backlog = 0

	class SMPP:
		
		def __init__(self, system_id):
			self.system_id = system_id

	class MobileAdapter:
		
		def __init__(self, serial_port):
			self.serial_port = serial_port
			self.baudrate = 9600
			self.data_bits = 8
			self.stop_bits = 1
			self.parity = PARITY_NONE
			self.flow_control = "None"