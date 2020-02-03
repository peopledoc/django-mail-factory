# -*- coding: utf-8 -*-

from django.contrib.auth.forms import \
    PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode

from mail_factory import factory

from .mails import PasswordResetMail


class PasswordResetForm(DjangoPasswordResetForm):
    """MailFactory PasswordReset alternative."""

    def mail_factory_email(
            self, domain_override=None, email_template_name=None,
            use_https=False, token_generator=default_token_generator,
            from_email=None, request=None, extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)

            if email_template_name is not None:
                mail = factory.get_mail_object(email_template_name, context)
            else:
                mail = PasswordResetMail(context)

            mail.send(emails=[user.email], from_email=from_email)
