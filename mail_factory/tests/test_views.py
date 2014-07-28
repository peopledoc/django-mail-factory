# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from .. import factory
from .. import views
from ..forms import MailForm


class MailListViewTest(TestCase):

    def test_get_context_data(self):
        data = views.MailListView().get_context_data()
        self.assertIn('mail_map', data)
        self.assertEqual(len(data), len(factory._registry))


class MailPreviewMixinTest(TestCase):

    def test_get_html_alternative(self):
        view = views.MailFormView()
        # no_custom has no html alternative
        form_class = factory.get_mail_form('no_custom')
        mail_class = factory.get_mail_class('no_custom')
        form = form_class(mail_class=mail_class)
        mail = mail_class(form.get_context_data())
        message = mail.create_email_msg([])
        self.assertFalse(view.get_html_alternative(message))
        # custom_form has an html alternative
        form_class = factory.get_mail_form('custom_form')
        mail_class = factory.get_mail_class('custom_form')
        form = form_class(mail_class=mail_class)
        mail = mail_class(form.get_context_data())
        message = mail.create_email_msg([])
        self.assertTrue(view.get_html_alternative(message))

    def test_get_mail_preview_language(self):
        view = views.MailFormView()
        view.mail_name = 'no_custom'
        view.mail_class = factory._registry['no_custom']
        message = view.get_mail_preview('no_custom', 'en')
        self.assertEqual(message.subject, 'Title in english: ###')
        self.assertEqual(message.body, 'Content in english: ###')
        message = view.get_mail_preview('no_custom', 'fr')
        self.assertEqual(message.subject, 'Titre en français : ###')
        self.assertEqual(message.body, 'Contenu en français : ###')

    def test_get_mail_preview_no_html(self):
        view = views.MailFormView()
        view.mail_name = 'no_custom'  # no template for html alternative
        view.mail_class = factory._registry['no_custom']
        message = view.get_mail_preview('no_custom', 'en')
        self.assertFalse(message.html)

    def test_get_mail_preview_html(self):
        view = views.MailFormView()
        view.mail_name = 'custom_form'  # has templates for html alternative
        view.mail_class = factory._registry['custom_form']
        message = view.get_mail_preview('custom_form', 'en')
        self.assertTrue(message.html)


class MailFormViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_dispatch_unknown_mail(self):
        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = views.MailFormView()
        with self.assertRaises(Http404):
            view.dispatch(request, 'unknown')

    def test_dispatch(self):
        request = self.factory.post(
            reverse('mail_factory_form', kwargs={'mail_name': 'no_custom'}),
            {'raw': 'foo', 'send': 'foo', 'email': 'email'})
        view = views.MailFormView()
        view.request = request
        view.dispatch(request, 'no_custom')
        self.assertEqual(view.mail_name, 'no_custom')
        self.assertEqual(view.mail_class, factory._registry['no_custom'])
        self.assertTrue(view.raw)
        self.assertTrue(view.send)
        self.assertEqual(view.email, 'email')

    def test_get_form_kwargs(self):
        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = views.MailFormView()
        view.mail_name = 'no_custom'
        view.mail_class = factory._registry['no_custom']
        view.request = request
        self.assertIn('mail_class', view.get_form_kwargs())
        self.assertEqual(view.get_form_kwargs()['mail_class'].__name__,
                         'NoCustomMail')

    def test_get_form_class(self):
        view = views.MailFormView()
        view.mail_name = 'no_custom'
        self.assertEqual(view.get_form_class(), MailForm)

    def test_form_valid_raw(self):
        class MockForm(object):
            cleaned_data = {'title': 'title', 'content': 'content'}

        view = views.MailFormView()
        view.mail_name = 'no_custom'
        view.raw = True
        response = view.form_valid(MockForm())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))
        self.assertTrue(response.content.startswith(b'<pre>'))

    def test_form_valid_send(self):
        class MockForm(object):
            cleaned_data = {'title': 'title', 'content': 'content'}

        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = views.MailFormView()
        view.request = request
        view.mail_name = 'no_custom'
        view.raw = False
        view.send = True
        view.email = 'foo@example.com'
        old_factory_mail = factory.mail  # save current mail method
        # save current django.contrib.messages.success (imported in .views)
        old_messages_success = views.messages.success
        self.factory_send_called = False

        def mock_factory_mail(mail_name, to, context):
            self.factory_send_called = True  # noqa

        factory.mail = mock_factory_mail  # mock mail method
        views.messages.success = lambda x, y: True  # mock messages.success
        response = view.form_valid(MockForm())
        factory.mail = old_factory_mail  # restore mail method
        views.messages.success = old_messages_success  # restore messages
        self.assertTrue(self.factory_send_called)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], reverse('mail_factory_list'))

    def test_form_valid_html(self):
        class MockForm(object):
            cleaned_data = {'title': 'title', 'content': 'content'}

            def get_context_data(self):
                return self.cleaned_data

        view = views.MailFormView()
        view.mail_name = 'custom_form'  # has templates for html alternative
        view.raw = False
        view.send = False
        response = view.form_valid(MockForm())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))

    def test_get_context_data(self):
        view = views.MailFormView()
        view.mail_name = 'no_custom'
        # save the current
        old_get_mail_preview = views.MailPreviewMixin.get_mail_preview
        # mock
        views.MailPreviewMixin.get_mail_preview = lambda x, y, z: 'mocked'
        data = view.get_context_data()
        # restore after mock
        views.MailPreviewMixin.get_mail_preview = old_get_mail_preview
        self.assertIn('mail_name', data)
        self.assertEqual(data['mail_name'], 'no_custom')
        self.assertIn('preview_messages', data)
        self.assertDictEqual(data['preview_messages'],
                             {'fr': 'mocked', 'en': 'mocked'})


class MailPreviewMessageViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_dispatch_unknown_mail(self):
        request = self.factory.get(
            reverse('mail_factory_preview_message',
                    kwargs={'mail_name': 'unknown', 'lang': 'fr'}))
        view = views.MailPreviewMessageView()
        with self.assertRaises(Http404):
            view.dispatch(request, 'unknown', 'fr')

    def test_dispatch(self):
        request = self.factory.get(
            reverse('mail_factory_preview_message',
                    kwargs={'mail_name': 'no_custom', 'lang': 'fr'}))
        view = views.MailPreviewMessageView()
        view.request = request
        view.dispatch(request, 'no_custom', 'fr')
        self.assertEqual(view.mail_name, 'no_custom')
        self.assertEqual(view.lang, 'fr')
        self.assertEqual(view.mail_class, factory._registry['no_custom'])

    def test_get_context_data(self):
        view = views.MailPreviewMessageView()
        view.lang = 'fr'
        view.mail_name = 'no_custom'
        view.mail_class = factory._registry['no_custom']
        data = view.get_context_data()
        self.assertIn('mail_name', data)
        self.assertEqual(data['mail_name'], 'no_custom')
        self.assertIn('message', data)
