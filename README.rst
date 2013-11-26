###################
Django Mail Factory
###################

.. image:: https://secure.travis-ci.org/novapost/django-mail-factory.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/novapost/django-mail-factory
.. image:: https://pypip.in/v/django-mail-factory/badge.png
   :target: https://crate.io/packages/django-mail-factory/
.. image:: https://pypip.in/d/django-mail-factory/badge.png
   :target: https://crate.io/packages/django-mail-factory/

Django Mail Factory lets you manage your email in a multilingual project.

* Authors: Rémy Hubscher and `contributors
  <https://github.com/novapost/django-mail-factory/graphs/contributors>`_
* Licence: BSD
* Compatibility: Django 1.4+, python2.6 up to python3.3
* Project URL: https://github.com/novapost/django-mail-factory
* Documentation: http://django-mail-factory.rtfd.org/


Hacking
=======

Setup your environment:

::

    git clone https://github.com/novapost/django-mail-factory.git
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
http://localhost:8000/admin/mails/.


Release
=======

To release a new version (including the wheel)::

    pip install wheel
    python setup.py sdist bdist_wheel upload
