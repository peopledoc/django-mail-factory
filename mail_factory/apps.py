from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MailFactoryConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    name = "mail_factory"
    verbose_name = _("Mail Factory")

    def ready(self):
        super(MailFactoryConfig, self).ready()
        for app in self.apps.get_app_configs():
            try:
                import_module(name=".mails", package=app.module.__name__)
            except ImportError:
                pass
