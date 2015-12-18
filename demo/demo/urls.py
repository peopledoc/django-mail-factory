from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^mail_factory/', include('mail_factory.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
