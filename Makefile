
run: clean
	docker-compose build
	docker-compose up

down:
	docker-compose down

clean:
	docker system prune -f

psql:
	docker exec -it `docker ps -q --filter="ancestor=postgres:11.1-alpine"` /bin/bash

