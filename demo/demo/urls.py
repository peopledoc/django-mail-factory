from django.conf.urls import patterns, include
from django.contrib import admin

from mail_factory import models as factory

factory.autodiscover()
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^mail_factory/', include('mail_factory.urls')),
    (r'^admin/', include(admin.site.urls)),
)
