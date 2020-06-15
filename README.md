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
- Visualized Grafana interfaces for monitoring the results (Refresh time set to 5 seconds)
- Unstructured and structured logs are parsed and inserted into Postgres
- All ports are opened and monitored by default
- Easy automation and can be deployed on AWS ec2
- & More features to Explore

## Roadmap
- ~~Refactoring logging~~
- Code Cleanup
- Adding error response
- Implementing the rest of servers
- Adding some detection logic to the sinffer
- Adding a control panel

## Example
#### Easy to run and configure (Default configuration)
```python
from ssh_server import QSSHServer
qsshserver = QSSHServer()
qsshserver.run_server()
```

#### Or, edit the configuration
```python
ip= String E.g. 0.0.0.0
port= Int E.g. 22
username= String E.g. Test
password= String E.g. Test
mocking= Boolean or String E.g OpenSSH 7.0
logs= String E.g db, terminal or all

qsshserver = QSSHServer(ip="0.0.0.0",port=22,username="Test",password="Test",mocking="OpenSSH 7.0",logs="terminal")
qsshserver = QSSHServer()
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
- Almost all servers are stripped-down - You can adjust that as needed based on the client
- If you are interested in adopting some features in your project - please mention this source somewhere in your project
