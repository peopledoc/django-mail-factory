# -*- coding: utf-8 -*-


def autodiscover():
    """
    Auto-discover INSTALLED_APPS mails.py modules and fail silently
    when not present. This forces an import on them to register. Also
    import explicit modules.
    """
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        module = import_module(app)

        if module_has_submodule(module, 'mails'):
            emails = import_module('%s.mails' % app)
            try:
                import_module('%s.mails.previews' % app)
            except ImportError:
                # Only raise the exception if this module contains previews and
                # there was a problem importing them. (An emails module that
                # does not contain previews is not an error.)
                if module_has_submodule(emails, 'previews'):
                    raise

autodiscover()
