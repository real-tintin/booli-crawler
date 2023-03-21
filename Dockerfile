FROM python:3.9.5

ARG PSEUDO_VERSION=1

RUN apt-get update
RUN pip install --upgrade pip

ENV ROOT /booli_crawler
WORKDIR ${ROOT}
COPY . ${ROOT}

RUN SETUPTOOLS_SCM_PRETEND_VERSION=${PSEUDO_VERSION} pip install .[test]
