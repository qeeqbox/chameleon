from time import sleep
from sys import stdout
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

print('Wait for 10 seconds..')
sleep(10)
stdout.flush()
from modules.postgres_conn import postgres_class
postgres_class(drop=True)

from modules.custom_logging import CustomHandler
from psutil import Process,net_io_counters
from ntpath import basename
from netifaces import ifaddresses,AF_INET,AF_LINK
from subprocess import Popen
from glob import glob

logs = getLogger('chameleonlogger')
logs.setLevel(DEBUG)	
logs.addHandler(CustomHandler('db'))

print('Your IP: {}'.format(ifaddresses('eth0')[AF_INET][0]['addr'].encode('utf-8')))
print('Your MAC: {}'.format(ifaddresses('eth0')[AF_LINK][0]['addr'].encode('utf-8')))
Popen('iptables -A OUTPUT -p tcp -m tcp --tcp-flags RST RST -j DROP',shell=True)

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