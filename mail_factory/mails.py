# -*- coding: utf-8 -*-
from os.path import join

from django.conf import settings
from django.template import Context, TemplateDoesNotExist
from django.template.loader import select_template
from django.utils import translation

from mail_factory import exceptions
from mail_factory.messages import EmailMultiRelated


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

    def __init__(self, context):
        """Create a mail instance from a context."""
        # Create the context
        c = self.get_context_data(**context)
        self.context = Context(c)
        self.lang = self.get_language()

        # Check that all the mandatory context is present.
        for key in self.get_params():
            if not key in context:
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

    def get_attachments(self, attachments):
        """Return the attachments."""
        if attachments:
            return attachments

        return []

    def get_template_part(self, part):
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
        localized = join('mails', self.template_name, self.lang, part)
        templates.append(localized)

        # 2/ fallback: mails/invitation_code/
        fallback = join('mails', self.template_name, part)
        templates.append(fallback)

        # return the list of templates path candidates
        return templates

    def _render_part(self, part):
        """Render a mail part against the mail context.

        Part can be:

          * subject.txt
          * body.txt
          * body.html

        """
        tpl = select_template(self.get_template_part(part))
        cur_lang = translation.get_language()
        try:
            translation.activate(self.lang)
            rendered = tpl.render(self.context)
        finally:
            translation.activate(cur_lang)
        return rendered.strip()

    def create_email_msg(self, emails, from_email=None):
        """Create an email message instance."""

        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        subject = self._render_part('subject.txt')
        try:
            body = self._render_part('body.txt')
        except TemplateDoesNotExist:
            body = ''
        try:
            html_content = self._render_part('body.html')
        except TemplateDoesNotExist:
            html_content = None

        msg = EmailMultiRelated(
            subject, body, from_email, emails,
            headers={'Reply-To': getattr(settings,
                                         "SUPPORT_EMAIL",
                                         settings.DEFAULT_FROM_EMAIL)})
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        return msg

    def send(self, emails, attachments, from_email=None):
        """Create the message and send it to emails."""
        msg = self.create_email_msg(emails, from_email=from_email)

        attachments = self.get_attachments(attachments)

        if attachments:
            for filepath, filename, mimetype in attachments:
                with open(filepath, 'rb') as attachment:
                    if mimetype.startswith('image'):
                        msg.attach_related_file(filepath, mimetype, filename)
                    else:
                        msg.attach(filename, attachment.read(), mimetype)

        msg.send()

    def mail_admins(self, attachments=None, from_email=None):
        """Send email to admins."""
        self.send(settings.ADMINS, attachments, from_email)
