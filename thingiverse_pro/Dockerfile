FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
#    python-dev \
#    python-pip \
    python3-dev \
    python3-pip \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev

RUN pip3 install Scrapy
RUN pip3 install psycopg2-binary

RUN mkdir /html/
RUN mkdir /html/things/
RUN mkdir /html/makes/
RUN mkdir /html/remixes/
RUN mkdir /html/comments/

COPY . .

RUN chmod +x /wait-for-it.sh


