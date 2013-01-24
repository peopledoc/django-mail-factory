=========================
The MailFactory Interface
=========================

In daily work email branding is important because it will call your
custommer to action.

MailFactory comes with a little tool that helps you to test your emails.

To do that, we generate a Django Form so that you may provide a context for
your email.

Here's how you can customize your administration form.


Enabling MailFactory administration
===================================

You just need to enable the urls:

:file:`project/urls.py`:

.. code-block:: python

    urlpatterns = (
        # ...
        url(r'^admin/mails/', include('mail_factory.urls')),
        url(r'^admin/', include(admin.site.urls)),
        # ...
    )

Then you can connect to `/admin/mails/
<http://127.0.0.1:8000/admin/mails/>`_ to try out your emails.


Registering a specific form
===========================

These two calls are equivalent:

.. code-block:: python

    from mail_factory import factory, BaseMail


    class InvitationMail(BaseMail):
        template_name = "invitation"
        params = ['user']

    factory.register(InvitationMail)

.. code-block:: python

    from mail_factory import factory, MailForm, BaseMail


    class InvitationMail(BaseMail):
        template_name = "invitation"
        params = ['user']

    factory.register(InvitationMail, MailForm)


Creating a custom MailForm
==========================

We may also want to build a very specific form for our email.

Let's say we have a *share this page* email, with a custom message:

.. code-block:: python

    from mail_factory import factory, BaseMail, MailForm


    class SharePageMail(BaseMail):
        template_name = "share_page"
        params = ['user', 'message', 'date']


    class SharePageMailForm(MailForm):
        user = forms.ModelChoiceField(queryset=User.objects.all())
        message = forms.CharField(widget=forms.Textarea)
        date = forms.DateTimeField()

        class Meta:
            mail_class = SharePageMail


    factory.register(SharePageMail, SharePageMailForm)


Creating your application custom MailForm
=========================================

Let's create a project wide BaseMailForm that uses a ``ModelChoiceField`` on
the ``auth.models.User`` each time a ``user`` param is needed in the email.

.. code-block:: python

    from django.contrib.auth.models import User
    from mail_factory.forms import MailForm, forms


    class BaseMailForm(MailForm):
        def get_field_for_param(self, param):
            if param == 'user':
                return forms.ModelChoiceField(
                    queryset=User.objects.order_by('last_name', 'first_name'))

            return super(BaseMailForm, self).get_field_for_param(param)

By default, all email params are represented as a ``forms.CharField()``, which
uses a basic test input.
