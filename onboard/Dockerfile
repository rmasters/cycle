FROM python:3

ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir /app
ADD . /app
WORKDIR /app

