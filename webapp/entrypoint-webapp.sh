#!/bin/bash

function postgres_ready(){
python3 << END
import socket
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('postgres',5432))
    s.close()
except socket.error:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 1
done

flask db upgrade

flask run --host=0.0.0.0

