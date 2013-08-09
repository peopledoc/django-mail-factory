===============================
Django default mail integration
===============================

If you use Django Mail Factory, you will definitly want to manage all
your application mails from Django Mail Factory.

Even if your are using some Django generic views that send mails.


Password Reset Mail
===================

Here is an example of how you can use Mail Factory with the
``django.contrib.auth.views.password_reset`` view.

You can first add this pattern in your ``urls.py``:

.. code-block:: python

    url(_(r'^password_reset/$'),
        'mail_factory.contrib.auth.views.password_reset'),
    url(_(r'^password_reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-'
          r'[0-9A-Za-z]{1,20})/$'),
        'django.contrib.auth.views.password_reset_confirm')
    url(_(r'^password_reset/done/$'),
        'django.contrib.auth.views.password_reset_done')


Then you can overload the default templates
``mails/password_reset/subject.txt`` and ``mails/password_reset/body.txt``.

But you can also register your own ``PasswordResetMail``:

.. code-block:: python

    from django.conf import settings
    from mail_factory import factory
    from mail_factory.contrib.auth.mails import PasswordResetMail
    from myapp.mails import AppBaseMail, AppBaseMailForm

    class PasswordResetMail(AppBaseMail, PasswordResetMail):
        """Add the App header + i18n for PasswordResetMail."""


    class PasswordResetForm(AppBaseMailForm):
        class Meta:
            mail_class = PasswordResetMail
            initial = {'email': settings.ADMINS[0][1],
                       'domain': settings.SITE_URL.split('/')[2],
                       'site_name': settings.SITE_NAME,
                       'uid': u'4',
                       'user': 4,
                       'token': '3gg-37af4e5097565a629f2e',
                       'protocol': settings.SITE_URL.split('/')[0].rstrip(':')}


    factory.register(PasswordResetMail, PasswordResetForm)

You can then update your urls.py to use this new form:

.. code-block:: python

    url(_(r'^password_reset/$'),
        'mail_factory.contrib.auth.views.password_reset',
        {'email_template_name': 'password_reset'}),


The default PasswordResetMail is not registered in the factory so that
people that don't use it are not disturb.

If you want to use it as is, you can just register it in your app
``mails.py`` file like that:


.. code-block:: python

    from mail_factory import factory
    from mail_factory.contrib.auth.mails import PasswordResetMail

    factory.register(PasswordResetMail)
