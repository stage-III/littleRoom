import json
from datetime import time
from unittest.mock import patch
from zoneinfo import ZoneInfo

import stripe
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from rooms.models import Room
from studio_settings.models import StudioHours

TZ = ZoneInfo('Europe/London')


def make_dt(hour):
    from datetime import datetime, date
    d = date(2026, 4, 27)
    return datetime(d.year, d.month, d.day, hour, tzinfo=TZ)


class StripeWebhookViewTests(APITestCase):
    url = '/api/payments/webhook/'

    def setUp(self):
        room = Room.objects.create(name='Room 101', slug='room-101', hourly_rate='10.00')
        StudioHours.objects.create(day_of_week=0, open_time=time(9), close_time=time(22), is_open=True)
        self.booking = Booking.objects.create(
            room=room,
            start_datetime=make_dt(10),
            end_datetime=make_dt(11),
            guest_email='test@example.com',
            stripe_payment_intent_id='pi_test_123',
            payment_status=Booking.PaymentStatus.PENDING,
            total_cost='10.00',
        )

    def _post_event(self, event_type, intent_id='pi_test_123', booking_id=None):
        event = {
            'type': event_type,
            'data': {
                'object': {
                    'id': intent_id,
                    'metadata': {'booking_id': str(booking_id or self.booking.pk)},
                }
            },
        }
        with patch('payments.views.stripe.Webhook.construct_event', return_value=event):
            return self.client.post(
                self.url, '{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=1,v1=test',
            )

    def test_invalid_signature_returns_400(self):
        with patch(
            'payments.views.stripe.Webhook.construct_event',
            side_effect=stripe.error.SignatureVerificationError('bad sig', 'sig_header'),
        ):
            res = self.client.post(self.url, '{}', content_type='application/json',
                                   HTTP_STRIPE_SIGNATURE='bad')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_succeeded_marks_booking_paid(self):
        res = self._post_event('payment_intent.succeeded')
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, Booking.PaymentStatus.PAID)

    def test_payment_failed_leaves_booking_pending(self):
        res = self._post_event('payment_intent.payment_failed')
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, Booking.PaymentStatus.PENDING)

    def test_unknown_event_type_returns_200_and_is_ignored(self):
        res = self._post_event('customer.created')
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, Booking.PaymentStatus.PENDING)

    def test_intent_id_mismatch_does_not_update_booking(self):
        res = self._post_event('payment_intent.succeeded', intent_id='pi_different_456')
        self.assertEqual(res.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, Booking.PaymentStatus.PENDING)

    def test_missing_booking_id_in_metadata_does_not_crash(self):
        event = {
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': 'pi_test_123', 'metadata': {}}},
        }
        with patch('payments.views.stripe.Webhook.construct_event', return_value=event):
            res = self.client.post(self.url, '{}', content_type='application/json',
                                   HTTP_STRIPE_SIGNATURE='t=1,v1=test')
        self.assertEqual(res.status_code, 200)
