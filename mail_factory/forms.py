# -*- coding: utf-8 -*-
from django import forms


class MailForm(forms.Form):
    """Prepopulated the form using mail params."""
    mail_class = None

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'initial'):
            initial = self.Meta.initial.copy()
            if 'initial' in kwargs:
                initial.update(kwargs['initial'])
            kwargs['initial'] = initial

        if 'mail_class' in kwargs:
            self.mail_class = kwargs.pop('mail_class')

        super(MailForm, self).__init__(*args, **kwargs)

        if self.mail_class is not None:
            # Automatic param creation for not already defined fields
            for param in self.mail_class.params:
                if param not in self.fields:
                    self.fields[param] = self.get_field_for_param(param)

            keyOrder = self.mail_class.params
            if hasattr(self.fields, 'keyOrder'):  # Django < 1.7
                keyOrder += [x for x in self.fields.keyOrder
                             if x not in self.mail_class.params]
            else:  # Django >= 1.7
                keyOrder += [x for x in self.fields.keys()
                             if x not in self.mail_class.params]
            self.fields.keyOrder = keyOrder

    def get_field_for_param(self, param):
        """By default always return a CharField for a param."""
        return forms.CharField()

    def get_preview_data(self, **kwargs):
        """Return some preview data, not necessarily valid form data."""
        return kwargs

    def get_context_data(self, **kwargs):
        """Return context data used for the mail preview."""
        data = {}
        if self.mail_class is not None:
            for param in self.mail_class.params:
                data[param] = "###"  # default
        data.update(self.initial)
        data.update(kwargs)
        return data
