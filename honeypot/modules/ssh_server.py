__G__ = "(G)bd249ce4"

from paramiko import ServerInterface,Transport,RSAKey,AutoAddPolicy
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
from _thread import start_new_thread
from io import StringIO
from random import choice
from multiprocessing import Process
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from paramiko import SSHClient
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

class QSSHServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 22
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['OpenSSH 7.5','OpenSSH 7.3','Serv-U SSH Server 15.1.1.108','OpenSSH 6.4']
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def generate_pub_pri_keys(self):
		try:
			key = RSAKey.generate(2048)
			string_io = StringIO()
			key.write_private_key(string_io)
			return key.get_base64(), string_io.getvalue()
		except:
			pass
		return None,None

	def ssh_server_main(self):
		_q_s = self

		class SSHHandle(ServerInterface):

			def __init__(self,ip,port):
				self.ip = ip
				self.port = port
				ServerInterface.__init__(self)

			def check_auth_password(self, username, password):
				username, password = username.encode("utf-8"), password.encode("utf-8")
				if username ==  _q_s.username and password == _q_s.password:
					_q_s.logs.info(["servers",{'server':'ssh_server','action':'login','status':'success','ip':self.ip,'port':self.port,'username':username,'password':password}])
				else:
					_q_s.logs.info(["servers",{'server':'ssh_server','action':'login','status':'failed','ip':self.ip,'port':self.port,'username':username,'password':password}])

		def ConnectionHandle(client,priv):
			try:
				t = Transport(client)
				ip, port = client.getpeername()
				t.local_version = 'SSH-2.0-'+choice(self.random_servers)
				t.add_server_key(RSAKey(file_obj=StringIO(priv)))
				t.start_server(server=SSHHandle(ip,port))
				chan = t.accept(1)
				if not chan is None:
					chan.close()
			except:
				pass

		sock = socket(AF_INET,SOCK_STREAM)
		sock.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
		sock.bind((self.ip, self.port))
		sock.listen(1)
		pub, priv = self.generate_pub_pri_keys()
		while True:
			try:
				client, addr = sock.accept()
				start_new_thread(ConnectionHandle,(client,priv,))
			except:
				pass

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.ssh_server = Process(name='QSSHServer_', target=self.ssh_server_main)
			self.ssh_server.start()
		else:
			self.ssh_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.ssh_server.terminate()
			self.ssh_server.join()

	def test_server(self,ip,port,username,password):
		try:
			sleep(2)
			_ip = ip or self.ip
			_port = port or self.port 
			_username = username or self.username
			_password = password or self.password
			ssh = SSHClient()
			ssh.set_missing_host_key_policy(AutoAddPolicy()) #if you have default ones, remove them before using this.. 
			ssh.connect(_ip, port=_port,username=_username,password=_password)
		except Exception as e:
			self.logs.error(["errors",{'server':'ssh_server','error':'write',"type":"error -> "+repr(e)}])

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
		qsshserver = QSSHServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qsshserver.run_server()

	if parsed.test:
		qsshserver = QSSHServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qsshserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)