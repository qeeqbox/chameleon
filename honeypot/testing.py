from modules.dns_server import QDNSServer
from modules.ftp_server import QFTPServer
from modules.http_proxy_server import QHTTPPoxyServer
from modules.http_server import QHTTPServer
from modules.https_server import QHTTPSServer
from modules.rdp_server import QRDPServer
from modules.smb_server import QSMBServer
from modules.smtp_server import QSMTPServer
from modules.ssh_server import QSSHServer
from modules.telnet_server import QTelnetServer
from modules.pop3_server import QPOP3Server
from modules.socks5_server import QSOCKS5Server
from modules.postgres_server import QPostgresServer
from modules.imap_server import QIMAPServer
from modules.redis_server import QRedisServer
from modules.mysql_server import QMysqlServer
from modules.server_options import server_arguments
from socket import gethostbyname

parsed = server_arguments()
parsed.ip = gethostbyname("honeypot")
parsed.logs = "terminal"
parsed.mocking = True

print("Testing QDNSServer")
qdnsserver = QDNSServer(ip=parsed.ip,port=parsed.port,resolver_addresses=parsed.resolver_addresses,logs=parsed.logs)
qdnsserver.test_server(ip=parsed.ip,port=parsed.port,domain=parsed.domain)
print("Testing QHTTPPoxyServer")
qhttpproxyserver = QHTTPPoxyServer(ip=parsed.ip,port=parsed.port,mocking=parsed.mocking,logs=parsed.logs)
qhttpproxyserver.test_server(ip=parsed.ip,port=parsed.port,domain=parsed.domain)
print("Testing QFTPServer")
qftpserver = QFTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qftpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QHTTPServer")
qhttpserver = QHTTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qhttpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QHTTPSServer")
qhttpsserver = QHTTPSServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qhttpsserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QRDPServer")
qrdpserver = QRDPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qrdpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QSMBServer")
qsmbserver = QSMBServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qsmbserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QSMTPServer")
qsmtpserver = QSMTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qsmtpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QSSHServer")
qsshserver = QSSHServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qsshserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QTelnetServer")
qtelnetserver = QTelnetServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qtelnetserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QTPOP3Server")
qpop3server = QPOP3Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qpop3server.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QTPOP3Server")
qimapserver = QIMAPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qimapserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QSOCKS5Server")
qsocks5server = QSOCKS5Server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qsocks5server.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QPostgresServer")
qpostgresserver = QPostgresServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qpostgresserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QRedisServer")
qredisserver = QRedisServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qredisserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
print("Testing QRedisServer")
qmysqlserver = QMysqlServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
qmysqlserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)