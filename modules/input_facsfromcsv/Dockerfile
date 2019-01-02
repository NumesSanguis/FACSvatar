FROM python:3.7.1-slim

MAINTAINER FACSvatar Stef <stefstruijk@protonmail.ch>

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gcc

WORKDIR /app
COPY requirements.txt facsvatarzeromq.py /app/
RUN pip install -r requirements.txt

COPY input_facsfromcsv /app/input_facsfromcsv

WORKDIR /app/input_facsfromcsv
# part of Docker network and therefore tcp://facsvatar_bridge:5551 resolves
#CMD ["python", "main.py", "--pub_ip", "facsvatar_bridge"]
