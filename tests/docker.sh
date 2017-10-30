#!/bin/bash

set -ve

# run simple smoketests to verify docker image build is sane

# start docker container
docker run --name admin -p 8000:8000 -d admin runuwsgi

# setup database and implicitly test running commands
docker exec admin failmap-admin migrate
docker exec admin failmap-admin loaddata development

# index page
curl -s http://localhost:8000 |grep MSPAINT.EXE
# static files
curl -sI http://localhost:8000/static/images/red-dot.png |grep 200\ OK
# compressed static files
curl -sI "http://localhost:8000/static/$(curl -s http://localhost:8000/static/CACHE/manifest.json|sed -n 's,.*\(CACHE/js/.*js\).*,\1,p')"|grep 200\ OK
# admin login
curl -si --cookie-jar cookie --cookie cookie http://localhost:8000/admin/login/|grep 200\ OK
curl -si --cookie-jar cookie --cookie cookie --data "csrfmiddlewaretoken=$(grep csrftoken cookie | cut -f 7)&username=admin&password=faalkaart" http://localhost:8000/admin/login/|grep 302\ Found
