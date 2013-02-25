# -*- coding: utf-8 -*-
from mail_factory import exceptions
from mail_factory.forms import mailform_factory, MailForm


class MailFactory(object):
    mail_form = MailForm
    mail_map = {}
    form_map = {}
    preview_map = {}

    def register(self, mail_klass, mail_form=None, mail_preview=None):
        """Register a Mail class from the factory map."""
        if not hasattr(mail_klass, 'template_name'):
            raise exceptions.MailFactoryError(
                "%s doesn't have a template_name and cannot be registered." % (
                    mail_klass.__name__))

        if mail_klass.template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is already registered for %s.' % (
                    mail_klass.template_name,
                    self.mail_map[mail_klass.template_name].__name__))

        self.mail_map[mail_klass.template_name] = mail_klass

        if mail_form:
            self.form_map[mail_klass.template_name] = mail_form
        else:
            self.form_map[mail_klass.template_name] = \
                mailform_factory(mail_klass, self.mail_form)

        if mail_preview:
            self.preview_map[mail_klass.template_name] = mail_preview

    def unregister(self, mail_klass):
        """Unregister a Mail class from the factory map."""
        if not mail_klass.template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is not registered.' % mail_klass.template_name)

        if self.mail_map[mail_klass.template_name] != mail_klass:
            raise exceptions.MailFactoryError(
                '%s is registered for %s not for %s.' % (
                    mail_klass.template_name,
                    self.mail_map[mail_klass.template_name].__name__,
                    mail_klass.__name__))

        key = mail_klass.template_name

        del self.mail_map[key]
        del self.form_map[key]

        if key in self.preview_map:
            del self.preview_map[key]

    def get_mail_class(self, template_name):
        """Returns the MailClass from the registration map and its
        template_name."""
        if not template_name in self.mail_map:
            raise exceptions.MailFactoryError(
                '%s is not registered.' % template_name)

        return self.mail_map[template_name]

    def get_mail_object(self, template_name, context=None):
        """Returns the MailClass instance from the registration map and its
        template_name."""
        MailClass = self.get_mail_class(template_name)

        return MailClass(context)

    def get_mail_form(self, template_name):
        """Returns the MailForm instance from the registration map and its
        template_name."""
        if template_name in self.mail_map:
            try:
                return self.form_map[template_name]
            except KeyError:
                raise exceptions.MailFactoryError(
                    "%s is registered but doesn't have a form."
                    "Please restart your server" % template_name)

    def get_mail_preview(self, template_name):
        """Returns the PreviewMail instance from the registration map and its
        template_name."""
        if template_name in self.mail_map:
            try:
                return self.preview_map[template_name]
            except KeyError:
                raise exceptions.MailFactoryError(
                    "%s is registered but doesn't have a form."
                    "Please restart your server" % template_name)

    def mail(self, template_name, emails, context,
             attachments=None, from_email=None):
        """Send a mail from the template_name."""
        self.get_mail_object(template_name, context) \
            .send(emails, attachments, from_email)

    def mail_admins(self, template_name, context,
                    attachments=None, from_email=None):
        """Send the mail to admins."""
        self.get_mail_object(template_name, context) \
            .mail_admins(attachments, from_email)

    def get_html_for(self, template_name, context):
        """Preview the body.html mail."""
        return self.get_mail_object(template_name, context) \
                   ._render_part('body.html')

    def get_text_for(self, template_name, context):
        """Return the rendered mail text body."""
        return self.get_mail_object(template_name, context) \
                   ._render_part('body.txt')

    def get_subject_for(self, template_name, context):
        """Return the rendered mail subject."""
        return self.get_mail_object(template_name, context) \
                   ._render_part('subject.txt')

    def get_raw_content(self, template_name, emails, context, from_email=None):
        """Return raw mail source before sending."""
        return self.get_mail_object(template_name, context) \
                   .create_email_msg(emails, from_email=from_email)
