__G__ = "(G)bd249ce4"

from twisted.conch.telnet import TelnetProtocol, TelnetTransport
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from random import choice
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from multiprocessing import Process
from telnetlib import Telnet
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

class QTelnetServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 23
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['Ubuntu 18.04 LTS','Ubuntu 16.04.3 LTS','Welcome to Microsoft Telnet Server.']
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def telent_server_main(self):
		_q_s = self

		class CustomTelnetProtocol(TelnetProtocol):
			_state = None
			_user = None
			_pass = None

			def connectionMade(self):
				self._state = None
				self._user = None
				self._pass = None

				if isinstance(_q_s.mocking, bool):
					if _q_s.mocking == True:
						self.transport.write('{} \n'.format(choice(_q_s.random_servers)))
				elif isinstance(_q_s.mocking, str):
					self.transport.write('{} \n'.format(choice(_q_s.random_servers)))				
				self.transport.write('PC login: ')
				self._state = "Username"

			def dataReceived(self, data):
				data = data.strip()
				if self._state == 'Username':
					self._user = data
					self._state = "Password"
					self.transport.write('Password: ')
				elif self._state == 'Password':
					self._pass = data
					if self._user == _q_s.username and self._pass == _q_s.password:
						_q_s.logs.info(["servers",{'server':'telnet_server','action':'login','status':'success','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':_q_s.username,'password':_q_s.password}])
					else:
						_q_s.logs.info(["servers",{'server':'telnet_server','action':'login','status':'failed','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':self._user,'password':self._pass}])
					self.transport.loseConnection()
				else:
					self.transport.loseConnection()

			def connectionLost(self, reason):
				self._state = None
				self._user = None
				self._pass = None

		factory = Factory()
		factory.protocol = lambda: TelnetTransport(CustomTelnetProtocol)
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.telnet_server = Process(name='QTelnetServer_', target=self.telent_server_main)
			self.telnet_server.start()
		else:
			self.telent_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.telnet_server.terminate()
			self.telnet_server.join()

	def test_server(self,ip,port,username,password):
		sleep(3)
		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			t = Telnet(_ip, _port, 15)
			t.read_until("login: ")
			t.write(_username + "\n")
			t.read_until("Password: ")
			t.write(_password + "\n")
		except Exception:
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
		qtelnetserver = QTelnetServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qtelnetserver.run_server()

	if parsed.test:
		qtelnetserver = QTelnetServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qtelnetserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
