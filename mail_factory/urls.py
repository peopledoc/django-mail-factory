# -*- coding: utf-8 -*-
"""URLconf for mail_factory admin interface."""
from django.conf.urls import patterns, url
from mail_factory.views import mail_list, form

urlpatterns = patterns(
    '',
    url(r'^$', mail_list, name='mail_factory_list'),
    url(r'^(?P<mail_name>[-\w]+)/$', form, name='mail_factory_form'),
)
