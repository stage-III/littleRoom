from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from bookings.models import Booking
from rooms.models import Room
from studio_settings.models import ClosureDate, StudioHours, StudioSettings

TZ = ZoneInfo('Europe/London')

# Monday 2026-04-27 — used as a fixed test date throughout
TEST_DATE = date(2026, 4, 27)


def make_dt(hour, minute=0, d=TEST_DATE):
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=TZ)


def make_booking(room, start_hour, end_hour, **kwargs):
    return Booking.objects.create(
        room=room,
        start_datetime=make_dt(start_hour),
        end_datetime=make_dt(end_hour),
        guest_email=kwargs.pop('guest_email', 'fixture@example.com'),
        **kwargs,
    )


class AvailabilityViewTests(APITestCase):
    url = '/api/availability/'

    def setUp(self):
        self.room = Room.objects.create(name='Room 101', slug='room-101', hourly_rate='10.00')
        self.studio_hours = StudioHours.objects.create(
            day_of_week=0,  # Monday
            open_time=time(9, 0),
            close_time=time(22, 0),
            is_open=True,
        )
        settings = StudioSettings.get_solo()
        settings.min_booking_hours = 1
        settings.save()

    def test_missing_date_param_returns_400(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_date_format_returns_400(self):
        res = self.client.get(self.url, {'date': 'not-a-date'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_closure_date_returns_closed(self):
        ClosureDate.objects.create(date=TEST_DATE)
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['is_open'])
        self.assertEqual(res.data['rooms'], [])

    def test_no_studio_hours_configured_returns_closed(self):
        tuesday = date(2026, 4, 28)  # No StudioHours for Tuesday
        res = self.client.get(self.url, {'date': str(tuesday)})
        self.assertFalse(res.data['is_open'])

    def test_studio_closed_flag_returns_closed(self):
        self.studio_hours.is_open = False
        self.studio_hours.save()
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        self.assertFalse(res.data['is_open'])

    def test_open_day_no_bookings_returns_correct_slots(self):
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        self.assertTrue(res.data['is_open'])
        self.assertEqual(len(res.data['rooms']), 1)
        slots = res.data['rooms'][0]['slots']
        # 09:00 to 21:00 inclusive at 15-min steps = 49 slots
        self.assertEqual(len(slots), 49)
        self.assertEqual(slots[0]['max_hours'], 13)   # 09:00 → can book until 22:00
        self.assertEqual(slots[-1]['max_hours'], 1)   # 21:00 → can only book 1h

    def test_slot_before_booking_has_correct_max_hours(self):
        make_booking(self.room, start_hour=12, end_hour=13)
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        slots = res.data['rooms'][0]['slots']
        slot_09 = next(s for s in slots if '09:00' in s['start_time'])
        # From 09:00 the next booking starts at 12:00 → 3 free hours
        self.assertEqual(slot_09['max_hours'], 3)

    def test_slots_not_shown_when_window_too_short_for_minimum(self):
        # Booking at 10:00 leaves only 1h before it (09:00–10:00)
        make_booking(self.room, start_hour=10, end_hour=11)
        settings = StudioSettings.get_solo()
        settings.min_booking_hours = 2
        settings.save()
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        slots = res.data['rooms'][0]['slots']
        # 09:00 only has 1h free → filtered out with min=2
        self.assertFalse(any('09:00' in s['start_time'] for s in slots))

    def test_slots_resume_after_booked_window(self):
        make_booking(self.room, start_hour=11, end_hour=12)
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        slots = res.data['rooms'][0]['slots']
        start_times = [s['start_time'] for s in slots]
        # Inside the booking: should not appear
        self.assertFalse(any('T11:00' in t for t in start_times))
        # After the booking: should appear
        self.assertTrue(any('T12:00' in t for t in start_times))
        # 10:15 → only 45 min free before booking, below min 1h → not shown
        self.assertFalse(any('T10:15' in t for t in start_times))
        # 10:00 → exactly 1h free before booking → shown
        self.assertTrue(any('T10:00' in t for t in start_times))

    def test_fully_booked_room_returns_no_slots(self):
        make_booking(self.room, start_hour=9, end_hour=22)
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        self.assertEqual(res.data['rooms'][0]['slots'], [])

    def test_refunded_booking_does_not_block_slot(self):
        make_booking(self.room, start_hour=10, end_hour=11,
                     payment_status=Booking.PaymentStatus.REFUNDED)
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        slots = res.data['rooms'][0]['slots']
        # The refunded slot should be available again
        self.assertTrue(any('T10:00' in s['start_time'] for s in slots))

    def test_response_includes_studio_metadata(self):
        res = self.client.get(self.url, {'date': str(TEST_DATE)})
        self.assertEqual(res.data['open_time'], '09:00')
        self.assertEqual(res.data['close_time'], '22:00')
        self.assertEqual(res.data['min_booking_hours'], 1)


class BookingCreateViewTests(APITestCase):
    url = '/api/bookings/'

    def setUp(self):
        self.room = Room.objects.create(name='Room 101', slug='room-101', hourly_rate='10.00')
        StudioHours.objects.create(
            day_of_week=0,
            open_time=time(9, 0),
            close_time=time(22, 0),
            is_open=True,
        )
        settings = StudioSettings.get_solo()
        settings.min_booking_hours = 1
        settings.allow_pay_on_day = False
        settings.save()
        self.valid_payload = {
            'room': self.room.pk,
            'start_datetime': make_dt(10).isoformat(),
            'end_datetime': make_dt(11).isoformat(),
            'guest_email': 'guest@example.com',
            'guest_name': 'Test Guest',
        }

    def test_guest_booking_creates_booking(self):
        res = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertIsNone(booking.user)
        self.assertEqual(booking.guest_email, 'guest@example.com')

    def test_authenticated_user_booking_sets_user(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='x')
        self.client.force_authenticate(user=user)
        res = self.client.post(self.url, {
            'room': self.room.pk,
            'start_datetime': make_dt(10).isoformat(),
            'end_datetime': make_dt(11).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, user)
        self.assertEqual(booking.guest_email, '')

    def test_guest_booking_without_email_returns_400(self):
        payload = {k: v for k, v in self.valid_payload.items() if k != 'guest_email'}
        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_not_on_15_min_boundary_returns_400(self):
        res = self.client.post(self.url, {
            **self.valid_payload,
            'start_datetime': make_dt(10, 7).isoformat(),
            'end_datetime': make_dt(11, 7).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duration_below_minimum_returns_400(self):
        res = self.client.post(self.url, {
            **self.valid_payload,
            'end_datetime': make_dt(10, 30).isoformat(),  # 30 min, below 1h minimum
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_whole_hour_duration_beyond_minimum_returns_400(self):
        # 1h30m: 30min excess beyond minimum of 1h is not a whole hour
        res = self.client.post(self.url, {
            **self.valid_payload,
            'end_datetime': make_dt(11, 30).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duration_over_24_hours_returns_400(self):
        res = self.client.post(self.url, {
            **self.valid_payload,
            'start_datetime': make_dt(9).isoformat(),
            'end_datetime': (make_dt(9) + timedelta(hours=25)).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_on_closure_date_returns_400(self):
        ClosureDate.objects.create(date=TEST_DATE)
        res = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_outside_studio_hours_returns_400(self):
        res = self.client.post(self.url, {
            **self.valid_payload,
            'start_datetime': make_dt(7).isoformat(),
            'end_datetime': make_dt(8).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlapping_booking_returns_400(self):
        make_booking(self.room, start_hour=10, end_hour=11)
        res = self.client.post(self.url, {
            **self.valid_payload,
            'start_datetime': make_dt(10, 30).isoformat(),
            'end_datetime': make_dt(11, 30).isoformat(),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_on_refunded_slot_succeeds(self):
        make_booking(self.room, start_hour=10, end_hour=11,
                     payment_status=Booking.PaymentStatus.REFUNDED)
        res = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_pay_on_day_silently_overridden_for_ineligible_user(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='x')
        user.allow_pay_on_day = False
        user.save()
        self.client.force_authenticate(user=user)
        res = self.client.post(self.url, {
            'room': self.room.pk,
            'start_datetime': make_dt(10).isoformat(),
            'end_datetime': make_dt(11).isoformat(),
            'payment_method': 'ON_DAY',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.get().payment_method, Booking.PaymentMethod.UPFRONT)

    def test_pay_on_day_silently_overridden_when_global_flag_off(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='x')
        user.allow_pay_on_day = True
        user.save()
        # Global flag is already False from setUp
        self.client.force_authenticate(user=user)
        res = self.client.post(self.url, {
            'room': self.room.pk,
            'start_datetime': make_dt(10).isoformat(),
            'end_datetime': make_dt(11).isoformat(),
            'payment_method': 'ON_DAY',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.get().payment_method, Booking.PaymentMethod.UPFRONT)

    def test_pay_on_day_allowed_for_fully_eligible_user(self):
        settings = StudioSettings.get_solo()
        settings.allow_pay_on_day = True
        settings.save()
        user = User.objects.create_user(username='u', email='u@example.com', password='x')
        user.allow_pay_on_day = True
        user.save()
        self.client.force_authenticate(user=user)
        res = self.client.post(self.url, {
            'room': self.room.pk,
            'start_datetime': make_dt(10).isoformat(),
            'end_datetime': make_dt(11).isoformat(),
            'payment_method': 'ON_DAY',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.get().payment_method, Booking.PaymentMethod.ON_DAY)


class BookingMineViewTests(APITestCase):
    url = '/api/bookings/mine/'

    def setUp(self):
        self.room = Room.objects.create(name='Room 101', slug='room-101', hourly_rate='10.00')
        self.user = User.objects.create_user(username='u', email='u@example.com', password='x')
        self.other = User.objects.create_user(username='o', email='o@example.com', password='x')

    def test_unauthenticated_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_only_current_users_bookings(self):
        Booking.objects.create(room=self.room, user=self.user,
                               start_datetime=make_dt(10), end_datetime=make_dt(11))
        Booking.objects.create(room=self.room, user=self.other,
                               start_datetime=make_dt(12), end_datetime=make_dt(13))
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['room']['slug'], 'room-101')

    def test_returns_empty_list_for_user_with_no_bookings(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
