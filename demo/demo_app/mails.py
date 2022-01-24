from mail_factory import factory, BaseMail, MailForm


class CustomFormMail(BaseMail):
    template_name = 'custom_form'
    params = ['title', 'content']


class CustomFormMailForm(MailForm):

    class Meta:
        initial = {
            'title': 'My initial subject',
            'content': 'My initial content'
        }

factory.register(CustomFormMail, mail_form=CustomFormMailForm)


class NoCustomMail(BaseMail):
    template_name = 'no_custom'
    params = ['title', 'content']

factory.register(NoCustomMail)  # default form
