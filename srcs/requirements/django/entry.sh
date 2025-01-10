#!/bin/bash

python /app/manage.py migrate

#DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/db_adm_psw)" python manage.py createsuperuser \
# 	--noinput \
# 	--username "$(cat /run/secrets/db_user)" \
# 	--email "$(cat /run/secrets/db_user)"@transcendence.com

python /app/manage.py runserver 0.0.0.0:8080