from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from select import epoll, EPOLLIN, EPOLLOUT, EPOLLHUP
from sys import exit

class TCPServer:

	_instance = None
	_buffer = 2000

	def __new__(cls, *args, **kwargs):
		if TCPServer._instance is None:
			TCPServer._instance = object.__new__(cls)
		return TCPServer._instance

	def __init__(self, ip_address, port, application):
		self._server = TCPServer._open_socket(ip_address, port)
		self.application = application
		self._message_buffer = {}
		self._connections = {}
		self._polling = epoll()
		self._polling.register(self._server.fileno(), EPOLLIN)

	@staticmethod
	def _open_socket(ip_address, port):
		try:
			server = socket(AF_INET, SOCK_STREAM)
			server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			server.setblocking(0)
			server.bind((ip_address, port))
			server.listen(5)
		except OSError as error:
			print("TCPServer Error:", error)
			exit(1)
		return server

	def _handle_new_connection(self):
		client, address = self._server.accept()
		client.setblocking(0)
		self._connections[client.fileno()] = client
		self._message_buffer[client.fileno()] = b""
		self._polling.register(client.fileno(), EPOLLIN)

	def _handle_read(self, fileno):
		data = self._connections[fileno].recv(TCPServer._buffer)
		if data:
			self._message_buffer[fileno] = self.application.build_response(data)
			self._polling.modify(fileno, EPOLLOUT)
		else:
			self._polling.modify(fileno, 0)
			self._connections[fileno].shutdown(SHUT_RDWR)				

	def _handle_write(self, fileno):
		close_indicator, data = self._message_buffer[fileno]
		self._connections[fileno].send(data)
		if not close_indicator:
			self._polling.modify(fileno, EPOLLIN)
		else:
			self._polling.modify(fileno, 0)
			self._connections[fileno].shutdown(SHUT_RDWR)

	def _handle_close(self, fileno):
	    self._polling.unregister(fileno)
	    self._connections[fileno].close()
	    del self._connections[fileno]
	    del self._message_buffer[fileno]

	def start(self):
		while True:
			events = self._polling.poll(0.1)
			for fileno, event in events:
				if fileno == self._server.fileno():
					self._handle_new_connection()
				elif event & EPOLLIN:
					self._handle_read(fileno)
				elif event & EPOLLOUT:
					self._handle_write(fileno)
				elif event & EPOLLHUP:
					self._handle_close(fileno)
					