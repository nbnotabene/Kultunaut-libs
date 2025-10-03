#!/bin/bash

timestamp=$(date +"%Y-%m-%d %H:%M:%S")
echo "$timestamp generateUI.sh"
cd /home/nb/repos/kultunaut/Kultunaut-libs
source /home/nb/repos/kultunaut/Kultunaut-libs/.venv/bin/activate

# /usr/bin/git pull

.venv/bin/python3 -m kultunaut.lib.UI
# /usr/bin/git add .
# /usr/bin/git commit -m "$timestamp commit"
# /usr/bin/git push origin main

