# -*- coding: utf-8 -*-
"""URLconf for mail_factory admin interface."""
from django.conf import settings
from django.conf.urls import url

from mail_factory.views import form, html_not_found, mail_list, preview_message

LANGUAGE_CODES = '|'.join([code for code, name in settings.LANGUAGES])


urlpatterns = [
    url(r'^$',
        mail_list,
        name='mail_factory_list'),
    url(r'^detail/(?P<mail_name>.*)/$',
        form,
        name='mail_factory_form'),
    url(r'^preview/(?P<lang>(%s))/(?P<mail_name>.*)/$' % LANGUAGE_CODES,
        preview_message,
        name='mail_factory_preview_message'),
    url(r'^html_not_found/(?P<mail_name>.*)/$',
        html_not_found,
        name='mail_factory_html_not_found'),
]
