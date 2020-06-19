__G__ = "(G)bd249ce4"

from twisted.protocols.ftp import FTPFactory, FTP, AUTH_FAILURE
from twisted.internet import reactor
from ftplib import FTP as FFTP
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from multiprocessing import Process
from logging import DEBUG, basicConfig, getLogger
from twisted.python import log as tlog
from os import path
from tempfile import gettempdir,_get_candidate_names

class QFTPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 21
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['ProFTPD 1.2.10','ProFTPD 1.3.4a','FileZilla ftp 0.9.43','Gene6 ftpd 3.10.0','FileZilla ftp 0.9.33','ProFTPD 1.2.8']
		self.setup_logger(logs)

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

	def ftp_server_main(self):
		_q_s = self

		class CustomFTPProtocol(FTP):

			def ftp_PASS(self, password):
				if self._user == _q_s.username and password == _q_s.password:
					_q_s.logs.info(["servers",{'server':'ftp_server','action':'login','status':'success','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':_q_s.username,'password':_q_s.password}])
				else:
					_q_s.logs.info(["servers",{'server':'ftp_server','action':'login','status':'failed','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'username':self._user,'password':password}])
				return AUTH_FAILURE

		class CustomFTPFactory(FTPFactory):
			protocol = CustomFTPProtocol
			portal = None
			
			def buildProtocol(self, address):
				p = self.protocol()
				p.portal = self.portal
				p.factory = self
				return p

		factory = CustomFTPFactory()
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server = Process(name='FTPServer_', target=self.ftp_server_main)
			self.ftp_server.start()
		else:
			self.ftp_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server.terminate()
			self.ftp_server.join()

	def test_server(self,ip,port,username,password):
		sleep(3)
		try:
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			f = FFTP()
			f.connect(_ip,_port)
			f.login(_username,_password)
		except Exception as e:
			self.logs.error(["errors",{'server':'ftp_server','error':'write',"type":"error -> "+repr(e)}])

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
		ftpserver = QFTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		ftpserver.run_server()

	if parsed.test:
		ftpserver = QFTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		ftpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
