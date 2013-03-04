# -*- coding: utf-8 -*-
from django.conf import settings


try:
    # Try to import floppyforms
    import floppyforms as forms

    # If we can import it but we don't want to use it
    if not 'floppyforms' in settings.INSTALLED_APPS:
        raise ImportError

except ImportError:
    # If django floppyforms is not installed we use django forms.
    from django import forms


class MailForm(forms.Form):
    """Prepopulated the form using mail params."""

    def __init__(self, *args, **kwargs):
        self.mail_class = None

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'initial'):
            kwargs['initial'] = self.Meta.initial
        print(kwargs)

        if 'mail_class' in kwargs:
            self.mail_class = kwargs.pop('mail_class')

        super(MailForm, self).__init__(*args, **kwargs)

        if self.mail_class is not None:
            # Automatic param creation for not already defined fields
            for param in self.mail_class.params:
                if param not in self.fields:
                    self.fields[param] = self.get_field_for_param(param)

            keyOrder = self.mail_class.params
            keyOrder += [x for x in self.fields.keyOrder
                         if x not in self.mail_class.params]
            self.fields.keyOrder = keyOrder

    def get_field_for_param(self, param):
        """By default always return a CharField for a param."""
        return forms.CharField()
