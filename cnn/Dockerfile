FROM python:3.6.8

RUN mkdir /app
WORKDIR /app

EXPOSE 5000

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "app.py" ]

