.PHONY: docs test clean

bin/python:
	virtualenv .
	bin/python setup.py develop

test: bin/python
	bin/pip install tox
	bin/tox

docs:
	bin/pip install sphinx
	SPHINXBUILD=../bin/sphinx-build $(MAKE) -C docs html $^

clean:
	rm -rf bin .tox include/ lib/ man/ django_mail_factory.egg-info/ build/
