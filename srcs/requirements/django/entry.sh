#!/bin/bash

python /app/manage.py migrate

python /app/manage.py runserver localhost:8080