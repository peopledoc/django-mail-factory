# -*- coding: utf-8 -*-
from mail_factory import BaseMail


class PasswordResetMail(BaseMail):
    template_name = 'password_reset'
    params = ['email', 'domain', 'site_name', 'uid',
              'user', 'token', 'protocol']
