<p align="center"> <img src="https://raw.githubusercontent.com/qeeqbox/chameleon/master/readme/chameleonlogo.png"></p>

#
[![Generic badge](https://img.shields.io/badge/dynamic/json.svg?url=https://raw.githubusercontent.com/qeeqbox/chameleon/master/info&label=version&query=$.version&colorB=blue)](https://github.com/qeeqbox/chameleon/blob/master/changes.md) [![Generic badge](https://img.shields.io/badge/dynamic/json.svg?url=https://raw.githubusercontent.com/qeeqbox/chameleon/master/info&label=docker-compose&query=$.dockercompose&colorB=green)](https://github.com/qeeqbox/chameleon/blob/master/changes.md)

Customizable honeypots (DNS, HTTP Proxy, HTTP, HTTPS, SSH, POP3, IMAP, STMP, RDP, VNC, SMB, SOCK5, TELNET and Postgres) for monitoring network traffic, bots activities and loose credentials

## Grafana Interface
<img src="https://raw.githubusercontent.com/qeeqbox/chameleon/master/readme/intro.png" style="max-width:768px"/>

#### NMAP Scan
<img src="https://raw.githubusercontent.com/qeeqbox/chameleon/master/readme/nmap_scan.png" style="max-width:768px"/>

#### Credentials Monitoring
<img src="https://raw.githubusercontent.com/qeeqbox/chameleon/master/readme/creds_monitoring.png" style="max-width:768px"/>

## General Features
- Modular approach (honeypots run as scripts or imported as objects)
- Most honeypots serve as servers (Only a few that emulate the application layer protocols)
- Settings servers with username, password and banner (Default username and password are test)
- ICMP, DNS TCP and UDP payloads are parsed and check against common patterns
- Visualized Grafana interfaces for monitoring the results (Filter by IP)
- Unstructured and structured logs are parsed and inserted into Postgres
- All ports are opened and monitored by default
- Easy automation and can be deployed on AWS ec2
- & More features to Explore

## Roadmap
- ~~Refactoring logging~~
- ~~Fixing logger~~
- Code Cleanup
- Switching some servers to twisted 
- Adding graceful connection close (error response)
- Implementing the rest of servers
- Adding some detection logic to the sinffer
- Adding a control panel

## SSH Server and Client Example (Easy to run, configure, edit and test)
```python
from ssh_server import QSSHServer
qsshserver = QSSHServer()
qsshserver.run_server()
```
``` bash
ssh test@127.0.0.1
```
``` bash
INFO:chameleonlogger:['servers', {'status': 'success', 'username': 'test', 'ip': '127.0.0.1', 'server': 'ssh_server', 'action': 'login', 'password': 'test', 'port': 38696}]
```

#### Or

```python
ip= String E.g. 0.0.0.0
port= Int E.g. 400
username= String E.g. Test
password= String E.g. Test
mocking= Boolean or String E.g OpenSSH 7.0
logs= String E.g db, terminal or all
qsshserver = QSSHServer(ip="0.0.0.0",port=400,username="Test",password="Test",mocking="OpenSSH 7.0",logs="terminal")
qsshserver.run_server()
```
``` bash
ssh test@127.0.0.1 -p 400
```
``` bash
INFO:chameleonlogger:['servers', {'status': 'success', 'username': 'test', 'ip': '127.0.0.1', 'server': 'ssh_server', 'action': 'login', 'password': 'test', 'port': 38699}]
```

## Install and run
#### On ubuntu 18 or 19 System (Auto-configure test)
```bash
git clone https://github.com/qeeqbox/chameleon.git
cd chameleon
chmod +x ./run.sh
./run.sh auto_test
open localhost:3000 (username and passowrd: admin)
```

#### On ubuntu 18 or 19 System (Auto-configure dev)
```bash
git clone https://github.com/qeeqbox/chameleon.git
cd chameleon
chmod +x ./run.sh
./run.sh auto_dev
open localhost:3000 (username and passowrd in the docker-compose-dev.yml file)
```

## Requirements (Servers only)
```bash
apt-get update -y && apt-get install -y iptables-persistent tcpdump nmap iputils-ping python python-pip python-psycopg2 lsof psmisc dnsutils
pip install scapy netifaces pyftpdlib sqlalchemy pyyaml paramiko==2.7.1 impacket twisted rdpy==1.3.2 psutil requests
pip install -U requests[socks]
pip install -Iv rsa==4.0
```

## Resources
- Twisted documentation
- Impacket documentation
- Grafana documentation
- Expert Twisted
- robertheaton
- Please let me know if i missed a resource or dependency

## Other Licenses
By using this framework, you are accepting the license terms of each package listed below:
- https://github.com/grafana/grafana/blob/master/LICENSE
- https://www.tcpdump.org/license.html
- https://nmap.org/book/man-legal.html
- https://www.psycopg.org/license/
- https://github.com/tutumcloud/dnsutils/blob/master/LICENSE
- https://github.com/secdev/scapy/blob/master/LICENSE
- https://github.com/al45tair/netifaces/blob/master/LICENSE
- https://github.com/giampaolo/pyftpdlib/blob/master/LICENSE
- https://docs.sqlalchemy.org/en/13/copyright.html
- https://github.com/yaml/pyyaml/blob/master/LICENSE
- https://github.com/paramiko/paramiko/blob/master/LICENSE
- https://github.com/SecureAuthCorp/impacket/blob/master/LICENSE
- https://twistedmatrix.com/trac/
- https://github.com/citronneur/rdpy/blob/master/LICENSE
- https://github.com/giampaolo/psutil/blob/master/LICENSE
- https://github.com/psf/requests/blob/master/LICENSE
- https://github.com/FreeRDP/FreeRDP/blob/master/LICENSE
- https://github.com/filmicpro/SMBClient/blob/master/LICENSE
- https://github.com/TigerVNC/tigervnc/blob/master/LICENCE.TXT

## Disclaimer\Notes
- Almost all servers and emulators are stripped-down - You can adjust that as needed based on the client
- If you are interested in adopting some features in your project - please mention this source somewhere in your project
