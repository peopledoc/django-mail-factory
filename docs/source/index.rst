.. django-mail-factory documentation master file, created by
   sphinx-quickstart on Wed Jan 23 17:31:52 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-mail-factory's documentation!
===============================================

Django Mail Factory is a little Django app that let's you manage mails
for your app very easily.

Features
--------

Django Mail Factory has support for:

 * Multilingual support
 * Administration to preview mails
 * MultiAlternative Mails
 * Attachments
 * HTML inline display of attached images

Other ressources
----------------

Fork it on:

 * http://github.com/novagile/django-mail-factory/
 * http://django-mail-factory.rtfd.org/


Get started
-----------

From the github tree::

    pip install -e http://github.com/novagile/django-mail-factory/

or after the first release::

    pip intall django-mail-factory

Then add mail_factory to your INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'mail_factory',
        ...
    )


Create your first mail
----------------------

**my_app/mails.py**::

    from mail_factory import factory
    from mail_factory.mails import BaseMail

    class EmailActivation(BaseMail):
        template_name = 'email_activation'
        params = ['user', 'end_date', 'site_name', 'site_url']

    factory.register(EmailActivation)

Then you must also create:

    * **templates/mails/email_activation/subject.txt**
    * **templates/mails/email_activation/body.txt**
    * **templates/mails/email_activation/body.html** (optional)


Send a mail
-----------

**Using the factory**::

    ...
    from mail_factory import factory

    def create_user(request):
        ...
        form = UserCreationForm(request.POST)
        user = form.save()

        ...
        
        factory.mail('email_activation', [user.email],
                     {'user': user,
                     'end_date': now()+timedelta(days=10),
                     'site_name': settings.SITE_NAME,
                     'site_url': settings.SITE_URL})

        return HttpResponse('User created, a mail has been send')


**Using the mail class**::

    from my_app.mails import EmailActivation

    ...

    msg = EmailActivation({
        'user': user,
        'end_date': now()+timedelta(days=10),
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL})
    msg.send([user.email])


How it works?
-------------

At startup, all ``mails.py`` files in your app are autodiscover to
register your mails in the factory.

This allows you to directly call your mails from the factory with
their ``template_name``.

It also allows you to list your mails in the administration, preview
you them and test by sending them to a custom address with a custom
context.



Contents
--------

.. toctree::
   :maxdepth: 2

   api
   template
