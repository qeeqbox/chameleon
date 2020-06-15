__G__ = "(G)bd249ce4"

from dns.resolver import query as dsnquery
from twisted.internet import reactor
from twisted.internet.protocol import Protocol,ClientFactory,Factory
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
from psutil import process_iter
from signal import SIGTERM
from multiprocessing import Process
from requests import get
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

class QHTTPPoxyServer():
	def __init__(self,ip=None,port=None,mocking=None,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 8080 
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

	def http_proxy_server_main(self):
		_q_s = self

		class CustomProtocolParent(Protocol):

			def __init__(self):
				self.buffer = None
				self.client = None

			def resolve_domain(self,request):
				class ParseHTTPRequest(BaseHTTPRequestHandler):
					def __init__(self, request_text):
						self.rfile = StringIO(request_text)
						self.raw_requestline = self.rfile.readline()
						self.error_code = self.error_message = None
						self.parse_request()

				try:
					parsed_request = ParseHTTPRequest(request)
					host = parsed_request.headers["host"].split(":")
					_q_s.logs.info(["servers",{'server':'http_proxy_server','action':'query','ip':self.transport.getPeer().host,'port':self.transport.getPeer().port,'payload':host[0]}])
					#return "127.0.0.1"
					return dsnquery(host[0], 'A')[0].address
				except Exception as e:
					_q_s.logs.error(["errors",{'server':'http_proxy_server','error':'resolve_domain',"type":"error -> "+repr(e)}])
				return None

			def dataReceived(self, data):
				try:
					ip = self.resolve_domain(data)
					if ip:
						factory = ClientFactory()
						factory.CustomProtocolParent_= self
						factory.protocol = CustomProtocolChild
						reactor.connectTCP(ip, 80, factory)
					else:
						self.transport.loseConnection()

					if self.client:
						self.client.write(data)
					else:
						self.buffer = data
				except:
					pass

			def write(self, data):
				self.transport.write(data)

		class CustomProtocolChild(Protocol):
			def connectionMade(self):
				self.write(self.factory.CustomProtocolParent_.buffer)

			def dataReceived(self, data):
				self.factory.CustomProtocolParent_.write(data)

			def write(self, data):
				self.transport.write(data)

		factory = Factory()
		factory.protocol = CustomProtocolParent
		reactor.listenTCP(port=self.port, factory=factory, interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.proxy_server = Process(name='QHTTPPoxyServer_', target=self.http_proxy_server_main)
			self.proxy_server.start()
		else:
			self.http_proxy_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.proxy_server.terminate()
			self.proxy_server.join()

	def test_server(self,ip,port,domain):
		try:
			_ip = ip or self.ip
			_port = port or self.port
			_domain = domain or "http://yahoo.com"
			get(_domain, proxies={"http":'http://{}:{}'.format(_ip,_port)}).text.encode('ascii', 'ignore')
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
		qhttpproxyserver = QHTTPPoxyServer(ip=parsed.ip,port=parsed.port,mocking=parsed.mocking,logs=parsed.logs)
		qhttpproxyserver.run_server()

	if parsed.test:
		qhttpproxyserver = QHTTPPoxyServer(ip=parsed.ip,port=parsed.port,mocking=parsed.mocking,logs=parsed.logs)
		qhttpproxyserver.test_server(ip=parsed.ip,port=parsed.port,domain=parsed.domain)