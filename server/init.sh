#/bin/bash

nginx
cd /root/inspector/
gunicorn app:app -c gunicorn.conf.py
