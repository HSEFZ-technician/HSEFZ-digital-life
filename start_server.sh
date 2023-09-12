#!/bin/bash
uwsgi --ini uwsgi.ini
setfacl -m u:web:rwx,g:web:rwx uwsgi.sock
sudo /usr/local/nginx/sbin/nginx -s reload
