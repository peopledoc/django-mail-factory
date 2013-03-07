# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.importlib import import_module


def autodiscover():
    """Auto-discover INSTALLED_APPS mails.py modules."""

    for app in settings.INSTALLED_APPS:
        module = '%s.mails' % app  # Attempt to import the app's 'mails' module
        try:
            import_module(module)
        except ImportError:
            pass

autodiscover()
