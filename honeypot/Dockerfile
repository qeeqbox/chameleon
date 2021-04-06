FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && apt-get install -y iptables-persistent tcpdump nmap iputils-ping python python-pip python-psycopg2 lsof psmisc dnsutils libffi-dev libssl-dev
RUN pip install scapy==2.4.4 netifaces==0.10.9 pyftpdlib==1.5.6 sqlalchemy==1.3.23 pyyaml==5.4.1 paramiko==2.7.1 impacket==0.9.22 twisted==20.3.0 psutil==5.8.0 requests==2.25.1 redis==3.5.3 mysql-connector-python==8.0.23 pygments==2.5.2
RUN pip install -U requests[socks]
RUN pip install -Iv rsa==4.0
RUN pip install rdpy==1.3.2
COPY . /honeypot
WORKDIR /honeypot
EXPOSE 21 22 23 25 53 80 110 143 443 445 1080 3306 3389 5900 6379 8080
RUN ["chmod","+x","/honeypot/start.py"]
ENTRYPOINT ["python","/honeypot/start.py"]
