# -*- coding: utf-8 -*-
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import translation
from django import forms
from django.contrib.auth.models import User
from django.test import Client

from mail_factory import factory
from mail_factory.exceptions import MailFactoryError
from mail_factory.mails import BaseMail
from mail_factory.forms import mailform_factory, MailForm


class TestMail(BaseMail):
    template_name = 'test'
    params = ['title']


class MailFactoryFormTestCase(TestCase):
    def test_mailform_factory(self):
        mailform_class = mailform_factory(TestMail)

        mailform = mailform_class()

        self.assertEqual(mailform.fields.keyOrder, TestMail.params)
        self.assertEqual(mailform.mail, TestMail)

    def test_mailform_factory_with_existing_meta(self):
        class CommentMail(BaseMail):
            template_name = 'comment'
            params = ['content']

        class CommentForm(MailForm):
            title = forms.CharField()

            class Meta:
                initial = {
                    'title': 'My subject',
                    'content': 'My content'
                }

                mail_class = CommentMail

        mailform_class = CommentForm
        mailform = mailform_class()

        self.assertEqual(mailform.fields.keyOrder, ['content', 'title'])
        self.assertEqual(mailform.mail, CommentMail)
        self.assertIn('content', mailform.fields)


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
            'mail_name': 'comments'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail_factory/form.html')

    def test_mail_form_complete(self):
        self.client.login(username='newbie', password='$ecret')

        response = self.client.post(reverse('mail_factory_form', kwargs={
            'mail_name': 'comments',
        }), data={
            'email': 'newbie@localhost',
            'send': 1,
            'title': 'Subject',
            'content': 'Content'
        })

        self.assertRedirects(response, reverse('mail_factory_list'))

        self.assertEqual(len(mail.outbox), 1)

        out = mail.outbox[0]

        self.assertEqual(out.subject, 'Subject')
        self.assertEqual(out.to, ['newbie@localhost'])

        response = self.client.post(reverse('mail_factory_form', kwargs={
            'mail_name': 'comments',
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
        self.assertEquals(factory._get_mail_object('test'), TestMail)

    def test_send_mail(self):
        """Test to send one mail."""
        # Test
        factory.mail('test', ['test@mail.com'], {'title': 'Et hop'})
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(['test@mail.com'], message.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, message.from_email)

    def test_send_mail_admin(self):
        """Test to send one mail."""
        # Test
        if not settings.ADMINS:
            settings.ADMINS = (('Novapost', 'test@novapost.fr'), )
        factory.mail_admins('test', {'title': 'Et hop'})
        self.assertEquals(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(list(settings.ADMINS), message.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, message.from_email)

    def test_html_for(self):
        """Get the html body of the mail."""
        message = factory.get_html_for('test', {'title': 'Et hop'})
        self.assertIn('Et hop', message)

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
        self.assertIn(u'Français', u'%s' % message.body)
        translation.activate('en')
