from django import forms
from django.contrib.auth.models import User
from mail_factory import factory, BaseMail, MailForm
from demo.demo_app.models import Article


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


class SentArticleByMail(BaseMail):
    template_name = 'article_by_mail'
    params = ['article']


class SentArticleMailForm(MailForm):
    """Configure initial data for the form"""
    article = forms.ModelChoiceField(queryset=Article.objects.all())

    class Meta:
        initial = {
            'article': 1
        }

    def get_preview_data(self):
        """Return the preview context of the mail"""
        return {
            'article': Article(user=User.objects.get(pk=1),
                               content='Welcome to django_mail_factory')
        }

factory.register(SentArticleByMail, SentArticleMailForm)
