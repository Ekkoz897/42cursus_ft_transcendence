#!/bin/bash

if [ ! -f /var/lib/postgresql/data/init.sql ]; then
    touch /var/lib/postgresql/data/init.sql
    
    postgres -D /var/lib/postgresql/data

	psql -c "CREATE DATABASE $(cat /run/secrets/db_name);" 
	psql -c "CREATE USER $(cat /run/secrets/db_user) WITH PASSWORD '$(cat /run/secrets/db_user_psw)';" 
	psql -c "GRANT ALL PRIVILEGES ON DATABASE $(cat /run/secrets/db_name) TO $(cat /run/secrets/db_user);" 
	psql -c "ALTER USER postgres WITH PASSWORD '$(cat /run/secrets/db_adm_psw)';"

	pg_ctl -D /var/lib/postgresql/data stop

fi



postgres -D /var/lib/postgresql/data