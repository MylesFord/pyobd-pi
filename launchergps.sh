#!/bin/sh
#launcher.sh
#navitate to home directory then to this directory then execute python script then home
cd /
cd home/pi/pyobd-pi
sudo systemctl stop gpsd.socket
sudo systemctl disable
sudo killall gpsd
sleep 1s
sudo python setgps10hz.py
sleep 1s
sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock
