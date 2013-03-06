# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core import mail
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from django.test import TestCase, Client
from django.utils import translation

from . import factory
from .exceptions import MailFactoryError, MissingMailContextParamException
from .forms import MailForm
from .mails import BaseMail


class TestMail(BaseMail):
    template_name = 'test'
    params = ['title']


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


class MailFactoryViewsTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('newbie', None,
                                                       '$ecret')
        self.client = Client()

    def test_mail_list_view(self):
        self.client.login(username='newbie', password='$ecret')
        response = self.client.get(reverse('mail_factory_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail_factory/list.html')

    def test_mail_form_view(self):
        self.client.login(username='newbie', password='$ecret')
        response = self.client.get(reverse('mail_factory_form', kwargs={
            'mail_name': 'unknown'
        }))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('mail_factory_form', kwargs={
            'mail_name': 'no_custom'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail_factory/form.html')

    def test_mail_form_complete(self):
        self.client.login(username='newbie', password='$ecret')

        response = self.client.post(reverse('mail_factory_form', kwargs={
            'mail_name': 'no_custom',
        }), data={
            'email': 'newbie@localhost',
            'send': 1,
            'title': 'Subject',
            'content': 'Content'
        })

        self.assertRedirects(response, reverse('mail_factory_list'))

        self.assertEqual(len(mail.outbox), 1)

        out = mail.outbox[0]

        self.assertEqual(out.subject, 'Title in english: Subject')
        self.assertEqual(out.to, ['newbie@localhost'])

        response = self.client.post(reverse('mail_factory_form', kwargs={
            'mail_name': 'no_custom',
        }), data={
            'email': 'newbie@localhost',
            'raw': 1,
            'title': 'Subject',
            'content': 'Content'
        })

        self.assertEqual(response.status_code, 200)


class MailFactoryRegistrationTestCase(TestCase):
    def test_factory_registration(self):
        factory.register(TestMail)
        self.assertIn('test', factory.mail_map)

        factory.unregister(TestMail)
        self.assertNotIn('test', factory.mail_map)

    def test_factory_unregister(self):
        with self.assertRaises(MailFactoryError):
            factory.unregister(TestMail)


class MailFactoryTestCase(TestCase):
    def setUp(self):
        factory.register(TestMail)

    def tearDown(self):
        factory.unregister(TestMail)

    def test_factory_get_object(self):
        self.assertEqual(factory.get_mail_class('test'), TestMail)

    def test_send_mail(self):
        """Test to send one mail."""
        factory.mail('test', ['test@mail.com'], {'title': 'Et hop'})
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(['test@mail.com'], message.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, message.from_email)

    def test_mail_admin(self):
        """Test mail admin."""
        if not settings.ADMINS:
            settings.ADMINS = (('Novapost', 'test@novapost.fr'), )
        factory.mail_admins('test', {'title': 'Et hop'})
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual([a[1] for a in settings.ADMINS], message.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, message.from_email)

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
        self.assertEqual(['test@mail.com'], message.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, message.from_email)
        self.assertIn('Et hop', str(message.message()))


class MailFactoryLanguageTestCase(TestCase):
    def setUp(self):
        factory.register(TestMail)

    def tearDown(self):
        factory.unregister(TestMail)

    def test_mail_en(self):
        translation.activate('en')
        message = factory.get_raw_content('test', ['test@mail.com'],
                                          {'title': 'Et hop'})
        self.assertIn('Et hop', '%s' % message.body)

    def test_mail_fr(self):
        translation.activate('fr')
        message = factory.get_raw_content('test', ['test@mail.com'],
                                          {'title': 'Et hop'})
        self.assertIn('Français', '%s' % message.body)
        translation.activate('en')
