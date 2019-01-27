
clean:
	docker system prune -f

run: clean
	docker-compose build
	docker-compose up

down:
	docker-compose down

psql:
	docker exec -it `docker ps -q --filter="ancestor=postgres:11.1-alpine"` /bin/bash

