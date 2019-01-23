FROM python:3.6.8

WORKDIR /app

ADD requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "app:app" ]

