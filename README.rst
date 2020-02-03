###################
Django Mail Factory
###################

.. image:: https://secure.travis-ci.org/peopledoc/django-mail-factory.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/peopledoc/django-mail-factory
.. image:: https://img.shields.io/pypi/v/django-mail-factory.svg
   :target: https://crate.io/packages/django-mail-factory/
.. image:: https://img.shields.io/pypi/dm/django-mail-factory.svg
   :target: https://crate.io/packages/django-mail-factory/

Django Mail Factory lets you manage your email in a multilingual project.

* Authors: Rémy Hubscher and `contributors
  <https://github.com/peopledoc/django-mail-factory/graphs/contributors>`_
* Licence: BSD
* Compatibility: Django 1.11, 2.0, 2.1 and 2.2, python2.7, 3.5, 3.6 and 3.7
* Project URL: https://github.com/peopledoc/django-mail-factory
* Documentation: http://django-mail-factory.rtfd.org/


Hacking
=======

Setup your environment:

::

    git clone https://github.com/peopledoc/django-mail-factory.git
    cd django-mail-factory

Hack and run the tests using `Tox <https://pypi.python.org/pypi/tox>`_ to test
on all the supported python and Django versions:

::

    make test

If you want to give a look at the demo (also used for the tests):

::

    bin/python demo/manage.py syncdb  # create an administrator
    bin/python demo/manage.py runserver

You then need to login on http://localhost:8000/admin, and the email
administration (preview or render) is available at
http://localhost:8000/mail_factory/.


Release
=======

To prepare a new version:

* Create a branch named ``release/<version>``
* In a commit, change the ``CHANGELOG`` and ``VERSION`` file to remove the ``.dev0`` and set the date of the release
* In a second commit, change the ``VERSION`` to the next version number + ``.dev0``
* Create a PR for your branch
* When the PR is merged, tag the first commit with the version number, and create a github release using the ``CHANGELOG``

To release a new version (including the wheel)::

    pip install twine
    python setup.py sdist bdist_wheel
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

And after testing everything works fine on the testing repository::

    twine upload dist/*
