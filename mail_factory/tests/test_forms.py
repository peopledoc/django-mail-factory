# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals


from django import forms
from django.test import TestCase

from ..forms import MailForm
from ..mails import BaseMail


class FormTest(TestCase):

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

    def test_get_context_data(self):
        self.assertEqual(MailForm().get_context_data(), {})
        self.assertEqual(
            MailForm(initial={'foo': 'bar'}).get_context_data()['foo'], "bar")
        self.assertEqual(
            MailForm().get_context_data(foo='bar')['foo'], "bar")
