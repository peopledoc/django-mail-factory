# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.encoding import smart_str

from mail_factory.messages import EmailMultiRelated


class PreviewMessage(EmailMultiRelated):
    def has_body_html(self):
        """Test if a message contains an alternative rendering in text/html"""
        return 'text/html' in self.rendering_formats

    @property
    def body_html(self):
        """Return an alternative rendering in text/html"""
        return self.rendering_formats.get('text/html', '')

    @property
    def rendering_formats(self):
        return dict((v, k) for k, v in self.alternatives)


class BasePreviewMail(object):
    """Abstract class that helps creating preview emails.

    You also may overwrite:
     * get_context_data: to add global context such as SITE_NAME
    """
    message_class = PreviewMessage

    def get_message(self, lang=None):
        """Return a new message instance based on your MailClass"""
        return self.mail.create_email_msg(self.get_email_receivers(),
                                          lang=lang,
                                          message_class=self.message_class)

    @property
    def mail(self):
        return self.mail_class(self.get_context_data())

    def get_email_receivers(self):
        """Returns email receivers."""
        return [settings.SERVER_EMAIL, ]

    def get_context_data():
        """Returns automatic context_data."""
        return {}

    @property
    def mail_class(self):
        raise NotImplementedError
