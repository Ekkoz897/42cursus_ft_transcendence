all: up

up: 
	docker-compose -f ./srcs/docker-compose.yml up -d

down: 
	docker-compose -f ./srcs/docker-compose.yml down

start: 
	docker-compose -f ./srcs/docker-compose.yml start

stop: 
	docker-compose -f ./srcs/docker-compose.yml stop

fclean: 
	docker-compose -f ./srcs/docker-compose.yml down
	docker rmi django:42 postgres:42
	docker volume rm srcs_web_data
	docker volume rm srcs_db_data

re:
	fclean all

status: 
	docker ps

.PHONY: all, clean, fclean, re