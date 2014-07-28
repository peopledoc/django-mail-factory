# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from .. import factory
from ..exceptions import MailFactoryError
from ..forms import MailForm
from ..mails import BaseMail


class RegistrationTest(TestCase):

    def tearDown(self):
        if 'foo' in factory._registry:
            del factory._registry['foo']

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
        self.assertIn('foo', factory._registry)
        self.assertEqual(factory._registry['foo'], TestMail)
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
        self.assertIn('foo', factory._registry)
        factory.unregister(TestMail)
        self.assertNotIn('foo', factory._registry)
        with self.assertRaises(MailFactoryError):
            factory.unregister(TestMail)


class FactoryTest(TestCase):
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


class FactoryMailTest(TestCase):

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
