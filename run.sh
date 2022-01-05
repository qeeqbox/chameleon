#!/bin/bash

echo -e "\nQeeqBox Chameleon v$(jq -r '.version' info) starter script -> https://github.com/qeeqbox/Chameleon"
echo -e "Current servers (DNS, HTTP Proxy, HTTP, HTTPS, SSH, POP3, IMAP, STMP, RDP, VNC, SMB, SOCK5, TELNET and Postgres)\n"\

if [[ $EUID -ne 0 ]]; then
   echo "You have to run this script with higher privileges" 
   exit 1
fi

echo "[x] System updating"
apt-get update -y
echo "[x] Install requirements"
apt-get install -y curl jq sudo > /dev/null

fix_ports_deploy () {
	echo "[x] Fixing ports"
	cp docker-compose-temp.yml docker-compose-dep.yml
	ports=""
	ports_dockerfile="PORTS="
	for i in $(jq .honeypots[].port config.json); do
	    ports+="      - '$i:$i'\n"
			ports_dockerfile+="$i "
	done
	sed -i '/{temp}/c\'"${ports}"'' docker-compose-dep.yml
	sed -i '$!N;/^\n$/{$q;D;};P;D;' docker-compose-dep.yml
	echo $ports_dockerfile > .env
	sed -i 's/^[ \t]*//;s/[ \t]*$//' .env
}

setup_requirements () {
	echo "[x] Install docker.io xdg-utils linux-headers"
	apt-get install -y linux-headers-$(uname -r) docker.io xdg-utils > /dev/null
	curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	echo "[x] Setting up docker-compose"
	chmod +x /usr/local/bin/docker-compose
	echo "[x] Checking docker & docker-compose"
	which docker-compose && echo "Good"
	which docker && echo "Good"
}

wait_on_web_interface () {
until $(curl --silent --head --fail http://localhost:3000 --output /dev/null); do
sleep 5
done
xdg-open http://localhost:3000
}

test_project () {
	docker-compose -f docker-compose-test.yml up --build --remove-orphan
}

dev_project () {
	docker-compose -f docker-compose-dev.yml up --build --remove-orphan
}

dep_project () {
	docker-compose -f docker-compose-dep.yml up --build --force-recreate --no-deps --remove-orphan
}

stop_containers () {
	echo "[x] Stopping all chameleon containers"
	which docker-compose && docker-compose -f docker-compose-test.yml down -v 2>/dev/null
	which docker-compose && docker-compose -f docker-compose-dev.yml down -v 2>/dev/null
	which docker && docker stop $(docker ps | grep chameleon_ | awk '{print $1}') 2>/dev/null
	which docker && docker kill $(docker ps | grep chameleon_ | awk '{print $1}') 2>/dev/null
}

deploy_aws_project () {
	echo "Will be added later on"
}

test () {
	echo "[x] Init test"
	stop_containers
	wait_on_web_interface &
	setup_requirements
	test_project
	stop_containers
	kill %% 2>/dev/null
}

dev () {
	echo "[x] Init dev"
	stop_containers
	wait_on_web_interface &
	setup_requirements
	dev_project
	stop_containers
	kill %% 2>/dev/null
}

deploy () {
	echo "[x] Init deploy"
	stop_containers
	wait_on_web_interface &
	setup_requirements
	fix_ports_deploy
	dep_project
	stop_containers
	kill %% 2>/dev/null
}

if [[ "$1" == "test" ]]; then
	test
fi

if [[ "$1" == "dev" ]]; then
	dev
fi

if [[ "$1" == "deploy" ]]; then
	deploy
fi

kill %% 2>/dev/null

while read -p "`echo -e '\nChoose an option:\n1) Setup requirements (docker, docker-compose)\n2) Test the project (All servers and Sniffer)\n7) Run deploy\n8) Run dev\n9) Run test\n>> '`"; do
  case $REPLY in
    "1") setup_requirements;;
    "2") test_project;;
	"7") deploy;;
    "8") dev;;
    "9") test;;
    *) echo "Invalid option";;
  esac
done
