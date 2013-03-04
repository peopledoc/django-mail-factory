# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404, HttpResponse
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

        for mail_name, mail_class in sorted(factory.mail_map.items(),
                                            key=lambda x: x[0]):
            mail_list.append((mail_name, mail_class.__name__))
        data['mail_map'] = mail_list
        return data


class MailFormView(FormView):
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

        return HttpResponse(
            factory.get_html_for(self.mail_name, form.cleaned_data))

    def get_context_data(self, **kwargs):
        data = super(MailFormView, self).get_context_data(**kwargs)

        data.update({
            'mail_name': self.mail_name,
            'languages': settings.LANGUAGES,
        })

        if self.mail_class.template_name in factory.preview_map:
            preview_class = factory.preview_map[self.mail_class.template_name]
            preview = preview_class(self.mail_class)

            data['preview'] = preview
            data['preview_messages'] = dict(
                (language_code, preview.get_preview(lang=language_code))
                for language_code, language in settings.LANGUAGES)

        return data


class MailPreviewMessageView(TemplateView):
    template_name = 'mail_factory/preview_message.html'

    def dispatch(self, request, mail_name, lang):
        self.mail_name = mail_name
        self.lang = lang

        try:
            preview_class = factory.preview_map[self.mail_name]
        except exceptions.MailFactoryError:
            raise Http404
        self.preview = preview_class(factory.mail_map[self.mail_name])

        return super(MailPreviewMessageView, self).dispatch(request)

    def get_context_data(self, **kwargs):
        data = super(MailPreviewMessageView, self).get_context_data(**kwargs)
        data['html_preview'] = self.preview.get_html_preview(lang=self.lang)
        return data

mail_list = admin_required(MailListView.as_view())
form = admin_required(MailFormView.as_view())
preview_message = admin_required(MailPreviewMessageView.as_view())
