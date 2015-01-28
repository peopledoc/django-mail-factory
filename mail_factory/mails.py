# -*- coding: utf-8 -*-
from os.path import join

import html2text

from django.conf import settings
from django.template import Context, TemplateDoesNotExist
from django.template.loader import select_template
from django.utils import translation

from . import exceptions
from .messages import EmailMultiRelated


class BaseMail(object):
    """Abstract class that helps creating emails.

    You need to define:
     * template_name : The template_dir in which to find parts. (subject, body)
     * params : Mandatory variable in the context to render the mail.

    You also may overwrite:
     * get_params: to build the mandatory variable list in the mail context
     * get_context_data: to add global context such as SITE_NAME
     * get_template_part: to get the list of possible paths to get parts.
    """

    def __init__(self, context=None):
        """Create a mail instance from a context."""
        # Create the context
        context = context or {}
        c = self.get_context_data(**context)
        self.context = Context(c)
        self.lang = self.get_language()

        # Check that all the mandatory context is present.
        for key in self.get_params():
            if key not in context:
                raise exceptions.MissingMailContextParamException(repr(key))

    def get_language(self):
        # Auto detect the current language
        return translation.get_language()  # Get current language

    def get_params(self):
        """Returns the list of mandatory context variables."""
        return self.params

    def get_context_data(self, **kwargs):
        """Returns automatic context_data."""
        return kwargs.copy()

    def get_attachments(self, attachments=None):
        """Return the attachments."""
        return attachments or []

    def get_template_part(self, part, lang=None):
        """Return a mail part

          * subject.txt
          * body.txt
          * body.html

        Try in order:

        1/ localized: mails/{{ template_name }}/fr/
        2/ fallback:  mails/{{ template_name }}/

        """
        templates = []
        # 1/ localized: mails/invitation_code/fr/
        localized = join('mails', self.template_name, lang or self.lang, part)
        templates.append(localized)

        # 2/ fallback: mails/invitation_code/
        fallback = join('mails', self.template_name, part)
        templates.append(fallback)

        # return the list of templates path candidates
        return templates

    def _render_part(self, part, lang=None):
        """Render a mail part against the mail context.

        Part can be:

          * subject.txt
          * body.txt
          * body.html

        """
        tpl = select_template(self.get_template_part(part, lang=lang))
        cur_lang = translation.get_language()
        try:
            translation.activate(lang or self.lang)
            rendered = tpl.render(self.context)
        finally:
            translation.activate(cur_lang)
        return rendered.strip()

    def create_email_msg(self, emails, attachments=None, from_email=None,
                         lang=None, message_class=EmailMultiRelated,
                         headers=None):
        """Create an email message instance."""

        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        subject = self._render_part('subject.txt', lang=lang).strip()
        try:
            body = self._render_part('body.txt', lang=lang)
        except TemplateDoesNotExist:
            body = None
        try:
            html_content = self._render_part('body.html', lang=lang)
        except TemplateDoesNotExist:
            html_content = None

        # If we have neither a html or txt template
        if html_content is None and body is None:
            raise TemplateDoesNotExist(
                "Txt and html templates have not been found")

        # If we have the html template only, we build automatically
        # txt content.
        if html_content is not None and body is None:
            h = html2text.HTML2Text()
            body = h.handle(html_content)

        if headers is None:
            reply_to = getattr(settings, "NO_REPLY_EMAIL", None)
            if not reply_to:
                reply_to = getattr(settings, "SUPPORT_EMAIL",
                                   settings.DEFAULT_FROM_EMAIL)

            headers = {'Reply-To': reply_to}

        msg = message_class(subject, body, from_email, emails, headers=headers)
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        attachments = self.get_attachments(attachments)

        if attachments:
            for filepath, filename, mimetype in attachments:
                with open(filepath, 'rb') as attachment:
                    if mimetype.startswith('image'):
                        msg.attach_related_file(filepath, mimetype, filename)
                    else:
                        msg.attach(filename, attachment.read(), mimetype)
        return msg

    def send(self, emails, attachments=None, from_email=None, headers=None):
        """Create the message and send it to emails."""
        message = self.create_email_msg(emails, attachments=attachments,
                                        from_email=from_email, headers=headers)
        message.send()

    def mail_admins(self, attachments=None, from_email=None):
        """Send email to admins."""
        self.send([a[1] for a in settings.ADMINS], attachments, from_email)
