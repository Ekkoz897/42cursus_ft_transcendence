#!/bin/bash

if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
	
	initdb --pwfile=/run/secrets/db_adm_psw -A md5 /var/lib/postgresql/data
   
	pg_ctl -D /var/lib/postgresql/data start

	PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "CREATE DATABASE $(cat /run/secrets/db_name);" 
	PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "CREATE USER $(cat /run/secrets/db_user) WITH PASSWORD '$(cat /run/secrets/db_user_psw)';" 
	PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "GRANT ALL PRIVILEGES ON DATABASE $(cat /run/secrets/db_name) TO $(cat /run/secrets/db_user);" 
	PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "ALTER USER postgres WITH PASSWORD '$(cat /run/secrets/db_adm_psw)';"

	pg_ctl -D /var/lib/postgresql/data stop

	echo "host all all all md5" >> /var/lib/postgresql/data/pg_hba.conf
	
   	touch /var/lib/postgresql/data/init.sql
fi

postgres -D /var/lib/postgresql/data