# -*- coding: utf-8 -*-
from django.conf import settings


class MailPreview(object):
    """Abstract class that helps creating email previews.

    To provide custom preview data, override ``get_context_data`` or
    ``get_value_for_param``.

    """

    def __init__(self, mail_class):
        self.mail_class = mail_class

    def get_preview(self, lang=None):
        """Return a new message instance with preview data."""
        mail = self.mail_class(self.get_context_data())
        return mail.create_email_msg([settings.SERVER_EMAIL], lang=lang)

    def get_html_preview(self, lang=None):
        """Return the html alternative of a message with preview data."""
        message = self.get_preview(lang=lang)
        alternatives = dict((v, k) for k, v in message.alternatives)
        if 'text/html' in alternatives:
            return alternatives['text/html']

    def get_context_data(self):
        """Return preview data."""
        data = {}
        for param in self.mail_class.params:
            data[param] = self.get_value_for_param(param)
        return data

    def get_value_for_param(self, param):
        """Return a value for a given param."""
        return "###"
