from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        params = urlencode({'key': emailconfirmation.key})
        return f"{settings.FRONTEND_URL}/confirm-email?{params}"

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=commit)
        if user.pk and user.email:
            from bookings.models import Booking
            Booking.objects.filter(guest_email__iexact=user.email, user__isnull=True).update(user=user)
        return user
