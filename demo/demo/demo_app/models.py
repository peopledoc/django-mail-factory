from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Article(models.Model):
    user = models.ForeignKey(User)
    content = models.CharField('text', max_length=100)
