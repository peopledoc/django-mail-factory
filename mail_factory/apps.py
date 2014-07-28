from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SimpleMailFactoryConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    name = 'mail_factory'
    verbose_name = _("Mail Factory")


class MailFactoryConfig(SimpleMailFactoryConfig):
    """The default AppConfig for mail_factory which does autodiscovery."""

    def ready(self):
        super(MailFactoryConfig, self).ready()
        self.module.autodiscover()
