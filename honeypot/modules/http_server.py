__G__ = "(G)bd249ce4"

from cgi import FieldStorage
from multiprocessing import Process
from psutil import process_iter
from signal import SIGTERM
from requests import get,post
from requests.packages.urllib3 import disable_warnings
from time import sleep
from logging import DEBUG, basicConfig, getLogger
from os import path
from tempfile import gettempdir,_get_candidate_names
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from random import choice

disable_warnings()

class QHTTPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 80
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.key = path.join(gettempdir(), next(_get_candidate_names()))
		self.cert = path.join(gettempdir(), next(_get_candidate_names()))
		self.random_servers = ['Apache','nginx','Microsoft-IIS/7.5','Microsoft-HTTPAPI/2.0','Apache/2.2.15','SmartXFilter','Microsoft-IIS/8.5','Apache/2.4.6','Apache-Coyote/1.1','Microsoft-IIS/7.0','Apache/2.4.18','AkamaiGHost','Apache/2.2.25','Microsoft-IIS/10.0','Apache/2.2.3','nginx/1.12.1','Apache/2.4.29','cloudflare','Apache/2.2.22']
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def http_server_main(self):
		_q_s = self

		class MainResource(Resource):

			isLeaf = True
			login_file = b""
			home_file = b""
			server = ""
			if path.exists('templates'):
				login_file = open('templates/login.html','rb').read()
				home_file = open('templates/home.html','rb').read()
			elif path.exists('modules/templates'):
				login_file = open('modules/templates/login.html','rb').read()
				home_file = open('modules/templates/home.html','rb').read()
			if isinstance(_q_s.mocking, bool):
				if _q_s.mocking == True:
					server = choice(_q_s.random_servers)
			elif isinstance(_q_s.mocking, str):
				server = _q_s.mocking

			def render(self, request):
				if self.server != "":
					request.responseHeaders.removeHeader("Server")
					request.responseHeaders.addRawHeader("Server", self.server)

				if request.method == "GET":
					_q_s.logs.info(["servers",{'server':'http_server','action':'get','ip':request.getClientIP()}])
					if request.uri == "/login.html":
						if _q_s.username != '' and _q_s.password != '':
							request.responseHeaders.addRawHeader("Content-Type", "text/html; charset=utf-8")
							return self.login_file

					request.responseHeaders.addRawHeader("Content-Type", "text/html; charset=utf-8")
					return self.home_file

				elif request.method == "POST":
					self.headers = request.getAllHeaders()
					_q_s.logs.info(["servers",{'server':'http_server','action':'post','ip':request.getClientIP()}])
					if _q_s.username != '' and _q_s.password != '':
						form = FieldStorage(fp=request.content,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['content-type'],})
						if 'username' in form and 'password' in form:
							if form['username'].value == _q_s.username and form['password'].value == _q_s.password:
								_q_s.logs.info(["servers",{'server':'http_server','action':'login','status':'success','ip':request.getClientIP(),'username':_q_s.username,'password':_q_s.password}])
							else:
								_q_s.logs.info(["servers",{'server':'http_server','action':'login','status':'failed','ip':request.getClientIP(),'username':form['username'].value,'password':form['password'].value}])

					request.responseHeaders.addRawHeader("Content-Type", "text/html; charset=utf-8")
					return self.home_file
				else:
					request.responseHeaders.addRawHeader("Content-Type", "text/html; charset=utf-8")
					return self.home_file

		reactor.listenTCP(self.port, Site(MainResource()))
		reactor.run()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.http_server = Process(name='QHTTPServer', target=self.http_server_main)
			self.http_server.start()
		else:
			self.http_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.http_server.terminate()
			self.http_server.join()

	def test_server(self,ip,port,username,password):
		try:
			sleep(2)
			_ip = ip or self.ip
			_port = port or self.port
			_username = username or self.username
			_password = password or self.password
			get('http://{}:{}'.format(_ip,_port),verify=False)
			post('http://{}:{}'.format(_ip,_port),data={'username': (None, _username),'password': (None, _password)})
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
		qhttpserver = QHTTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qhttpserver.run_server()

	if parsed.test:
		qhttpserver = QHTTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qhttpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
