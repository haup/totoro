############################################################
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:xenial

# File Author / Maintainer
MAINTAINER Tim Unkrig

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python3 python3-dev python3-setuptools python3-pip libpq-dev

# Copy the application folder inside the container
RUN cd /
Run git clone https://github.com/haup/totoro.git

RUN cd totoro && git checkout deploy

# Get pip to download and install requirements:
RUN pip3 install -r /totoro/totoro/requirements.txt

# Expose ports
EXPOSE 80

# Set the default directory where CMD will execute
WORKDIR /totoro/totoro

CMD python manage.py runserver
