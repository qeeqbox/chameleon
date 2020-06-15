__G__ = "(G)bd249ce4"

from twisted.mail.imap4 import IMAP4Server
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from random import choice
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from multiprocessing import Process
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig
from twisted import cred
from sys import stdout
from imaplib import IMAP4

class QIMAPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 143
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['OK Microsoft Exchange Server 2003 IMAP4rev1 server version 6.5.6944.0 DC9 ready']
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def imap_server_main(self):

		_q_s = self

		class CustomIMAP4Server(IMAP4Server):

			def connectionMade(self):
				if isinstance(_q_s.mocking, bool):
					if _q_s.mocking == True:
						self.sendPositiveResponse(message='{} \n'.format(choice(_q_s.random_servers)))
				elif isinstance(_q_s.mocking, str):
					self.sendPositiveResponse(message='{} \n'.format(choice(_q_s.random_servers)))
				else:
					self.sendPositiveResponse(message='Welcome')

			def authenticateLogin(self, user, passwd):
				if user == _q_s.username and passwd == _q_s.password:
					_q_s.logs.info(["servers",{'server':'imap_server','action':'login','status':'success','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':_q_s.username,'password':_q_s.password}])
				else:
					_q_s.logs.info(["servers",{'server':'imap_server','action':'login','status':'failed','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':user,'password':passwd}])
				
				raise cred.error.UnauthorizedLogin()

			def lineReceived(self, line):
				try:
					_line = line.split(" ")[1]
					if _line.lower().startswith("login") or _line.lower().startswith("capability"):
						IMAP4Server.lineReceived(self, line)
				except:
					pass

		class CustomIMAPFactory(Factory):
			protocol = CustomIMAP4Server
			portal = None
			
			def buildProtocol(self, address):
				p = self.protocol()
				p.portal = self.portal
				p.factory = self
				return p

		factory = CustomIMAPFactory()
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.imap_server = Process(name='QIMAPServer_', target=self.imap_server_main)
			self.imap_server.start()
		else:
			self.imap_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.imap_server.terminate()
			self.imap_server.join()

	def test_server(self,ip,port,username,password):
		sleep(3)
		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			imap_test = IMAP4(_ip,_port)
			imap_test.login(_username, _password)
		except Exception as e:
			self.logs.error(["errors",{'server':'imap_server','error':'write',"type":"error -> "+repr(e)}])

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
		qimaperver = QIMAPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qimaperver.run_server()

	if parsed.test:
		qimaperver = QIMAPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qimaperver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
