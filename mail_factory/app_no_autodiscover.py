from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SimpleMailFactoryConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    name = "mail_factory"
    verbose_name = _("Mail Factory")
