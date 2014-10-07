# -*- coding: utf-8 -*-
import base64
from . import exceptions
from .forms import MailForm


class MailFactory(object):
    mail_form = MailForm
    _registry = {}  # Needed: django.utils.module_loading.autodiscover_modules.
    form_map = {}

    def register(self, mail_klass, mail_form=None):
        """Register a Mail class with an optional mail form."""
        if not hasattr(mail_klass, 'template_name'):
            raise exceptions.MailFactoryError(
                "%s needs a template_name parameter to be registered" % (
                    mail_klass.__name__))

        if mail_klass.template_name in self._registry:
            raise exceptions.MailFactoryError(
                '%s is already registered for %s' % (
                    mail_klass.template_name,
                    self._registry[mail_klass.template_name].__name__))

        self._registry[mail_klass.template_name] = mail_klass

        mail_form = mail_form or self.mail_form
        self.form_map[mail_klass.template_name] = mail_form

    def unregister(self, mail_klass):
        """Unregister a Mail class from the factory map."""
        if mail_klass not in self._registry.values():
            raise exceptions.MailFactoryError(
                '%s is not registered' % mail_klass.template_name)

        key = mail_klass.template_name

        del self._registry[key]
        del self.form_map[key]

    def get_mail_class(self, template_name):
        """Return the registered mail class for this template name."""
        if template_name not in self._registry:
            raise exceptions.MailFactoryError(
                '%s is not registered' % template_name)

        return self._registry[template_name]

    def get_mail_object(self, template_name, context=None):
        """Return the registered mail class instance for this template name."""
        mail_class = self.get_mail_class(template_name)
        return mail_class(context)

    def get_mail_form(self, template_name):
        """Return the registered MailForm for this template name."""
        if template_name not in self.form_map:
            raise exceptions.MailFactoryError(
                'No form registered for %s' % template_name)
        return self.form_map[template_name]

    def mail(self, template_name, emails, context, attachments=None,
             from_email=None, headers=None):
        """Send a mail given its template_name."""
        mail = self.get_mail_object(template_name, context)
        mail.send(emails, attachments, from_email, headers)

    def mail_admins(self, template_name, context,
                    attachments=None, from_email=None):
        """Send a mail given its template name to admins."""
        mail = self.get_mail_object(template_name, context)
        mail.mail_admins(attachments, from_email)

    def get_html_for(self, template_name, context,
                     lang=None, cid_to_data=False):
        """Preview the body.html mail."""
        mail = self.get_mail_object(template_name, context)
        mail_content = mail._render_part('body.html', lang=lang)

        if cid_to_data:
            attachments = mail.get_attachments()
            for filepath, filename, mimetype in attachments:
                with open(filepath, 'rb') as attachment:
                    if mimetype.startswith('image'):
                        data_url_encode = 'data:%s;base64,%s' % (
                            mimetype, base64.b64encode(attachment.read()))
                        mail_content = mail_content.replace(
                            'cid:%s' % filename, data_url_encode)
        return mail_content

    def get_text_for(self, template_name, context, lang=None):
        """Return the rendered mail text body."""
        mail = self.get_mail_object(template_name, context)
        return mail._render_part('body.txt', lang=lang)

    def get_subject_for(self, template_name, context, lang=None):
        """Return the rendered mail subject."""
        mail = self.get_mail_object(template_name, context)
        return mail._render_part('subject.txt', lang=lang)

    def get_raw_content(self, template_name, emails, context,
                        lang=None, from_email=None):
        """Return raw mail source before sending."""
        mail = self.get_mail_object(template_name, context)
        return mail.create_email_msg(emails, from_email=from_email,
                                     lang=lang)
