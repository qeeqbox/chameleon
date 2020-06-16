__G__ = "(G)bd249ce4"

from twisted.mail.pop3 import POP3
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from random import choice
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from multiprocessing import Process
from poplib import POP3 as poplibPOP3
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig
from twisted.python import log as tlog
from os import path
from tempfile import gettempdir,_get_candidate_names

class QPOP3Server():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 110
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['Microsoft Exchange POP3 service is ready']
		self.setup_logger(logs)
		self.disable_logger()

	def disable_logger(self):
		temp_name = path.join(gettempdir(), next(_get_candidate_names()))
		tlog.startLogging(open(temp_name, "w"), setStdout=False)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def pop3_server_main(self):
		_q_s = self

		class CustomPOP3Protocol(POP3):

			self._user = None

			def connectionMade(self):

				self._user = None

				if isinstance(_q_s.mocking, bool):
					if _q_s.mocking == True:
						self.successResponse('{} \n'.format(choice(_q_s.random_servers)))
				elif isinstance(_q_s.mocking, str):
					self.successResponse('{} \n'.format(choice(_q_s.random_servers)))
				else:
					self.successResponse('Connected')

			def do_USER(self, user):
				self._user = user
				self.successResponse('USER Ok')

			def do_PASS(self, password):
				if self._user:
					if self._user == _q_s.username and password == _q_s.password:
						_q_s.logs.info(["servers",{'server':'pop3_server','action':'login','status':'success','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':_q_s.username,'password':_q_s.password}])
					else:
						_q_s.logs.info(["servers",{'server':'pop3_server','action':'login','status':'failed','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':self._user,'password':password}])
					self.failResponse('Authentication failed')
				else:
					self.failResponse('USER first, then PASS')
				
				self._user = None
				
			def lineReceived(self, line):
				if line.lower().startswith("user") or line.lower().startswith("pass"):
					POP3.lineReceived(self, line)
				else:
					self.failResponse('Authentication failed')

		class CustomPOP3Factory(Factory):
			protocol = CustomPOP3Protocol
			portal = None
			
			def buildProtocol(self, address):
				p = self.protocol()
				p.portal = self.portal
				p.factory = self
				return p

		factory = CustomPOP3Factory()
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.pop3_server = Process(name='QPOP3Server_', target=self.pop3_server_main)
			self.pop3_server.start()
		else:
			self.pop3_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.pop3_server.terminate()
			self.pop3_server.join()

	def test_server(self,ip,port,username,password):
		sleep(3)
		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			pp = poplibPOP3(_ip,_port)
			pp.user(_username)
			pp.pass_(_password)
		except Exception as e:
			self.logs.error(["errors",{'server':'pop3_server','error':'write',"type":"error -> "+repr(e)}])

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
		qpop3server = QPOP3Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qpop3server.run_server()

	if parsed.test:
		qpop3server = QPOP3Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qpop3server.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
