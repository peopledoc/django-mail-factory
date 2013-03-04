# -*- coding: utf-8 -*-
from . import exceptions
from .forms import MailForm
from .previews import MailPreview


class MailFactory(object):
    mail_form = MailForm
    mail_preview = MailPreview
    mail_map = {}
    form_map = {}
    preview_map = {}

    def register(self, mail_klass, mail_form=None, mail_preview=None):
        """Register a Mail class with optionnally a mail form and preview."""
        if not hasattr(mail_klass, 'template_name'):
            raise exceptions.MailFactoryError(
                "%s needs a template_name parameter to be registered" % (
                    mail_klass.__name__))

        if mail_klass.template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is already registered for %s' % (
                    mail_klass.template_name,
                    self.mail_map[mail_klass.template_name].__name__))

        self.mail_map[mail_klass.template_name] = mail_klass

        mail_form = mail_form or self.mail_form
        self.form_map[mail_klass.template_name] = mail_form

        mail_preview = mail_preview or self.mail_preview
        self.preview_map[mail_klass.template_name] = mail_preview

    def unregister(self, mail_klass):
        """Unregister a Mail class from the factory map."""
        if not mail_klass.template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is not registered' % mail_klass.template_name)

        if self.mail_map[mail_klass.template_name] != mail_klass:
            raise exceptions.MailFactoryError(
                '%s is registered for %s not for %s' % (
                    mail_klass.template_name,
                    self.mail_map[mail_klass.template_name].__name__,
                    mail_klass.__name__))

        key = mail_klass.template_name

        del self.mail_map[key]
        del self.form_map[key]

        if key in self.preview_map:
            del self.preview_map[key]  # TODO: remove 'if' when using factory

    def get_mail_class(self, template_name):
        """Return the registered MailClass for this template name."""
        if not template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is not registered' % template_name)

        return self.mail_map[template_name]

    def get_mail_object(self, template_name, context=None):
        """Return the registered MailClass instance for this template name."""
        MailClass = self.get_mail_class(template_name)

        return MailClass(context)

    def get_mail_form(self, template_name):
        """Return the registered MailForm for this template name."""
        if not template_name in self.form_map:
            raise exceptions.MailFactoryError(
                'No form registered for %s' % template_name)
        return self.form_map[template_name]

    def get_mail_preview(self, template_name):
        """Return the registered MailPreview for this template name."""
        if not template_name in self.preview_map:
            raise exceptions.MailFactoryError(
                'No preview registered for %s' % template_name)
        return self.preview_map[template_name]

    def mail(self, template_name, emails, context, attachments=None,
             from_email=None):
        """Send a mail given its template_name."""
        mail = self.get_mail_object(template_name, context)
        mail.send(emails, attachments, from_email)

    def mail_admins(self, template_name, context,
                    attachments=None, from_email=None):
        """Send a mail given its template name to admins."""
        mail = self.get_mail_object(template_name, context)
        mail.mail_admins(attachments, from_email)

    def get_html_for(self, template_name, context):
        """Preview the body.html mail."""
        mail = self.get_mail_object(template_name, context)
        return mail._render_part('body.html')

    def get_text_for(self, template_name, context):
        """Return the rendered mail text body."""
        mail = self.get_mail_object(template_name, context)
        return mail._render_part('body.txt')

    def get_subject_for(self, template_name, context):
        """Return the rendered mail subject."""
        mail = self.get_mail_object(template_name, context)
        return mail._render_part('subject.txt')

    def get_raw_content(self, template_name, emails, context, from_email=None):
        """Return raw mail source before sending."""
        mail = self.get_mail_object(template_name, context)
        return mail.create_email_msg(emails, from_email=from_email)
