# -*- coding: utf-8 -*-

from django.contrib.auth.views import \
    PasswordResetView as DjangoPasswordResetView
from django.http import HttpResponseRedirect

from .forms import PasswordResetForm


class PasswordResetView(DjangoPasswordResetView):
    """Substitute with the mail_factory PasswordResetForm."""
    form_class = PasswordResetForm
    email_template_name = None

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'request': self.request,
            'extra_email_context': self.extra_email_context,
        }
        form.mail_factory_email(**opts)
        return HttpResponseRedirect(self.get_success_url())


password_reset = PasswordResetView.as_view()
