FROM python:latest

RUN apt-get update && apt-get upgrade -y
RUN pip install --root-user-action=ignore django

RUN django-admin startproject app

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]