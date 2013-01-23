===================
Hacking MailFactory
===================

MailFactory is a tool to helps you manage your mails in the real world.

That means that for the same mail, regarding to the context, you may
want different brandings, different languages, etc.


Select language for your mails
==============================

Sometimes regarding to the context, you may want to select the
language for the mail.

Let say that our user have a ``language_code`` as a profile attribute:

.. code-block:: python

    class ActivationMail(BaseMail): 
        template_name = 'activation'        
        params = ['user', 'activation_key']

        def get_language(self):
            lang = BaseMail.get_language(self)  # Get the current language
            try:
                # Try to get the user language choice
                lang = self.context['user'].get_profile().language_code
            except:
                pass
            return lang


Force a param for all mails
===========================

You can overwrite ``get_params`` to add some mandatory parameters for
all mails:

.. code-block:: python

    class MyProjectBaseMail(BaseMail):         

        def get_params(self):
            return self.params + ['user']

        def get_language(self):
            lang = self.context['user'].get_profile().language_code
            return lang

    class ActivationMail(MyProjectBaseMail):
        template_name = 'activation'
        params = ['activation_key']

With this, your are certain that every mail would be send it the right
language since an error will be raise if the user ``language_code`` is
not found.


Add context data
================

If you have some information that must be added to every mail context,
you can put them here:

.. code-block:: python

    class MyProjectBaseMail(BaseMail):         

        def get_context_data(self, **kwargs):
            data = BaseMail.get_context_data(self, **kwargs)
            data['site_name'] = settings.SITE_NAME
            data['site_url'] = settings.SITE_URL
            return data


Add attachments
===============

Same thing here, if your branding need a logo or header in every
mails, you can define it here:


.. code-block:: python

    from django.contrib.staticfiles import finders

    class MyProjectBaseMail(BaseMail):         

        def get_attachments(self, attachements):
            attachments = BaseMail.get_attachments(attachments) || []
            attachments.append((finders.find('mails/header.png'),
                                'header.png', 'image/png'))
            return attachments


Template loading
================

By default, the template parts will be search in:

   * templates∕mails/{{ template_name }}/{{ language_code }}/
   * templates∕mails/{{ template_name }}/

But you may want to search in different location. ie:

  * templates/{{ site.domain }}/mails/{{ template_name }}/

To do that, you can override the ``get_template_part`` method:

.. code-block:: python

    class ActivationMail(BaseMail):
        template_name = 'activation'
        params = ['activation_key', 'site']

        def get_template_part(self, part):
            """Return a mail part (body, html body or subject) template
            
            Try in order:
            
            1/ domain specific localized:
                example.com/mails/activation/fr/
            2/ domain specific:
                example.com/mails/activation/
            3/ localized: 
                mails/activation/fr/
            4/ fallback:
                mails/activation/
            
            """
            templates = []

            site = self.context.get('site')
            if hasattr(site, 'domain'):
                # 1. {{ domain_name }}/mails/{{ template_name }}/{{ language_code}}/
                templates.append(path.join(site.domain,
                                           'mails',
                                           self.template_name,
                                           self.lang,
                                           part)
                # 2. {{ domain_name }}/mails/{{ template_name }}/
                templates.append(path.join(site.domain,
                                           'mails',
                                           self.template_name,=
                                           part)
            
            return templates + BaseMail.get_template_part(self, part)

``get_template_part`` returns a list of template and will take the first one available.
