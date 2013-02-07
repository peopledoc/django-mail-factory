# -*- coding: utf-8 -*-
"""URLconf for mail_factory admin interface."""
from django.conf.urls import patterns, url
from django.conf import settings

from mail_factory.views import mail_list, form, detail

urlpatterns = patterns(
    '',
    url(r'^$',
        mail_list,
        name='mail_factory_list'),

    url(r'^detail/(?P<mail_name>[-\w]+)/(?:(?P<mimetype>(html|txt))/)?(?:(?P<lang>(%s))/)?$' % '|'.join([lang for lang, _ in settings.LANGUAGES]),
        detail,
        name='mail_factory_detail'),

    url(r'^form/(?P<mail_name>[-\w]+)/$',
        form,
        name='mail_factory_form'),
)
