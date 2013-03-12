# -*- coding: utf-8 -*-

"""Keep in mind throughout those tests that the mails from demo.demo_app.mails
are automatically registered, and serve as fixture."""

from __future__ import unicode_literals

from os.path import basename

from django.test import TestCase

from .. import messages


class EmailMultiRelatedTest(TestCase):

    def setUp(self):
        self.message = messages.EmailMultiRelated()

    def test_attach_related_mimebase(self):
        mime_message = messages.MIMEBase(None, None)
        # no content nor mimetype with a mime message
        with self.assertRaises(AssertionError):
            self.message.attach_related(filename=mime_message, content='foo')
        with self.assertRaises(AssertionError):
            self.message.attach_related(filename=mime_message, mimetype='bar')
        # attach a mime message
        self.message.attach_related(filename=mime_message)
        self.assertEqual(self.message.related_attachments, [mime_message])

    def test_attach_related_non_mimebase(self):
        # needs a content if not a mimemessage
        with self.assertRaises(AssertionError):
            self.message.attach_related(filename='foo')
        # attach a non-mime message
        self.message.attach_related(filename='foo', content='bar',
                                    mimetype='baz')
        self.assertEqual(self.message.related_attachments,
                         [('foo', 'bar', 'baz')])

    def test_attach_related_file(self):
        path = __file__  # attach this very file you're reading
        self.message.attach_related_file(path=path, mimetype='baz')
        filename, content, mimetype = self.message.related_attachments[0]
        self.assertEqual(filename, basename(__file__))
        self.assertEqual(mimetype, 'baz')

    def test_create_alternatives(self):
        self.message.alternatives = [('<img src="img.gif" />', 'text/html')]
        self.message.related_attachments = [('img.gif', b'', 'image/gif')]
        self.message._create_alternatives(None)
        self.assertEqual(self.message.alternatives,
                         [('<img src="cid:img.gif" />', 'text/html')])

    def test_create_related_attachments(self):
        self.message.related_attachments = [('img.gif', b'', 'image/gif')]
        self.message.body = True
        new_msg = self.message._create_related_attachments('foo message')
        content, attachment = new_msg.get_payload()
        self.assertEqual(content, 'foo message')
        self.assertEqual(attachment.get_filename(), 'img.gif')
