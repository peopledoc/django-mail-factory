.PHONY: docs test clean

bin/python:
	virtualenv .
	bin/python setup.py develop

test: bin/python
	bin/pip install tox
	bin/tox

bin/sphinx-build: bin/python
	bin/pip install sphinx

docs: bin/sphinx-build
	bin/pip install sphinx
	SPHINXBUILD=../bin/sphinx-build $(MAKE) -C docs html $^

#: clean - Basic cleanup, mostly temporary files.
clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name __pycache__ -delete


#: distclean - Remove local builds, such as *.egg-info.
distclean: clean
	rm -rf *.egg
	rm -rf *.egg-info


#: maintainer-clean - Remove almost everything that can be re-generated.
maintainer-clean: distclean
	rm -rf build/
	rm -rf dist/
	rm -rf .tox/
