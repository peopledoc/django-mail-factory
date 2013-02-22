from base64 import b64encode

from django.conf import settings


class BasePreviewMail(object):
    def get_message(self, lang=None):
        return PreviewMessage(self.mail.create_email_msg(self.get_email_receivers(),
                                                         lang=lang))

    @property
    def mail(self):
        return self.mail_class(self.get_context_data())

    def get_email_receivers(self):
        return [settings.SERVER_EMAIL, ]

    def get_context_data():
        return {}

    @property
    def mail_class(self):
        raise NotImplementedError


class PreviewMessage(object):
    def __init__(self, msg):
        self.msg = msg

        self.alternatives = dict((mimetype, content)
                                 for content, mimetype in self.msg.alternatives)

    def has_body_html(self):
        return 'text/html' in self.alternatives

    @property
    def body_html(self):
        return self.alternatives.get('text/html', '')

    @property
    def subject(self):
        return self.msg.subject

    @property
    def body(self):
        return self.msg.body

    @property
    def body_html_escaped(self):
        return b64encode(self.body_html)
