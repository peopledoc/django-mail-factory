# -*- coding: utf-8 -*-
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.utils import translation

from mail_factory import factory
from mail_factory.exceptions import MailFactoryError
from mail_factory.mails import BaseMail


class TestMail(BaseMail):
    template_name = 'test'
    params = ['title']


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
