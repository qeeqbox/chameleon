__G__ = "(G)bd249ce4"

from twisted.internet.protocol import Protocol,Factory
from twisted.internet import reactor
from psutil import process_iter
from signal import SIGTERM
from logging import DEBUG, basicConfig, getLogger
from struct import unpack
from itertools import izip
from psycopg2 import connect
from twisted.python import log as tlog
from os import path
from tempfile import gettempdir,_get_candidate_names
from subprocess import Popen
from socket import socket as ssocket
from socket import AF_INET,SOCK_STREAM

class QPostgresServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 5432
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or ''
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

	def postgres_server_main(self):
		_q_s = self

		class CustomPostgresProtocol(Protocol):

			_state = None
			_variables = {}

			def read_data_custom(self,data):
				length = unpack("!I", data[0:4])
				x = (data[8:-1].split('\x00'))
				self._variables = dict(izip(*([iter(x)]*2)))

			def read_password_custom(self,data):
				self._variables["password"] = data[5:].split('\x00')[0]

			def connectionMade(self):
				self._state = 1
				self._variables = {}

			def dataReceived(self, data):
				if self._state == 1:
					self._state = 2
					self.transport.write(b'N')
				elif self._state == 2:
					self.read_data_custom(data)
					self._state = 3
					self.transport.write(b'R\x00\x00\x00\x08\x00\x00\x00\x03')
				elif self._state == 3:
					if data[0] == 'p' and "user" in self._variables:
						self.read_password_custom(data)
						if self._variables["user"] == _q_s.username and self._variables["password"] == _q_s.password:
							_q_s.logs.info(["servers",{'server':'postgres_server','action':'login','status':'success','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':_q_s.username,'password':_q_s.password}])
						else:
							_q_s.logs.info(["servers",{'server':'postgres_server','action':'login','status':'failed','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':self._variables["user"],'password':self._variables["password"]}])
					self.transport.loseConnection()
				else:
					self.transport.loseConnection()

			def connectionLost(self, reason):
				self._state = 1
				self._variables = {}

		factory = Factory()
		factory.protocol = CustomPostgresProtocol
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def test_server(self,ip=None,port=None,username=None,password=None):

		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			x = connect(host=_ip,port=_port,user=_username,password=_password)
		except Exception:
			pass

	def run_server(self,process=False):
		if process:
			if self.close_port():
				self.process = Popen(['python',path.realpath(__file__),'--custom','--ip',str(self.ip),'--port',str(self.port),'--username',str(self.username),'--password',str(self.password),'--mocking',str(self.mocking),'--logs',str(self._logs)])
		else:
			self.postgres_server_main()

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
			self.logs.error(['errors',{'server':'postgres_server','error':'port_open','type':'Port {} still open..'.format(self.ip)}])
			return False

if __name__ == '__main__':
	from server_options import server_arguments
	parsed = server_arguments()
	if parsed.docker or parsed.aws or parsed.custom:
		qpostgresserver = QPostgresServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qpostgresserver.run_server()