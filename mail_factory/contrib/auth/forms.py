# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.models import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36

from .mails import PasswordResetMail
from mail_factory import factory


class PasswordResetForm(PasswordResetForm):
    """MailFactory PasswordReset alternative."""

    def save(self, domain_override=None,
             subject_template_name=None,  # Not used anymore
             email_template_name=None,  # Mail Factory template name
             mail_object=None,  # Mail Factory Mail object
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            context_params = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }

            from_email = from_email or settings.DEFAULT_FROM_EMAIL

            if email_template_name is not None:
                mail = factory.get_mail_object(email_template_name,
                                               context_params)
            else:
                if mail_object is None:
                    mail_object = PasswordResetMail
                mail = mail_object(context_params)

            mail.send(emails=[user.email],
                      from_email=from_email)
