FROM python:3.6.8

#RUN addgroup -g 666 appuser && adduser -D -H -u 666 -G appuser appuser

#USER appuser

WORKDIR /app

ADD webapp/requirements.txt /app/ 
RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 5000

ENV FLASK_APP=webapp

COPY . .

RUN pip install --no-cache-dir -r webapp/requirements.txt

