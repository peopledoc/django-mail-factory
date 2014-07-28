# -*- coding: utf-8 -*-
"""Django Mail Manager"""

pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('django-mail-factory')

#: Module version, as defined in PEP-0396.
__version__ = distribution.version

from mail_factory.factory import MailFactory
from mail_factory.forms import MailForm  # NOQA
from mail_factory.mails import BaseMail  # NOQA

factory = MailFactory()


try:  # Only from Django1.7.
    from django.utils.module_loading import autodiscover_modules

    def autodiscover():
        autodiscover_modules('mails', register_to=factory)
except ImportError:
    pass


default_app_config = 'mail_factory.apps.MailFactoryConfig'
