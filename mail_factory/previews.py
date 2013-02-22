from base64 import b64encode

from django.conf import settings

from mail_factory import exceptions


class PreviewSite(object):
    def __init__(self):
        self.previews = {}

    def register(self, cls):
        """
        Adds a preview to the index.
        """
        preview = cls(site=self)

        index = self.previews.setdefault(preview.module, {})

        index[preview.name] = preview

    def get(self, mail_klass):
        if not self.has(mail_klass):
            raise exceptions.MailFactoryError(
                "The mail class %s is not registered" % (
                    mail_klass.__name__))

        return self.previews[mail_klass.__module__][mail_klass.__name__]

    def has(self, mail_klass):
        return (mail_klass.__module__ in self.previews and
                mail_klass.__name__ in self.previews[mail_klass.__module__])


class BasePreviewMail(object):
    def __init__(self, site):
        self.site = site

    def get_message(self, lang=None):
        return PreviewMessage(self.mail.create_email_msg(self.get_email_receivers(),
                                                         lang=lang))

    @property
    def mail(self):
        if not hasattr(self, '_mail'):
            self._mail = self.mail_class(self.get_context_data())

        return self._mail

    @property
    def module(self):
        return '%s' % self.mail_class.__module__

    @property
    def name(self):
        return '%s' % self.mail_class.__name__

    def get_email_receivers(self):
        return [settings.SERVER_EMAIL, ]

    def get_context_data(**kwargs):
        return kwargs.copy()

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
