from mail_factory.previews import BasePreviewMail
from mail_factory import site

from comments.mails import CommentMail


class PreviewCommentMail(BasePreviewMail):
    mail_class = CommentMail

    def get_context_data(self, **kwargs):
        return {
            'title': 'My super subject',
            'content': 'My super content'
        }

site.register(PreviewCommentMail)
