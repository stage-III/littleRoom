from allauth.account.models import EmailAddress as AllauthEmailAddress
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    allow_pay_on_day = models.BooleanField(default=False)


class EmailAddress(AllauthEmailAddress):
    class Meta:
        proxy = True
        app_label = 'accounts'
        verbose_name = 'Email Address'
        verbose_name_plural = 'Email Addresses'
