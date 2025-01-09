FROM python:latest

RUN apt-get update && apt-get upgrade -y
RUN pip install --root-user-action=ignore django

RUN pip install --root-user-action=ignore psycopg2

RUN django-admin startproject app

WORKDIR /app

RUN python manage.py startapp main

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

#CMD ["tail", "-f", "/dev/null"]