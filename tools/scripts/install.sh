#!/usr/bin/env bash

# Install python3, pip and gui tools
apt update && apt upgrade -y

apt install -y python3 python3-pip python3-venv net-tools virtualbox-guest-x11 xinit

# Install python packages
python3 -m venv /home/vagrant/.venv

source /home/vagrant/.venv/bin/activate

python3 -m pip install -r /home/vagrant/game/requirements.txt

# Setup folder for local game files
mkdir -p /home/vagrant/.local/share/Duel_Masters_Game

chown -R vagrant:vagrant /home/vagrant

reboot
