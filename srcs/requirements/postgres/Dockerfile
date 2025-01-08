FROM postgres:latest

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y postgresql && apt-get install -y procps

COPY entry.sh /

RUN chmod +x entry.sh

CMD ["./entry.sh"]