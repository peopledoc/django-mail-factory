=========================
The MailFactory Interface
=========================

In daily work email branding is important because it will call your
customer to action.

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


    factory.register(SharePageMail, SharePageMailForm)


Define form initial data
========================

You can define ``Meta.initial`` to automatically provide a context for
your mail.

.. code-block:: python

    import datetime
    import uuid

    from django.conf import settings
    from django.core.urlresolvers import reverse_lazy as reverse
    from django import forms
    from mail_factory import factory, MailForm, BaseMail


    class ShareBucketMail(BaseMail):
        template_name = 'share_bucket'
        params = ['first_name', 'last_name', 'comment', 'expiration_date',
                  'activation_url']


    def activation_url():
        return '%s%s' % (
            settings.SITE_URL, reverse('share:index',
                                       args=[str(uuid.uuid4()).replace('-', '')]))


    class ShareBucketForm(MailForm):
        expiration_date = forms.DateField()

        class Meta:
            initial = {'first_name': 'Thibaut',
                       'last_name': 'Dupont',
                       'comment': 'I shared with you documents we talked about.',
                       'expiration_date': datetime.date.today,
                       'activation_url': activation_url}

    factory.register(ShareBucketMail, ShareBucketForm)

Then the mail form will be autopopulated with this data.


Creating your application custom MailForm
=========================================

By default, all email params are represented as a ``forms.CharField()``, which
uses a basic text input.

Let's create a project wide ``BaseMailForm`` that uses a ``ModelChoiceField``
on ``auth.models.User`` each time a ``user`` param is needed in the email.

.. code-block:: python

    from django.contrib.auth.models import User
    from django import forms
    from mail_factory.forms import MailForm


    class BaseMailForm(MailForm):
        def get_field_for_param(self, param):
            if param == 'user':
                return forms.ModelChoiceField(
                    queryset=User.objects.order_by('last_name', 'first_name'))

            return super(BaseMailForm, self).get_field_for_param(param)

Now you need to inherit from this ``BaseMailForm`` to make use of it for your
custom mail forms:

.. code-block:: python

    class MyCustomMailForm(BaseMailForm):
        # your own customizations here

If you want this ``BaseMailForm`` to be used automatically when registering a
mail with no custom form, here's how to do it:

.. code-block:: python

    from mail_factory import MailFactory


    class BaseMailFactory(MailFactory):
        mail_form = BaseMailForm
    factory = BaseMailFactory

And use this new factory everywhere in your code instead of
``mail_factory.factory``.


Previewing your email
=====================

Sometimes however, you don't need or want to render the email, having to
provide some real data (eg a user, a site, some complex model...).

The emails may be written by your sales or marketing team, set up by your
designer, and all of those don't want to cope with the setting up of real data.

All they want is to be able to preview the email, in the different languages
available.

This is where email previewing is useful.

Previewing is available straigh away thanks to sane defaults. It uses the
data returned by ``get_context_data``, which in turn uses the form's
Meta.initial, and in last resort, returns "###".

The preview can thus use fake data: let's take the second example from this
page, the ``SharePageMail``:

.. code-block:: python

    import datetime

    from django.contrib.auth.models import User
    from django.conf import settings

    from mail_factory import factory, MailForm


    class SharePageMailForm(MailForm):
        user = forms.ModelChoiceField(queryset=User.objects.all())
        message = forms.CharField(widget=forms.Textarea)
        date = forms.DateTimeField()

        class Meta:
            initial = {'user': User(first_name='John', last_name='Doe'),
                       'message': 'Some message'}

        def get_context_data(self, **kwargs):
            data = super(SharePageMailForm, self).get_context_data(**kwargs)
            data['date'] = datetime.date.today(),
            return data

    factory.register(SharePageMail, SharePageMailForm)

With this feature, when displaying the mail form in the admin (to render the
email with real data), the email will also be previewed (in the different
available languages) with the fake data provided either by the form's
``get_context_data`` or by Meta.initial.
