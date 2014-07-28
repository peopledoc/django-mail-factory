# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404, HttpResponse
from django.template.base import TemplateDoesNotExist
from django.views.generic import TemplateView, FormView
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from . import factory, exceptions

admin_required = user_passes_test(lambda x: x.is_superuser)


class MailListView(TemplateView):
    """Return a list of mails."""
    template_name = 'mail_factory/list.html'

    def get_context_data(self, **kwargs):
        """Return object_list."""
        data = super(MailListView, self).get_context_data(**kwargs)
        mail_list = []

        for mail_name, mail_class in sorted(factory._registry.items(),
                                            key=lambda x: x[0]):
            mail_list.append((mail_name, mail_class.__name__))
        data['mail_map'] = mail_list
        return data


class MailPreviewMixin(object):

    def get_html_alternative(self, message):
        """Return the html alternative, if present."""
        alternatives = dict((v, k) for k, v in message.alternatives)
        if 'text/html' in alternatives:
            return alternatives['text/html']

    def get_mail_preview(self, template_name, lang, cid_to_data=False):
        """Return a preview from a mail's form's initial data."""
        form_class = factory.get_mail_form(self.mail_name)
        form = form_class(mail_class=self.mail_class)

        form = form_class(form.get_context_data(), mail_class=self.mail_class)
        data = form.get_context_data()
        if form.is_valid():
            data.update(form.cleaned_data)

        # overwrite with preview data if any
        data.update(form.get_preview_data())

        mail = self.mail_class(data)
        message = mail.create_email_msg([settings.ADMINS], lang=lang)

        try:
            message.html = factory.get_html_for(self.mail_name, data,
                                                lang=lang, cid_to_data=True)
        except TemplateDoesNotExist:
            message.html = False

        return message


class MailFormView(MailPreviewMixin, FormView):
    template_name = 'mail_factory/form.html'

    def dispatch(self, request, mail_name):
        self.mail_name = mail_name

        try:
            self.mail_class = factory.get_mail_class(self.mail_name)
        except exceptions.MailFactoryError:
            raise Http404

        self.raw = 'raw' in request.POST
        self.send = 'send' in request.POST
        self.email = request.POST.get('email')

        return super(MailFormView, self).dispatch(request)

    def get_form_kwargs(self):
        kwargs = super(MailFormView, self).get_form_kwargs()
        kwargs['mail_class'] = self.mail_class
        return kwargs

    def get_form_class(self):
        return factory.get_mail_form(self.mail_name)

    def form_valid(self, form):
        if self.raw:
            return HttpResponse('<pre>%s</pre>' %
                                factory.get_raw_content(
                                    self.mail_name,
                                    [settings.DEFAULT_FROM_EMAIL],
                                    form.cleaned_data).message())

        if self.send:
            factory.mail(self.mail_name, [self.email], form.cleaned_data)
            messages.success(self.request,
                             '%s mail sent to %s' % (self.mail_name,
                                                     self.email))
            return redirect('mail_factory_list')

        data = None

        if form:
            data = form.get_context_data()
            if hasattr(form, 'cleaned_data'):
                data.update(form.cleaned_data)

        try:
            html = factory.get_html_for(self.mail_name, data,
                                        cid_to_data=True)
        except TemplateDoesNotExist:
            return redirect('mail_factory_html_not_found',
                            mail_name=self.mail_name)
        return HttpResponse(html)

    def get_context_data(self, **kwargs):
        data = super(MailFormView, self).get_context_data(**kwargs)
        data['mail_name'] = self.mail_name

        preview_messages = {}
        for lang_code, lang_name in settings.LANGUAGES:
            message = self.get_mail_preview(self.mail_name, lang_code)
            preview_messages[lang_code] = message
        data['preview_messages'] = preview_messages

        return data


class HTMLNotFoundView(TemplateView):
    """No HTML template was found"""
    template_name = 'mail_factory/html_not_found.html'


class MailPreviewMessageView(MailPreviewMixin, TemplateView):
    template_name = 'mail_factory/preview_message.html'

    def dispatch(self, request, mail_name, lang):
        self.mail_name = mail_name
        self.lang = lang

        try:
            self.mail_class = factory.get_mail_class(self.mail_name)
        except exceptions.MailFactoryError:
            raise Http404

        return super(MailPreviewMessageView, self).dispatch(request)

    def get_context_data(self, **kwargs):
        data = super(MailPreviewMessageView, self).get_context_data(**kwargs)
        message = self.get_mail_preview(self.mail_name, self.lang)
        data['mail_name'] = self.mail_name
        data['message'] = message
        return data

mail_list = admin_required(MailListView.as_view())
form = admin_required(MailFormView.as_view())
html_not_found = admin_required(HTMLNotFoundView.as_view())
preview_message = admin_required(MailPreviewMessageView.as_view())
