from warnings import filterwarnings
filterwarnings(action='ignore',module='.*OpenSSL.*')

from argparse import ArgumentParser
from glob import glob
from time import sleep
from sys import stdout
from logging import DEBUG, getLogger
from subprocess import Popen
from netifaces import ifaddresses,AF_INET,AF_LINK
from psutil import Process,net_io_counters
from ntpath import basename

parser = ArgumentParser(description="Qeeqbox/chameleon")
parser.add_argument("--servers",help="list of servers server:port E.g. http:8001 https:8887", metavar="")
parser.add_argument("--mode", help="normal or docker", metavar="")
parsed = parser.parse_args()

if parsed.servers != "" and parsed.mode == "normal":
	servers = []
	temp_filse = []
	temp_servers = list(x.split(':') for x in parsed.servers.split())
	files = [_ for _ in glob('/honeypot/modules/*.py')]
	for server in temp_servers:
		file = "/honeypot/modules/{}_server.py".format(server[0])
		if file in files and file not in temp_filse:
			temp_filse.append(file)
			servers.append([basename(server[0]),Popen(['python',file,'--logs','terminal','--docker','--port',server[1]])])
	if len(servers) > 0:
		while True:
			sleep(1)
	else:
		print("No servers to run")
else:
	print('Your IP: {}'.format(ifaddresses('eth0')[AF_INET][0]['addr'].encode('utf-8')))
	print('Your MAC: {}'.format(ifaddresses('eth0')[AF_LINK][0]['addr'].encode('utf-8')))
	Popen('iptables -A OUTPUT -p tcp -m tcp --tcp-flags RST RST -j DROP',shell=True)
	print('Wait for 10 seconds..')
	stdout.flush()
	sleep(10)
	from modules.postgres_conn import postgres_class
	postgres_class(drop=True)
	from modules.custom_logging import CustomHandler
	logs = getLogger('chameleonlogger')
	logs.setLevel(DEBUG)	
	logs.addHandler(CustomHandler('db'))

	servers = [] 

	for _ in glob('/honeypot/modules/*.py'):
		if _.endswith('_server.py'):
			servers.append([basename(_)[:-3],Popen(['python',_,'--docker','--logs','db'])])
		elif _.endswith('sniffer.py'):
			servers.append([basename(_)[:-3],Popen(['python',_,'--filter','not port 9999','--interfac','eth0','--logs','db','--docker'])])

	while True:
		try:
			_servers = {}
			logs.info(['system',{'type':'network','bytes_sent':net_io_counters().bytes_sent,'bytes_recv':net_io_counters().bytes_recv,'packets_sent':net_io_counters().packets_sent,'packets_recv':net_io_counters().packets_recv}])
			for _ in servers:
				_servers[_[0]] = {'memory':Process(_[1].pid).memory_percent(),'cpu':Process(_[1].pid).cpu_percent()}
			logs.info(['system',_servers])
			stdout.flush()
		except:
			pass
		sleep(20)