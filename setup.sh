#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root / with sudo!"
   exit 1
fi
apt update --yes
apt dist-upgrade --yes
apt upgrade --yes
apt install --yes git python3 python3-pip python3-dev libpython-dev libqtgui4 libqt4-test libgstreamer1.0-0 libjpeg62-turbo-dev libmbedtls12 libmbedtls-dev screen
echo "############### LINUX DEPENDENCIES DONE - CHECK FOR ERRORS ###############"
exec pip install -r requirements.txt
echo "############### PYTHON DEPENDENCIES DONE - CHECK FOR ERRORS ###############"
echo "############### FULLY COMPLETE - CHECK FOR ERRORS ###############"
exit
