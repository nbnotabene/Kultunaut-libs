#!/bin/bash
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
echo "$timestamp fetchKult.sh"
cd /home/nb/repos/kultunaut/Kultunaut-libs
source /home/nb/repos/kultunaut/Kultunaut-libs/.venv/bin/activate
/usr/bin/git pull
.venv/bin/python3 fetchKult.py


