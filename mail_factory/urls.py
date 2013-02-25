# -*- coding: utf-8 -*-
"""URLconf for mail_factory admin interface."""
from django.conf.urls import patterns, url

from django.conf import settings

from mail_factory.views import mail_list, form, preview_message


LANGUAGE_CODES = '|'.join([code for code, name in settings.LANGUAGES])


urlpatterns = patterns(
    '',
    url(r'^$',
        mail_list,
        name='mail_factory_list'),
    url(r'^(?P<mail_name>[-\w]+)/$',
        form,
        name='mail_factory_form'),
    url(r'^(?P<mail_name>[-\w]+)/preview/(?P<lang>(%s))/$' % LANGUAGE_CODES,
        preview_message,
        name='mail_factory_preview_message'),
)
