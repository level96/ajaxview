FROM ubuntu:14.04

MAINTAINER Trung Phan <t.phan.an@level96.de>

USER root

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:nginx/stable

# Adds additional repo
RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip
RUN apt-get install -y python-setuptools
RUN apt-get install -y python-dev
RUN apt-get install -y vim

RUN easy_install pip
RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip -q install -r requirements.txt

ADD . /app/

# Just for local developing
VOLUME ['/app/logs', '/app/media']

# Sets permissions
RUN chmod +x /app/run_tests.sh

CMD ["/app/run_testsp.sh"]