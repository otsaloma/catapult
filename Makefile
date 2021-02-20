# -*- coding: utf-8-unix -*-

check:
	flake8 .
	flake8 bin/*

clean:
	rm -rf build
	rm -rf dist
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__

test:
	py.test -xs .

.PHONY: check clean test
