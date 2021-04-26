from honeypots import QDNSServer, QFTPServer, QHTTPProxyServer, QHTTPSServer, QHTTPServer, QIMAPServer, QMysqlServer, QPOP3Server, QPostgresServer, QRedisServer, QSMBServer, QSMTPServer, QSOCKS5Server, QSSHServer, QTelnetServer, QVNCServer, clean_all
from time import sleep
from socket import gethostbyname

ip = gethostbyname("honeypots")

print("Testing QDNSServer")
qdnsserver = QDNSServer(ip=ip)
sleep(1)
qdnsserver.test_server()
qdnsserver.kill_server()

print("Testing QFTPServer")
qftpserver = QFTPServer(ip=ip)
sleep(1)
qftpserver.test_server()
qftpserver.kill_server()

print("Testing QHTTPProxyServer")
qhttpproxyserver = QHTTPProxyServer(ip=ip)
sleep(1)
qhttpproxyserver.test_server()
qhttpproxyserver.kill_server()

print("Testing QHTTPServer")
qhttpserver = QHTTPServer(ip=ip)
sleep(1)
qhttpserver.test_server()
qhttpserver.kill_server()

print("Testing QHTTPSServer")
qhttpsserver = QHTTPSServer(ip=ip)
sleep(1)
qhttpsserver.test_server()
qhttpsserver.kill_server()

print("Testing QIMAPServer")
qimapserver = QIMAPServer(ip=ip)
sleep(1)
qimapserver.test_server()
qimapserver.kill_server()

print("Testing QMysqlServer")
qmysqlserver = QMysqlServer(ip=ip)
sleep(1)
qmysqlserver.test_server()
qmysqlserver.kill_server()

print("Testing QTPOP3Server")
qpop3server = QPOP3Server(ip=ip)
sleep(1)
qpop3server.test_server()
qpop3server.kill_server()

print("Testing QPostgresServer")
qpostgresserver = QPostgresServer(ip=ip)
sleep(1)
qpostgresserver.test_server()
qpostgresserver.kill_server()

print("Testing QRedisServer")
qredisserver = QRedisServer(ip=ip)
sleep(1)
qredisserver.test_server()
qredisserver.kill_server()

print("Testing QSMBServer")
qsmbserver = QSMBServer(ip=ip)
sleep(1)
qsmbserver.test_server()
qsmbserver.kill_server()

print("Testing QSMTPServer")
qsmtpserver = QSMTPServer(ip=ip)
sleep(1)
qsmtpserver.test_server()
qsmtpserver.kill_server()

print("Testing QSOCKS5Server")
qsocks5server = QSOCKS5Server(ip=ip)
sleep(1)
qsocks5server.test_server()
qsocks5server.kill_server()

print("Testing QSSHServer")
qsshserver = QSSHServer(ip=ip)
sleep(1)
qsshserver.test_server()
qsshserver.kill_server()

print("Testing QTelnetServer")
qtelnetserver = QTelnetServer(ip=ip)
sleep(1)
qtelnetserver.test_server()
qtelnetserver.kill_server()

print("Testing QVNCServer")
qvncserver = QVNCServer(ip=ip)
sleep(1)
qvncserver.test_server()
qvncserver.kill_server()
clean_all()
