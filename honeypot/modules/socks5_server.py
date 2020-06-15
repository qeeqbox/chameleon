__G__ = "(G)bd249ce4"

from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
from tempfile import mkdtemp
from shutil import rmtree
from random import choice
from multiprocessing import Process
from ftplib import FTP
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig
from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn
from struct import unpack,pack
from requests import get

class QSOCKS5Server():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 1080
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def socks5_server_main(self):
		_q_s = self

		class CustomStreamRequestHandler(StreamRequestHandler):
			def handle(self):
				v,m = unpack("!BB", self.connection.recv(2))
				if v == 5:
					if 2 in unpack("!"+"B"*m,self.connection.recv(m)):
						self.connection.sendall('\x05\x02')
						if 1 in unpack("B",self.connection.recv(1)):
							_len = ord(self.connection.recv(1))
							username = self.connection.recv(_len)
							_len = ord(self.connection.recv(1))
							password = self.connection.recv(_len)
							if username == _q_s.username and password == _q_s.password:
								_q_s.logs.info(["servers",{'server':'socks5_server','action':'login','status':'success','ip':self.client_address[0],'port':self.client_address[1],'username':_q_s.username,'password':_q_s.password}])
							else:
								_q_s.logs.info(["servers",{'server':'socks5_server','action':'login','status':'failed','ip':self.client_address[0],'port':self.client_address[1],'username':username,'password':password}])
				self.server.close_request(self.request)

		class ThreadingTCPServer(ThreadingMixIn, TCPServer):
			pass

		server = ThreadingTCPServer((self.ip, self.port), CustomStreamRequestHandler)
		server.serve_forever()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.socks5_server = Process(name='QSOCKS5Server_', target=self.socks5_server_main)
			self.socks5_server.start()
		else:
			self.socks5_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.socks5_server.terminate()
			self.socks5_server.join()

	def test_server(self,ip=None,port=None,username=None,password=None):
		try:
			sleep(2)
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			get('https://yahoo.com', proxies=dict(http='socks5://{}:{}@{}:{}'.format(_username,_password,_ip,_port),https='socks5://{}:{}@{}:{}'.format(_username,_password,_ip,_port)))
		except:
			pass
			
	def close_port(self):
		for process in process_iter():
			try:
				for conn in process.connections(kind='inet'):
					if self.port == conn.laddr.port:
						process.send_signal(SIGTERM)
						process.kill()
			except:
				pass

if __name__ == "__main__":
	from server_options import server_arguments
	parsed = server_arguments()

	if parsed.docker or parsed.aws or parsed.custom:
		QSOCKS5Server = QSOCKS5Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		QSOCKS5Server.run_server()

	if parsed.test:
		QSOCKS5Server = QSOCKS5Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		QSOCKS5Server.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
