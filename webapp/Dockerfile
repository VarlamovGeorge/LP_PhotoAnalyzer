FROM python:3.7.2-stretch

WORKDIR /app

EXPOSE 5000

ENV FLASK_APP=webapp

COPY ./webapp webapp

RUN pip install --no-cache-dir -r webapp/requirements.txt

CMD [ "flask", "run", "--host=0.0.0.0" ]

