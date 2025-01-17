#!/bin/bash

python /app/manage.py makemigrations main

python /app/manage.py migrate

DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/web_adm_psw)" python /app/manage.py createsuperuser \
	--noinput \
	--username "$(cat /run/secrets/web_adm)" \
	--email "$(cat /run/secrets/web_adm)"@transcendence.com

python /app/manage.py runserver 0.0.0.0:8080
