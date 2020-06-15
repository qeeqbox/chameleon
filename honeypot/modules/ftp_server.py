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

class QFTPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 21
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['ProFTPD 1.2.10','ProFTPD 1.3.4a','FileZilla ftp 0.9.43','Gene6 ftpd 3.10.0','FileZilla ftp 0.9.33','ProFTPD 1.2.8']
		self.setup_logger(logs)

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

		class CustomFtpHandler(FTPHandler):
			def on_login(self, username):
				_q_s.logs.info(["servers",{'server':'ftp_server','action':'login','ip':self.remote_ip,'port':self.remote_port,'status':'success','username':_q_s.username,'password':_q_s.password}])
		 
			def on_login_failed(self, username, password):
				username, password = username.encode("utf-8"), password.encode("utf-8")
				_q_s.logs.info(["servers",{'server':'ftp_server','action':'login','ip':self.remote_ip,'port':self.remote_port,'status':'failed','username':username,'password':password}])

			def handle_error(self):
				_q_s.logs.error(["errors",{'server':'ftp_server','error':'handle_error',"type":"None"}])

		dirpath = mkdtemp()
		authorizer = DummyAuthorizer()
		authorizer.add_user(self.username,self.password,dirpath, perm='')
		handler = CustomFtpHandler
		handler.authorizer = authorizer
		if isinstance(_q_s.mocking, bool):
			if _q_s.mocking == True:
				handler.banner = choice(self.random_servers)
		elif isinstance(_q_s.mocking, str):
			handler.banner = _q_s.mocking
		server = servers.FTPServer((self.ip, self.port), handler)
		server.max_cons = 256
		server.max_cons_per_ip = 5
		server.serve_forever()
		rmtree(dirpath)

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server = Process(name='QFTPServer_', target=self.ftp_server_main)
			self.ftp_server.start()
		else:
			self.ftp_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server.terminate()
			self.ftp_server.join()

	def test_server(self,ip=None,port=None,username=None,password=None):
		try:
			sleep(2)
			f = FTP()
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			f.connect(_ip,_port)
			f.login(_username,_password)
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
		qftpserver = QFTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qftpserver.run_server()

	if parsed.test:
		qftpserver = QFTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qftpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
