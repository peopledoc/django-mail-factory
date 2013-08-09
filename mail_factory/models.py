# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


def autodiscover():
    """Auto-discover INSTALLED_APPS mails.py modules."""

    for app in settings.INSTALLED_APPS:
        module = '%s.mails' % app  # Attempt to import the app's 'mails' module
        try:
            import_module(module)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have a mails module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            app_module = import_module(app)
            if module_has_submodule(app_module, 'mails'):
                raise

autodiscover()
