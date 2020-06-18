__G__ = "(G)bd249ce4"

from twisted.internet import reactor
from OpenSSL import crypto
from string import digits,ascii_lowercase
from random import choice
from rdpy.protocol.rdp.rdp import RDPServerObserver, ServerFactory
from rdpy.protocol.rdp.rdp import ClientFactory,RDPClientObserver
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from multiprocessing import Process
from tempfile import gettempdir
from os import path
from logging import DEBUG, basicConfig, getLogger
from twisted.python import log as tlog
from os import path
from tempfile import gettempdir,_get_candidate_names

def gen_random_string(n):
	return ''.join(choice(digits+ascii_lowercase) for _ in range(n))

def gen_random_path_name(n):
	return path.join(gettempdir(),gen_random_string(n))

class QRDPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 3389
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.key = gen_random_path_name(6)
		self.cert = gen_random_path_name(6)
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

	def CreateCert(self,host_name, key, cert):
		pk = crypto.PKey()
		pk.generate_key(crypto.TYPE_RSA, 2048)
		c = crypto.X509()
		c.get_subject().C = 'US'
		c.get_subject().ST = 'OR'
		c.get_subject().L = 'None'
		c.get_subject().O = 'None'
		c.get_subject().OU = 'None'
		c.get_subject().CN = gen_random_string(2)
		c.set_serial_number(0)
		before, after = (0, 60*60*24*365*2)
		c.gmtime_adj_notBefore(before)
		c.gmtime_adj_notAfter(after)
		c.set_issuer(c.get_subject())
		c.set_pubkey(pk)
		c.sign(pk, 'sha256')
		open(cert, "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, c))
		open(key, "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pk))

	def rdp_server_main(self):
		_q_s = self

		class CustomObserver(RDPServerObserver):
			def __init__(self, factory, controller):
				RDPServerObserver.__init__(self, controller)

			def onReady(self):
				domain, user, _pass = self._controller.getCredentials()
				self._controller.getHostname()
				self._controller.getProtocol().transport.getHost()
				client = self._controller.getProtocol().transport.getPeer()
				username, password = user.encode("utf-8").strip().replace('\00', ''), _pass.encode("utf-8").strip().replace('\00', '')
				if username == _q_s.username and password == _q_s.password:
					_q_s.logs.info(["servers",{'server':'rdp_server','action':'login','status':'success','ip':client.host,'port':client.port,'username':username,'password':password}])
				else:
					_q_s.logs.info(["servers",{'server':'rdp_server','action':'login','status':'failed','ip':client.host,'port':client.port,'username':username,'password':password}])
				self._controller.getProtocol().transport.loseConnection()
				return

			def onClose(self):
				return
				
			def onKeyEventScancode(self, code, isPressed, isExtended):
				return
			
			def onKeyEventUnicode(self, code, isPressed):
				return
				
			def onPointerEvent(self, x, y, button, isPressed):
				return
				
			def start(self):
				return
				
			def loopScenario(self, nextEvent):
				return

		class RDPHoneypot(ServerFactory):
			def __init__(self):
				_q_s.CreateCert("localhost", _q_s.key, _q_s.cert)
				ServerFactory.__init__(self, 16, _q_s.key, _q_s.cert)

			def buildObserver(self, controller, addr):
				return CustomObserver(self, controller)

			def handle_accept(self):
				conn, addr = self.accept()
				LMTPChannel(self, conn, addr)

		reactor.listenTCP(port=self.port, factory=RDPHoneypot(), interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.rdp_server = Process(name='QRDPServer_', target=self.rdp_server_main)
			self.rdp_server.start()
		else:
			self.rdp_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.rdp_server.terminate()
			self.rdp_server.join()

	def test_server(self,ip,port,username,password):
		_ip = ip or self.ip
		_port = port or self.port
		_username = username or self.username
		_password = password or self.password
		def _test_rdp_server_main():
			try:
				class CustomRDPFactory(ClientFactory):
					def clientConnectionLost(self, connector, reason):
						pass
					def clientConnectionFailed(self, connector, reason):
						pass
					def buildObserver(self, controller, addr):
						class CustomRDPClientObserver(RDPClientObserver):
							controller.setUsername(_username)
							controller.setPassword(_password)
							
							def onClose(self):
								pass
						return CustomRDPClientObserver(controller)
				reactor.connectTCP(_ip, _port, CustomRDPFactory())
				reactor.run()
			except Exception:
				pass

		self.rdp_server_test = Process(name='QRDPServer_test_rdp_server_main', target=_test_rdp_server_main)
		self.rdp_server_test.start()
		sleep(5)
		self.rdp_server_test.terminate()
		self.rdp_server_test.join()

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
		qrdpserver = QRDPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qrdpserver.run_server()

	if parsed.test:
		qrdpserver = QRDPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qrdpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)