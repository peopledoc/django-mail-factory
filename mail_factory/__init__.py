# -*- coding: utf-8 -*-
"""Django Mail Manager"""

import django

from mail_factory.app_no_autodiscover import SimpleMailFactoryConfig
from mail_factory.apps import MailFactoryConfig
from mail_factory.factory import MailFactory
from mail_factory.forms import MailForm  # NOQA
from mail_factory.mails import BaseMail  # NOQA

pkg_resources = __import__("pkg_resources")
distribution = pkg_resources.get_distribution("django-mail-factory")

#: Module version, as defined in PEP-0396.
__version__ = distribution.version

__all__ = ["MailFactoryConfig", "SimpleMailFactoryConfig"]

factory = MailFactory()


if django.VERSION[:2] < (3, 2):
    default_app_config = "mail_factory.apps.MailFactoryConfig"
