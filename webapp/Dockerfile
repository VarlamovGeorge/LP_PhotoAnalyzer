FROM python:3.6.8-alpine

#RUN addgroup -g 666 appuser && adduser -D -H -u 666 -G appuser appuser

#USER appuser

WORKDIR /app

EXPOSE 5000

ENV FLASK_APP=webapp

COPY . .

RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r webapp/requirements.txt

