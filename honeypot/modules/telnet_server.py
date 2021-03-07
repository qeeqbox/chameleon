__G__ = "(G)bd249ce4"

from warnings import filterwarnings
filterwarnings(action='ignore',module='.*OpenSSL.*')

from twisted.conch.telnet import TelnetProtocol, TelnetTransport
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from random import choice
from psutil import process_iter
from signal import SIGTERM
from telnetlib import Telnet as TTelnet
from logging import DEBUG, basicConfig, getLogger
from twisted.python import log as tlog
from os import path
from tempfile import gettempdir,_get_candidate_names
from subprocess import Popen
from socket import socket as ssocket
from socket import AF_INET,SOCK_STREAM

class QTelnetServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 23
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or ''
		self.random_servers = ['Ubuntu 18.04 LTS','Ubuntu 16.04.3 LTS','Welcome to Microsoft Telnet Server.']
		self.process = None
		self._logs = logs
		self.setup_logger(self._logs)
		self.disable_logger()

	def disable_logger(self):
		temp_name = path.join(gettempdir(), next(_get_candidate_names()))
		tlog.startLogging(open(temp_name, 'w'), setStdout=False)

	def setup_logger(self,logs):
		self.logs = getLogger('chameleonlogger')
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

	def test_server(self,ip=None,port=None,username=None,password=None):

		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			t = TTelnet(_ip, _port)
			t.read_until("login: ")
			t.write(_username + "\n")
			t.read_until("Password: ")
			t.write(_password + "\n")
		except Exception as e:
			print(e)

	def run_server(self,process=False):
		if process:
			if self.close_port():
				self.process = Popen(['python',path.realpath(__file__),'--custom','--ip',str(self.ip),'--port',str(self.port),'--username',str(self.username),'--password',str(self.password),'--mocking',str(self.mocking),'--logs',str(self._logs)])
		else:
			self.telent_server_main()

	def kill_server(self,process=False):
		if self.process != None:
			self.process.kill()

	def close_port(self):
		sock = ssocket(AF_INET,SOCK_STREAM)
		sock.settimeout(2) 
		if sock.connect_ex((self.ip,self.port)) == 0:
			for process in process_iter():
				try:
					for conn in process.connections(kind='inet'):
						if self.port == conn.laddr.port:
							process.send_signal(SIGTERM)
							process.kill()
				except:
					pass
		if sock.connect_ex((self.ip,self.port)) != 0:
			return True
		else:
			self.logs.error(['errors',{'server':'telnet_server','error':'port_open','type':'Port {} still open..'.format(self.ip)}])
			return False

if __name__ == '__main__':
	from server_options import server_arguments
	parsed = server_arguments()
	if parsed.docker or parsed.aws or parsed.custom:
		qtelnetserver = QTelnetServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qtelnetserver.run_server()
