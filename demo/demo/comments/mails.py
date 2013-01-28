from mail_factory.mails import BaseMail
from mail_factory import factory


class CommentMail(BaseMail):
    template_name = 'comments'
    params = ['title', 'content']


factory.register(CommentMail)
