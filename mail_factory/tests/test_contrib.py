# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetDoneView
)
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from mail_factory import factory
from mail_factory.contrib.auth.mails import PasswordResetMail
from mail_factory.contrib.auth.views import PasswordResetView, password_reset

urlpatterns = [
    url(r'^reset/$', password_reset, name="reset"),
    url(r'^reset_template_name/$',
        PasswordResetView.as_view(email_template_name="password_reset"),
        name="reset_template_name"),

    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    url(r'^password_reset/done/$',
        PasswordResetDoneView.as_view(), name="password_reset_done"),
    url(r'^admin/', admin.site.urls),
]


def with_registered_mail_klass(mail_klass):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            factory.register(mail_klass)
            result = func(*args, **kwargs)
            factory.unregister(mail_klass)
            return result
        return wrapped
    return wrapper


@override_settings(ROOT_URLCONF='mail_factory.tests.test_contrib')
class ContribTestCase(TestCase):
    def test_password_reset_default(self):

        user = User.objects.create_user(username='user',
                                        email='admin@example.com',
                                        password="password")

        response = self.client.post(reverse("reset"), data={
            "email": user.email
        })
        self.assertRedirects(response, reverse("password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Password reset on example.com")

    @with_registered_mail_klass(PasswordResetMail)
    def test_password_reset_with_template_name(self):

        user = User.objects.create_user(username='user',
                                        email='admin@example.com',
                                        password="password")

        response = self.client.post(reverse("reset_template_name"), data={
            "email": user.email
        })
        self.assertRedirects(response, reverse("password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Password reset on example.com")
