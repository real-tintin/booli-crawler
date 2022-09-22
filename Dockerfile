FROM python:3.9.5

RUN apt-get update
RUN pip install --upgrade pip

ENV ROOT /booli_crawler
WORKDIR ${ROOT}
COPY . ${ROOT}

RUN pip install .[test]
