from mail_factory.mails import BaseMail
from mail_factory import factory
from mail_factory.previews import MailPreview


class CustomPreviewMail(BaseMail):
    template_name = 'custom_preview'
    params = ['title', 'content']


class CustomPreviewMailPreview(MailPreview):

    def get_context_data(self, **kwargs):
        return {
            'title': 'My super subject',
            'content': 'My super content'
        }

factory.register(CustomPreviewMail, mail_preview=CustomPreviewMailPreview)


class NoCustomMail(BaseMail):
    template_name = 'no_custom'
    params = ['title', 'content']

factory.register(NoCustomMail)  # default form and preview
