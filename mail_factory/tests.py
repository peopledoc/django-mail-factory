# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.template import TemplateDoesNotExist
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import translation

from . import factory
from . import views
from .exceptions import MailFactoryError, MissingMailContextParamException
from .forms import MailForm
from .mails import BaseMail
from .views import MailListView, MailFormView, MailPreviewMessageView


class MailTest(TestCase):

    def test_init(self):
        class TestMail(BaseMail):
            params = ['foo']

        with self.assertRaises(MissingMailContextParamException):
            TestMail()
        with self.assertRaises(MissingMailContextParamException):
            TestMail({})
        with self.assertRaises(MissingMailContextParamException):
            TestMail({'bar': 'bar'})
        self.assertTrue(TestMail({'foo': 'bar'}))

    def test_get_language(self):
        class TestMail(BaseMail):
            params = []

        translation.activate('en')
        self.assertEqual(TestMail().get_language(), 'en')
        translation.activate('fr')
        self.assertEqual(TestMail().get_language(), 'fr')

    def test_get_params(self):
        class TestMail(BaseMail):
            params = []

        self.assertEqual(TestMail().get_params(), [])

        class TestMail2(BaseMail):
            params = ['foo']

        self.assertEqual(TestMail2({'foo': 'bar'}).get_params(), ['foo'])

    def test_get_context_data(self):
        class TestMail(BaseMail):
            params = []

        self.assertEqual(TestMail().get_context_data(), {})
        self.assertEqual(TestMail().get_context_data(foo='bar'),
                         {'foo': 'bar'})

    def test_get_attachments(self):
        class TestMail(BaseMail):
            params = []

        self.assertEqual(TestMail().get_attachments(None), [])
        self.assertEqual(TestMail().get_attachments('foo'), 'foo')

    def test_get_template_part(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        test_mail = TestMail()
        test_mail.lang = 'foo'
        self.assertEqual(test_mail.get_template_part('stuff'),
                         ['mails/test/foo/stuff', 'mails/test/stuff'])
        self.assertEqual(test_mail.get_template_part('stuff', 'bar'),
                         ['mails/test/bar/stuff', 'mails/test/stuff'])

    def test_render_part(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        test_mail = TestMail()
        with self.assertRaises(TemplateDoesNotExist):
            test_mail._render_part('stuff')

        # active language before stays the same
        cur_lang = translation.get_language()
        test_mail._render_part('subject.txt')
        self.assertEqual(cur_lang, translation.get_language())

        # without a proper language, fallback
        test_mail.lang = 'not a lang'
        self.assertEqual(test_mail._render_part('subject.txt'),
                         '[TestCase] Mail test subject')
        # with a proper language, use it
        test_mail.lang = 'fr'
        self.assertEqual(test_mail._render_part('body.txt'), 'Français')
        # use provided language
        test_mail.lang = 'not a lang'
        self.assertEqual(test_mail._render_part('subject.txt', 'en'),
                         '[TestCase] Mail test subject')
        self.assertEqual(test_mail._render_part('body.txt', 'fr'), 'Français')
        # if provided language doesn't exist, fallback
        self.assertEqual(test_mail._render_part('subject.txt', 'not a lang'),
                         '[TestCase] Mail test subject')

    def test_create_email_msg(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        test_mail = TestMail()
        # no "from email" given => use settings.DEFAULT_FROM_EMAIL
        self.assertEqual(test_mail.create_email_msg([]).from_email,
                         settings.DEFAULT_FROM_EMAIL)
        msg = test_mail.create_email_msg([], from_email='foo')
        self.assertEqual(msg.from_email, 'foo')
        # templates with html
        msg = test_mail.create_email_msg([], lang='fr')
        self.assertEqual(len(msg.alternatives), 1)
        msg = test_mail.create_email_msg([], lang='en')
        self.assertEqual(len(msg.alternatives), 1)
        # templates without html
        test_mail.template_name = 'test_no_html'
        msg = test_mail.create_email_msg([], lang='fr')
        self.assertEqual(len(msg.alternatives), 0)
        msg = test_mail.create_email_msg([], lang='en')
        self.assertEqual(len(msg.alternatives), 0)

    def test_create_email_msg_attachments(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        test_mail = TestMail()
        attachments = [
            (finders.find('admin/img/nav-bg.gif'), 'nav-bg.gif', 'image/png'),
            (finders.find('admin/css/base.css'), 'base.css', 'plain/text')]
        msg = test_mail.create_email_msg([], attachments=attachments)
        self.assertEqual(len(msg.attachments), 1)  # base.css
        self.assertEqual(len(msg.related_attachments), 1)  # nav-bg.gif

    def test_send(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        before = len(mail.outbox)
        TestMail().send(['foo@bar.com'])
        self.assertEqual(len(mail.outbox), before + 1)
        self.assertEqual(mail.outbox[-1].to, ['foo@bar.com'])

    def test_mail_admins(self):
        class TestMail(BaseMail):
            params = []
            template_name = 'test'

        before = len(mail.outbox)
        TestMail().mail_admins()
        self.assertEqual(len(mail.outbox), before + 1)
        self.assertEqual(mail.outbox[-1].to, ['some_admin@example.com'])


class MailFactoryFormTest(TestCase):

    def test_init_initial(self):
        class TestForm(MailForm):
            class Meta:
                initial = {'title': 'My subject',
                           'content': 'My content'}

        # without Meta
        self.assertEqual(MailForm().initial, {})
        self.assertEqual(
            MailForm(initial={'foo': 'bar'}).initial['foo'], 'bar')
        # with Meta
        self.assertEqual(TestForm().initial['content'], 'My content')
        self.assertEqual(TestForm().initial['title'], 'My subject')
        # with "initial" provided to the form constructor (takes precedence)
        self.assertEqual(
            TestForm(initial={'content': 'foo'}).initial['content'], 'foo')

    def test_init_mail_class(self):
        class CommentMail(BaseMail):
            params = ['content']
            template_name = 'comment'

        class CommentForm(MailForm):
            title = forms.CharField()

            class Meta:
                initial = {'title': 'My subject', 'content': 'My content'}

        class CommentFormWithMailClass(MailForm):
            title = forms.CharField()
            mail_class = CommentMail

            class Meta:
                initial = {'title': 'My subject', 'content': 'My content'}

        # without mail_class
        mailform = CommentForm()
        self.assertIn('title', mailform.fields)
        self.assertNotIn('content', mailform.fields)
        # with mail_class as constructor parameter
        mailform = CommentForm(mail_class=CommentMail)
        self.assertEqual(mailform.mail_class, CommentMail)
        self.assertIn('title', mailform.fields)
        self.assertIn('content', mailform.fields)
        self.assertEqual(mailform.fields.keyOrder, ['content', 'title'])
        # with mail_class as class attribute
        mailform = CommentFormWithMailClass()
        self.assertEqual(mailform.mail_class, CommentMail)
        self.assertIn('title', mailform.fields)
        self.assertIn('content', mailform.fields)
        self.assertEqual(mailform.fields.keyOrder, ['content', 'title'])

    def test_get_field_for_params(self):
        field = MailForm().get_field_for_param('foo')
        self.assertTrue(isinstance(field, forms.CharField))

    def test_get_value_for_params(self):
        self.assertEqual(MailForm().get_value_for_param('foo'), "###")
        self.assertEqual(
            MailForm(initial={'foo': 'bar'}).get_value_for_param('foo'), "bar")


class MailFactoryViewsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_mail_list_view_get_context_data(self):
        data = MailListView().get_context_data()
        self.assertIn('mail_map', data)
        self.assertEqual(len(data), len(factory.mail_map))

    def test_get_mail_preview(self):
        view = MailFormView()
        view.mail_name = 'no_custom'
        view.mail_class = factory.mail_map['no_custom']
        message = view.get_mail_preview('no_custom', 'en')
        self.assertEqual(message.subject, 'Title in english: ###')
        self.assertEqual(message.body, 'Content in english: ###')
        message = view.get_mail_preview('no_custom', 'fr')
        self.assertEqual(message.subject, 'Titre en français : ###')
        self.assertEqual(message.body, 'Contenu en français : ###')

    def test_mail_form_view_dispatch_unknown_mail(self):
        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = MailFormView()
        with self.assertRaises(Http404):
            view.dispatch(request, 'unknown')

    def test_mail_form_view_dispatch(self):
        request = self.factory.post(
            reverse('mail_factory_form', kwargs={'mail_name': 'no_custom'}),
            {'raw': 'foo', 'send': 'foo', 'email': 'email'})
        view = MailFormView()
        view.request = request
        view.dispatch(request, 'no_custom')
        self.assertEqual(view.mail_name, 'no_custom')
        self.assertEqual(view.mail_class, factory.mail_map['no_custom'])
        self.assertTrue(view.raw)
        self.assertTrue(view.send)
        self.assertEqual(view.email, 'email')

    def test_mail_form_view_get_form_kwargs(self):
        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = MailFormView()
        view.mail_name = 'no_custom'
        view.mail_class = factory.mail_map['no_custom']
        view.request = request
        self.assertIn('mail_class', view.get_form_kwargs())
        self.assertEqual(view.get_form_kwargs()['mail_class'].__name__,
                         'NoCustomMail')

    def test_mail_form_view_get_form_class(self):
        view = MailFormView()
        view.mail_name = 'no_custom'
        self.assertEqual(view.get_form_class(), MailForm)

    def test_mail_form_view_form_valid_raw(self):
        class MockForm(object):
            cleaned_data = {'title': 'title', 'content': 'content'}

        view = MailFormView()
        view.mail_name = 'no_custom'
        view.raw = True
        response = view.form_valid(MockForm())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))
        self.assertTrue(response.content.startswith(b'<pre>'))

    def test_mail_form_view_form_valid_send(self):
        class MockForm(object):
            cleaned_data = {'title': 'title', 'content': 'content'}

        request = self.factory.get(reverse('mail_factory_form',
                                           kwargs={'mail_name': 'unknown'}))
        view = MailFormView()
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

    def test_mail_form_view_form_valid_html(self):
        view = MailFormView()
        view.mail_name = 'no_custom'
        view.raw = False
        view.send = False
        response = view.form_valid(None)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['location'],
            reverse('mail_factory_preview_message',
                    kwargs={'mail_name': 'no_custom',
                            'lang': translation.get_language()}))

    def test_mail_form_view_get_context_data(self):
        view = MailFormView()
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

    def test_mail_preview_message_view_dispatch_unknown_mail(self):
        request = self.factory.get(
            reverse('mail_factory_preview_message',
                    kwargs={'mail_name': 'unknown', 'lang': 'fr'}))
        view = MailPreviewMessageView()
        with self.assertRaises(Http404):
            view.dispatch(request, 'unknown', 'fr')

    def test_mail_preview_message_view_dispatch(self):
        request = self.factory.get(
            reverse('mail_factory_preview_message',
                    kwargs={'mail_name': 'no_custom', 'lang': 'fr'}))
        view = MailPreviewMessageView()
        view.request = request
        view.dispatch(request, 'no_custom', 'fr')
        self.assertEqual(view.mail_name, 'no_custom')
        self.assertEqual(view.lang, 'fr')
        self.assertEqual(view.mail_class, factory.mail_map['no_custom'])

    def test_mail_preview_message_view_get_context_data(self):
        view = MailPreviewMessageView()
        view.lang = 'fr'
        # no_custom has no template for html alternative
        view.mail_name = 'no_custom'
        view.mail_class = factory.mail_map['no_custom']
        data = view.get_context_data()
        self.assertIn('mail_name', data)
        self.assertEqual(data['mail_name'], 'no_custom')
        self.assertNotIn('html_preview', data)
        # custom_form has templates for html alternative
        view.mail_name = 'custom_form'
        view.mail_class = factory.mail_map['custom_form']
        data = view.get_context_data()
        self.assertIn('mail_name', data)
        self.assertEqual(data['mail_name'], 'custom_form')
        self.assertIn('html_preview', data)
        self.assertIn('contenu en HTML et en français : My initial content',
                      data['html_preview'])


class MailFactoryRegistrationTest(TestCase):

    def tearDown(self):
        if 'foo' in factory.mail_map:
            del factory.mail_map['foo']

    def test_registration_without_template_name(self):
        class TestMail(BaseMail):
            pass

        with self.assertRaises(MailFactoryError):
            factory.register(TestMail)

    def test_registration_already_registered(self):
        class TestMail(BaseMail):
            template_name = 'foo'

        factory.register(TestMail)
        with self.assertRaises(MailFactoryError):
            factory.register(TestMail)

    def test_registration(self):
        class TestMail(BaseMail):
            template_name = 'foo'

        factory.register(TestMail)
        self.assertIn('foo', factory.mail_map)
        self.assertEqual(factory.mail_map['foo'], TestMail)
        self.assertIn('foo', factory.form_map)
        self.assertEqual(factory.form_map['foo'], MailForm)  # default form

    def test_registration_with_custom_form(self):
        class TestMail(BaseMail):
            template_name = 'foo'

        class TestMailForm(MailForm):
            pass

        factory.register(TestMail, TestMailForm)
        self.assertIn('foo', factory.form_map)
        self.assertEqual(factory.form_map['foo'], TestMailForm)  # custom form

    def test_factory_unregister(self):
        class TestMail(BaseMail):
            template_name = 'foo'

        factory.register(TestMail)
        self.assertIn('foo', factory.mail_map)
        factory.unregister(TestMail)
        self.assertNotIn('foo', factory.mail_map)
        with self.assertRaises(MailFactoryError):
            factory.unregister(TestMail)


class MailFactoryTest(TestCase):
    def setUp(self):
        class TestMail(BaseMail):
            template_name = 'test'
            params = ['title']

        self.test_mail = TestMail
        factory.register(TestMail)

    def tearDown(self):
        factory.unregister(self.test_mail)

    def test_get_mail_class_not_registered(self):
        with self.assertRaises(MailFactoryError):
            factory.get_mail_class('not registered')

    def test_factory_get_mail_class(self):
        self.assertEqual(factory.get_mail_class('test'), self.test_mail)

    def test_factory_get_mail_object(self):
        self.assertTrue(
            isinstance(factory.get_mail_object('test', {'title': 'foo'}),
                       self.test_mail))

    def test_get_mail_form_not_registered(self):
        with self.assertRaises(MailFactoryError):
            factory.get_mail_form('not registered')

    def test_factory_get_mail_form(self):
        self.assertEqual(factory.get_mail_form('test'), MailForm)

    def test_html_for(self):
        """Get the html body of the mail."""
        message = factory.get_html_for('test', {'title': 'Et hop'})
        self.assertIn('Et hop', message)

    def test_text_for(self):
        """Get the text body of the mail."""
        message = factory.get_text_for('test', {'title': 'Et hop'})
        self.assertIn('Et hop', message)

    def test_subject_for(self):
        """Get the subject of the mail."""
        subject = factory.get_subject_for('test', {'title': 'Et hop'})
        self.assertEqual(subject, "[TestCase] Mail test subject")

    def test_get_raw_content(self):
        """Get the message object."""
        message = factory.get_raw_content('test', ['test@mail.com'],
                                          {'title': 'Et hop'})
        self.assertEqual(message.to, ['test@mail.com'])
        self.assertEqual(message.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn('Et hop', str(message.message()))


class MailFactoryMailTest(TestCase):

    def setUp(self):
        class MockMail(object):  # mock mail to check if its methods are called
            mail_admins_called = False
            send_called = False
            template_name = 'mockmail'

            def send(self, *args, **kwargs):
                self.send_called = True

            def mail_admins(self, *args, **kwargs):
                self.mail_admins_called = True

        self.mock_mail = MockMail()
        self.mock_mail_class = MockMail
        factory.register(MockMail)
        self.old_get_mail_object = factory.get_mail_object
        factory.get_mail_object = self._mock_get_mail_object

    def tearDown(self):
        factory.unregister(self.mock_mail_class)
        self.mock_mail.send_called = False
        self.mock_mail.mail_admins_called = False
        factory.get_mail_object = self.old_get_mail_object

    def _mock_get_mail_object(self, template_name, context):
        return self.mock_mail

    def test_mail(self):
        self.assertFalse(self.mock_mail.send_called)
        factory.mail('test', ['foo@example.com'], {})
        self.assertTrue(self.mock_mail.send_called)

    def test_mail_admins(self):
        self.assertFalse(self.mock_mail.mail_admins_called)
        factory.mail_admins('test', {})
        self.assertTrue(self.mock_mail.mail_admins_called)
