# -*- coding: utf-8 -*-
from mail_factory import exceptions
from mail_factory.forms import mailform_factory
from django.template import TemplateDoesNotExist


class MailFactory(object):
    mail_map = {}
    form_map = {}

    def register(self, mail_klass, mail_form=None):
        """Register a Mail class from the factory map."""
        if hasattr(mail_klass, 'template_name'):
            if mail_klass.template_name not in self.mail_map:
                self.mail_map[mail_klass.template_name] = mail_klass
                if mail_form:
                    self.form_map[mail_klass.template_name] = mail_form
                else:
                    self.form_map[mail_klass.template_name] = \
                        mailform_factory(mail_klass)
            else:
                raise exceptions.MailFactoryError(
                    '%s is already register for %s.' % (
                        mail_klass.template_name,
                        self.mail_map[mail_klass.template_name].__name__))
        else:
            raise exceptions.MailFactoryError(
                "%s doesn't have a template_name and cannot be register." % (
                    mail_klass.__name__))

    def unregister(self, mail_klass):
        """Unregister a Mail class from the factory map."""
        if mail_klass.template_name in self.mail_map:
            if self.mail_map[mail_klass.template_name] == mail_klass:
                del self.mail_map[mail_klass.template_name]
                del self.form_map[mail_klass.template_name]
            else:
                raise exceptions.MailFactoryError(
                    '%s is registered for %s not for %s.' % (
                        mail_klass.template_name,
                        self.mail_map[mail_klass.template_name].__name__,
                        mail_klass.__name__))
        else:
            raise exceptions.MailFactoryError(
                '%s is not registered.' % mail_klass.template_name)

    def _get_mail_object(self, template_name):
        """Returns the MailClass from the registration map and its
        template_name."""
        if template_name in self.mail_map:
            return self.mail_map[template_name]
        else:
            raise exceptions.MailFactoryError(
                '%s is not register.' % template_name)

    def _get_mail_form(self, template_name):
        if template_name in self.mail_map:
            try:
                return self.form_map[template_name]
            except KeyError:
                raise exceptions.MailFactoryError(
                    "%s is register but doesn't have a form."
                    "Please restart your server" % template_name)

    def mail(self, template_name, emails, context,
             attachments=None, from_email=None):
        """Send a mail from the template_name."""
        MailClass = self._get_mail_object(template_name)
        msg = MailClass(context)
        msg.send(emails, attachments, from_email)

    def mail_admins(self, template_name, context,
                    attachments=None, from_email=None):
        """Send the mail to admins."""
        MailClass = self._get_mail_object(template_name)
        msg = MailClass(context)
        msg.mail_admins(attachments, from_email)

    def get_html_for(self, template_name, context):
        """Preview the body.html mail."""
        MailClass = self._get_mail_object(template_name)
        msg = MailClass(context)
        try:
            return msg._render_part('body.html')
        except TemplateDoesNotExist:
            return '<pre>'+msg._render_part('body.txt')+'</pre>'

    def get_raw_content(self, template_name, emails, context, from_email=None):
        """Return raw mail source before sending."""
        MailClass = self._get_mail_object(template_name)
        msg = MailClass(context)
        return msg.create_email_msg(emails, from_email=from_email)
