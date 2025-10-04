#!/bin/bash

timestamp=$(date +"%Y-%m-%d %H:%M:%S")
echo "$timestamp generateUI.sh"
CURDIR=$(dirname "$(readlink -f "$0")")
cd $CURDIR
# echo $CURDIR
# 
source $CURDIR/.venv/bin/activate
/usr/bin/git pull
.venv/bin/python3 -m kultunaut.lib.UI

# /usr/bin/git add .
# /usr/bin/git commit -m "$timestamp commit"
# /usr/bin/git push origin main

