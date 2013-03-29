===================
Hacking MailFactory
===================

MailFactory is a tool to help you manage your emails in the real world.

That means that for the same email, regarding the context, you may want a
different branding, different language, etc.


Specify the language for your emails
====================================

If you need to specify the language for your email, other than the currently
used language, you can do so by overriding the ``get_language`` method on your
custom class.

Let's say that our user has a ``language_code`` as a profile attribute:

.. code-block:: python

    class ActivationEmail(BaseMail):
        template_name = 'activation'
        params = ['user', 'activation_key']

        def get_language(self):
            return self.context['user'].get_profile().language_code


Force a param for all emails
============================

You can also overriding the ``get_params`` method of a custom ancestor class to
add some mandatory parameters for all your emails:

.. code-block:: python

    class MyProjectBaseMail(BaseMail):

        def get_params(self):
            params = super(MyProjectBaseMail, self).get_params()
            return params.append('user')

    class ActivationEmail(MyProjectBaseMail):
        template_name = 'activation'
        params = ['activation_key']

This way, all your emails will have the user in the context by default.


Add context data
================

If you have some information that must be added to every email context, you can
put them here:

.. code-block:: python

    class MyProjectBaseMail(BaseMail):

        def get_context_data(self, **kwargs):
            data = super(MyProjectBaseMail, self).get_context_data(**kwargs)
            data['site_name'] = settings.SITE_NAME
            data['site_url'] = settings.SITE_URL
            return data


Add attachments
===============

Same thing here, if your branding needs a logo or a header in every emails, you
can define it here:


.. code-block:: python

    from django.contrib.staticfiles import finders

    class MyProjectBaseMail(BaseMail):

        def get_attachments(self, files=None):
            attach = super(MyProjectBaseMail, self).get_attachments(files)
            attach.append((finders.find('mails/header.png'),
                           'header.png', 'image/png'))
            return attach


Template loading
================

By default, the template parts will be searched in:

* :file:`templates∕mails/{{ template_name }}/{{ language_code }}/`
* :file:`templates∕mails/{{ template_name }}/`

But you may want to search in different locations, ie:

* :file:`templates/{{ site.domain }}/mails/{{ template_name }}/`

To do that, you can override the ``get_template_part`` method:

.. code-block:: python

    class ActivationEmail(BaseMail):
        template_name = 'activation'
        params = ['activation_key', 'site']

        def get_template_part(self, part):
            """Return a mail part (body, html body or subject) template

            Try in order:

            1/ domain specific localized:
                example.com/mails/activation/fr/
            2/ domain specific:
                example.com/mails/activation/
            3/ default localized:
                mails/activation/fr/
            4/ fallback:
                mails/activation/

            """
            templates = []

            site = self.context['site']
            # 1/ {{ domain_name }}/mails/{{ template_name }}/{{ language_code}}/
            templates.append(path.join(site.domain,
                                       'mails',
                                       self.template_name,
                                       self.lang,
                                       part))
            # 2/ {{ domain_name }}/mails/{{ template_name }}/
            templates.append(path.join(site.domain,
                                       'mails',
                                       self.template_name,
                                       part))
            # 3/ and 4/ provided by the base class
            base_temps = super(MyProjectBaseMail, self).get_template_part(part)
            return templates + base_temps

``get_template_part`` returns a list of template and will take the first one
available.
