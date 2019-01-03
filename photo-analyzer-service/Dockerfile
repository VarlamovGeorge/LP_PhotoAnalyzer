FROM python:3.7.2-stretch

WORKDIR /app

EXPOSE 5000

COPY ./webapp .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "app.py" ]

