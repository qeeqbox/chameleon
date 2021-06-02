from honeypots import QDNSServer, QFTPServer, QHTTPProxyServer, QHTTPSServer, QHTTPServer, QIMAPServer, QMysqlServer, QPOP3Server, QPostgresServer, QRedisServer, QSMBServer, QSMTPServer, QSOCKS5Server, QSSHServer, QTelnetServer, QVNCServer, QElasticServer, QMSSQLServer, clean_all
from socket import gethostbyname
from sys import modules
from pebble import concurrent
from time import sleep

ip = gethostbyname("honeypots")
honeypots_module = modules["honeypots"]

@concurrent.process(timeout=10)
def run_server(name, ip):
	print("Testing {}".format(name))
	x = getattr(honeypots_module, name)(ip=ip)
	x.test_server()
	x.kill_server()
	print("Killing {}".format(name))

for key in dir(honeypots_module):
	if isinstance( getattr(honeypots_module, key), type ):
		if key.lower().endswith("server"):
			try:
				future = run_server(key,ip)
				result = future.result()
			except:
				print("Closing {}".format(key))

print("Done!")
clean_all()
