.. django-mail-factory documentation master file, created by
   sphinx-quickstart on Wed Jan 23 17:31:52 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-mail-factory's documentation!
===============================================

Django Mail Factory is a little Django app that let's you manage emails
for your project very easily.

Features
--------

Django Mail Factory has support for:

 * Multilingual support
 * Administration to preview emails
 * Multi-alternatives emails: text and html
 * Attachments
 * HTML inline display of attached images


Other resources
---------------

Fork it on: http://github.com/novagile/django-mail-factory/

Documentation: http://django-mail-factory.rtfd.org/


Get started
-----------

From the github tree::

    pip install -e http://github.com/novagile/django-mail-factory/

or from PyPI once it's available::

    pip install django-mail-factory

Then add ``mail_factory`` to your *INSTALLED_APPS*::

    INSTALLED_APPS = (
        ...
        'mail_factory',
        ...
    )


Create your first mail
----------------------

:file:`my_app/mails/__init__.py`:

.. code-block:: python

    from mail_factory import factory
    from mail_factory.mails import BaseMail

    class WelcomeMail(BaseMail):
        template_name = 'activation_email'
        params = ['user', 'site_name', 'site_url']

    factory.register(WelcomeMail)

Then you must also create the templates:

* :file:`templates/mails/activation_email/subject.txt`

::

    [{{site_name }}] Dear {{ user.first_name }}, your account is created


* :file:`templates/mails/activation_email/body.txt`

::

    Dear {{ user.first_name }},

    Your account has been created for the site {{ site_name }}, and is
    available at {{ site_url }}.

    See you there soon!


    The awesome {{ site_name }} team


* :file:`templates/mails/activation_email/body.html` (optional)


Preview your first mail
-----------------------

For example if you are using the standard `django.contrib.auth` module to
manage your users, your preview will be:

* :file:`my_app/mails/previews.py`

.. code-block:: python

    from django.contrib.auth.models import User
    from django.conf import settings

    from my_app.mails import WelcomeMail

    from mail_factory.previews import BasePreviewMail
    from mail_factory import site

    class WelcomePreviewMail(BasePreviewMail):
        mail_class = WelcomeMail

        def get_context_data(self):
            return {
                'user': User(username='newbie',
                             email='newbie@localhost'),
                'site_name': settings.SITE_NAME,
                'site_url': settings.SITE_URL
            }

    site.register(WelcomePreviewMail)


Send a mail
-----------

**Using the factory**:

.. code-block:: python

    from mail_factory import factory


    factory.mail('activation_email', [user.email],
                 {'user': user,
                  'site_name': settings.SITE_NAME,
                  'site_url': settings.SITE_URL})


**Using the mail class**:

.. code-block:: python

    from my_app.mails import WelcomeMail


    msg = WelcomeMail({'user': user,
                       'site_name': settings.SITE_NAME,
                       'site_url': settings.SITE_URL})
    msg.send([user.email])


How does it work?
-----------------

At startup, all :file:`mails.py` files in your application folders are
automatically discovered and the emails are registered to the factory.

If you want to preview your emails you have to write
all your previews in :file:`mails/previews.py`, previews are
also automatically discovered.

You can then directly call your emails from the factory with their
``template_name``.

It also allows you to list your emails in the administration, preview and test
them by sending them to a custom address with a custom context.


Contents
--------

.. toctree::
   :maxdepth: 2

   api
   template
   interface
