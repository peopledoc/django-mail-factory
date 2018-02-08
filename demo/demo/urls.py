from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^mail_factory/', include('mail_factory.urls')),
    url(r'^admin/', admin.site.urls),
]
