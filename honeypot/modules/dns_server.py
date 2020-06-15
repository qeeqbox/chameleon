__G__ = "(G)bd249ce4"

from multiprocessing import Process
from twisted.names import dns, error,client
from twisted.names.server import DNSServerFactory
from twisted.internet import defer, reactor
from psutil import process_iter
from signal import SIGTERM
from time import sleep
from subprocess import Popen,PIPE
from shlex import split as ssplit
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

class QDNSServer():
	def __init__(self,ip=None,port=None,resolver_addresses=None,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 53 
		self.resolver_addresses = resolver_addresses or [("8.8.8.8", 53)]
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def dns_server_main(self):
		_q_s = self
		class CustomCilentResolver(client.Resolver):
			def queryUDP(self, queries, timeout=2):
				res = client.Resolver.queryUDP(self, queries, timeout)
				def queryFailed(reason):
					return defer.fail(error.DomainError())
				res.addErrback(queryFailed)
				return res

		class CustomDNSServerFactory(DNSServerFactory):
			def gotResolverResponse(self, response, protocol, message, address):
				args = (self, response, protocol, message, address)
				try:
					for items in response:
						for item in items:
							_q_s.logs.info(["servers",{'server':'dns_server','action':'query','ip':address[0],'port':address[1],'payload':item.payload}])
				except Exception as e:
					_q_s.logs.error(["errors",{'server':'dns_server','error':'gotResolverResponse',"type":"error -> "+repr(e)}])
				return DNSServerFactory.gotResolverResponse(*args)
		

		self.resolver = CustomCilentResolver(servers=self.resolver_addresses)
		self.factory = CustomDNSServerFactory(clients=[self.resolver])
		self.protocol = dns.DNSDatagramProtocol(controller=self.factory)
		reactor.listenUDP(self.port, self.protocol,interface=self.ip)
		reactor.listenTCP(self.port, self.factory,interface=self.ip)
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server = Process(name='QFTPServer_', target=self.ftp_server_main)
			self.ftp_server.start()
		else:
			self.dns_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.ftp_server.terminate()
			self.ftp_server.join()

	def test_server(self,ip,port,domain):
		try:
			sleep(2)
			_ip = ip or self.ip
			_port = port or self.port 
			_domain = domain or "yahoo.com"
			proc=Popen(ssplit('dig -p {} @{} {} A +short'.format(_port,_ip,_domain)),stdout=PIPE)
			out,err=proc.communicate()
			raise ValueError(out)
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
		qdnsserver = QDNSServer(ip=parsed.ip,port=parsed.port,resolver_addresses=parsed.resolver_addresses,logs=parsed.logs)
		qdnsserver.run_server()

	if parsed.test:
		qdnsserver = QDNSServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qdnsserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
