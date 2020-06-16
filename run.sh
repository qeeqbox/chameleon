echo -e "\nQeeqBox Chameleon v$(jq -r '.version' info) starter script -> https://github.com/qeeqbox/Chameleon"
echo -e "Current servers (DNS, HTTP Proxy, HTTP, HTTPS, SSH, POP3, IMAP, STMP, RDP, VNC, SMB, SOCK5, TELNET and Postgres)\n"\

setup_requirements () {
	sudo apt update -y
	sudo apt install -y linux-headers-$(uname -r) docker.io jq
	sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
	which docker-compose && echo "Good"
	which docker && echo "Good"
}

test_project () {
	sudo docker-compose -f docker-compose-test.yml up --build
}

dev_project () {
	sudo docker-compose -f docker-compose-dev.yml up --build
}

deploy_aws_project () {
	echo "Will be added later on"
}

auto_configure_test () {
	setup_requirements
	test_project
}

auto_configure_dev () {
	setup_requirements
	dev_project
}

if [[ "$1" == "auto_test" ]]; then
	auto_configure_test
	exit 
fi

if [[ "$1" == "auto_dev" ]]; then
	auto_configure_dev
	exit 
fi

while read -p "`echo -e '\nChoose an option:\n1) Setup requirements (docker, docker-compose)\n2) Test the project (All servers and Sniffer)\n8) Run auto dev\n9) Run auto test\n>> '`"; do
  case $REPLY in
    "1") setup_requirements;;
    "2") test_project;;
    "8") auto_configure_dev;;
    "9") auto_configure_test;;
    *) echo "Invalid option";;
  esac
done
