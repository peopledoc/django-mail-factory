from mail_factory.mails import BaseMail
from mail_factory import factory
from mail_factory.previews import BasePreviewMail


class CommentMail(BaseMail):
    template_name = 'comments'
    params = ['title', 'content']


class CommentPreviewMail(BasePreviewMail):
    mail_class = CommentMail

    def get_context_data(self, **kwargs):
        return {
            'title': 'My super subject',
            'content': 'My super content'
        }

factory.register(CommentMail, mail_preview=CommentPreviewMail)
