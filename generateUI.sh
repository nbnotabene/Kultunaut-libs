#!/bin/bash

cd /home/nb/repos/kultunaut/Kultunaut-libs
source /home/nb/repos/kultunaut/Kultunaut-libs/.venv/bin/activate
.venv/bin/python3 kultunaut/lib/UI.py

timestamp=$(date +"%Y-%m-%d %H:%M:%S")
/usr/bin/git add .
/usr/bin/git commit -m "$timestamp commit"
/usr/bin/git push origin main

