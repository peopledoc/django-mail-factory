=========================
The MailFactory Interface
=========================

In daily work mail branding is important because it will call your
custommer to action.

MailFactory comes with a little tool that helps you to try your mails.

To do that, we generate a Django Form so that you will let you provide
a context for your mail.

Here we will explain you how you can customize your administration form.


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
<http://127.0.0.1:8000/admin/mails/>`_ to try out your mails.


Registering a specific form
===========================

This two call are equivalent:

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

We may also want to build a very specific form for our mail.

Let's say we have a share this page mail, with a custom message:

.. code-block:: python

    from mail_factory import factory, BaseMail


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


Creating your application MailForm
==================================

As for BaseMail, you can say that everytime a ``user`` params is
needed in the mail, it will be a ``ModelChoiceField`` on the
``auth.models.User``

Let's do that:

.. code-block:: python

    from django.contrib.auth.models import User
    from mail_factory.forms import MailForm, forms


    class BaseMailForm(MailForm):
        def get_field_for_param(self, param):
            if param == 'user':
                return forms.ModelChoiceField(
                    queryset=User.objects.order_by('last_name', 'first_name'))

            return super(BaseMailForm, self).get_field_for_param(param)

By default, all mail params are created as a ``forms.CharField()``
