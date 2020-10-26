FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && apt-get install -y iptables-persistent tcpdump nmap iputils-ping python python-pip python-psycopg2 lsof psmisc dnsutils libffi-dev libssl-dev
RUN pip install scapy netifaces pyftpdlib sqlalchemy pyyaml paramiko==2.7.1 impacket twisted rdpy==1.3.2 psutil requests redis mysql-connector-python
RUN pip install -U requests[socks]
RUN pip install -Iv rsa==4.0
COPY . /honeypot
WORKDIR /honeypot
RUN ["chmod","+x","/honeypot/start.py"]
CMD ["python","/honeypot/start.py"]
