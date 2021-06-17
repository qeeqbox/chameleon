#!/bin/bash
echo -e "[x] Test will run in 120 Secs\n"
sleep 120
honeypots --test --config config_test.json --ip `getent hosts honeypots | awk '{print $1}'` --chameleon
echo "[x] Testing Ping"
ping -c 4 honeypots
echo "[x] Settings up Virtual framebuffer "
Xvfb :100 & 
sleep 5
export DISPLAY=:100
echo "[x] Testing QVNCServer"
echo "test" | vncviewer -autopass honeypots
echo "[x] Testing NMAP #1"
nmap honeypots