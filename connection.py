import errno
import socket

socket.setdefaulttimeout(10)

class Connection:
	def __init__(self):
		self.socket = None
		self.last_buf = None
		self.debug = False

	def send(self, *data):
		line = ' '.join(data) + '\r\n'
		if self.debug: print('->', line, end='')
		self.socket.sendall(bytes(line, 'utf-8'))

	def recv(self):
		data = self.socket.recv(4096)
		if self.last_buf is not None:
			data = self.last_buf + data
			self.last_buf = None
		lines = data.split(b'\r\n')
		for i in range(len(lines) - 1):
			line = str(lines[i], 'utf-8', 'replace')
			if self.debug: print('<-', line)
			yield line
		last = lines[-1]
		if last:
			self.last_buf = last

	def connect(self, host, port):
		self.socket = socket.socket()
		self.socket.setblocking(False)
		error = None
		try:
			self.socket.connect_ex((host, port))
		except socket.error as e:
			error = e
		return self.socket.fileno(), error

	def disconnect(self):
		if self.socket is None:
			return
		try:
			self.send('QUIT')
		except socket.error as e:
			if e.errno != errno.EPIPE:
				raise
		self.socket.close()
		self.socket = None
