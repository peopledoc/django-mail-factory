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
        mod = import_module(app)
        # Attempt to import the app's translation module.
        module = '%s.mails' % app
        try:
            import_module(module)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have a mail module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'mails'):
                raise

autodiscover()
