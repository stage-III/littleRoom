from django.conf import settings
from django.db import models

from rooms.models import Room


class Booking(models.Model):
    class PaymentMethod(models.TextChoices):
        UPFRONT = 'UPFRONT', 'Upfront'
        ON_DAY = 'ON_DAY', 'Pay on the day'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        REFUNDED = 'REFUNDED', 'Refunded'

    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='bookings',
    )
    guest_email = models.EmailField(blank=True)
    guest_name = models.CharField(max_length=200, blank=True)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.UPFRONT)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)

    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        who = self.user or self.guest_email or 'Guest'
        return f'{self.room} — {self.start_datetime:%Y-%m-%d %H:%M} ({who})'
