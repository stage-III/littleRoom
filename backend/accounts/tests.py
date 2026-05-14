from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.adapter import AccountAdapter
from bookings.models import Booking
from rooms.models import Room
from studio_settings.models import StudioHours

User = get_user_model()
TZ = ZoneInfo('Europe/London')


def make_dt(hour):
    return datetime(2026, 4, 27, hour, tzinfo=TZ)


class GuestBookingClaimTests(TestCase):
    def setUp(self):
        StudioHours.objects.create(day_of_week=0, open_time=time(9), close_time=time(22), is_open=True)
        room = Room.objects.create(name='Room A', slug='room-a', hourly_rate='10.00')
        self.booking = Booking.objects.create(
            room=room,
            start_datetime=make_dt(10),
            end_datetime=make_dt(11),
            guest_email='alice@example.com',
            total_cost='10.00',
        )

    def _register(self, email):
        user = User(email=email, username=email)
        user.set_password('pass')
        user.save()
        request = RequestFactory().post('/')
        adapter = AccountAdapter()

        class FakeForm:
            cleaned_data = {'email': email, 'username': email, 'password1': 'pass'}

        adapter.save_user(request, user, FakeForm(), commit=False)
        return user

    def test_guest_booking_claimed_on_signup_with_matching_email(self):
        user = self._register('alice@example.com')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.user, user)

    def test_guest_booking_not_claimed_with_different_email(self):
        self._register('bob@example.com')
        self.booking.refresh_from_db()
        self.assertIsNone(self.booking.user)

    def test_email_match_is_case_insensitive(self):
        user = self._register('Alice@Example.com')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.user, user)

    def test_already_linked_booking_not_reassigned(self):
        other_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        self.booking.user = other_user
        self.booking.save()
        self._register('alice@example.com')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.user, other_user)

    def test_multiple_guest_bookings_all_claimed(self):
        room = Room.objects.get(slug='room-a')
        booking2 = Booking.objects.create(
            room=room,
            start_datetime=make_dt(12),
            end_datetime=make_dt(13),
            guest_email='alice@example.com',
            total_cost='10.00',
        )
        user = self._register('alice@example.com')
        self.booking.refresh_from_db()
        booking2.refresh_from_db()
        self.assertEqual(self.booking.user, user)
        self.assertEqual(booking2.user, user)
