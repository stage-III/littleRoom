from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        params = urlencode({'key': emailconfirmation.key})
        return f"{settings.FRONTEND_URL}/confirm-email?{params}"
