# -*- coding: utf-8 -*-
from django.contrib.auth.views import password_reset as django_password_reset
from .forms import PasswordResetForm


def password_reset(request, **kwargs):
    """Substitute with the mail_factory PasswordResetForm."""
    if 'password_reset_form' not in kwargs:
        kwargs['password_reset_form'] = PasswordResetForm
    if 'email_template_name' not in kwargs:
        kwargs['email_template_name'] = None

    return django_password_reset(request, **kwargs)
