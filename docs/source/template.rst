==============
Mail templates
==============

When you want a multi-alternatives email, you need to provide a subject, the
``text/plain`` body and the ``text/html`` body.

All these parts are loaded from your email template directory.

:file:`templates/mails/invitation/subject.txt`:

.. code-block:: django

    {% load i18n %}{% blocktrans %}[{{ site_name }}] Invitation to the beta{% endblocktrans %}

A little warning: the subject needs to be on a single line

You can also create a different subject file for each language:

:file:`templates/mails/invitation/en/subject.txt`:

.. code-block:: django

    [{{ site_name }}] Invitation to the beta

:file:`templates/mails/invitation/body.txt`:

.. code-block:: django

    {% load i18n %}{% blocktrans with full_name=user.get_full_name expiration_date=expiration_date|date:"l d F Y" %}
    Dear {{ full_name }},

    You just received an invitation to connect to our beta program.

    Please click on the link below to activate your account:

    {{ activation_url }}

    This link will expire on: {{ expiration_date }}

    {{ site_name }}
    -------------------------------
    If you need help for any purpose, please contact us at {{ support_email }}
    {% endblocktrans %}


If you don't provide a ``body.html`` the mail will be sent in ``text/plain``
only, if it is present, it will be added as an alternative and displayed if the
user's mail client handles html emails.

:file:`templates/mails/invitation/body.html`:

.. code-block:: html

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>{{ site_name }}</title>
    </head>
    <body>
        <p><img src="cid:header.png" alt="{{ site_name }}" /></p>
        <h1>{% trans 'Invitation to the beta' %}</h1>
        <p>{% blocktrans with full_name=user.get_full_name %}Dear {{ full_name }},{% endblocktrans %}</p>
        <p>{% trans "You just received an invitation to connect to our beta program:" %}</p>
        <p>{% trans 'Please click on the link below to activate your account:' %}</p>
        <p><a href="{{ activation_url }}" target="_blank">{{ activation_url }}</a></p>
        <p>{{ site_name }}</p>
        <p>{% blocktrans %}If you need help for any purpose, please contact us at
            <a href="mailto:{{ support_email }}">{{ support_email }}</a>{% endblocktrans %}</p>
    </body>
    </html>
