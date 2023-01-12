FROM python:3.7.1-slim

MAINTAINER FACSvatar Stef <stefstruijk@protonmail.ch>

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gcc

WORKDIR /app
COPY requirements.txt facsvatarzeromq.py /app/
RUN pip install -r requirements.txt

ADD process_filterdatachanges /app/process_filterdatachanges

EXPOSE 5573
WORKDIR /app/process_filterdatachanges
# part of Docker network and therefore tcp://facsvatar_bridge:557x resolves
CMD ["python", "main.py", "--pub_ip", "*", "--sub_ip", "facsvatar_facstoblend"]
