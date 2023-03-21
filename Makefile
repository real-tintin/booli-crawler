# Makefile for installing the python package and
# running unit tests in a docker container.
#

.PHONY: install_pkg_and_test

install_pkg_and_test:
	docker build -t booli_crawler .
	docker run booli_crawler python -m pytest
