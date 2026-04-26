from django.test import TestCase
from django.urls import reverse

from .models import StudioSettings


class PublicSettingsViewTests(TestCase):
    def test_returns_200(self):
        res = self.client.get('/api/settings/')
        self.assertEqual(res.status_code, 200)

    def test_returns_expected_fields(self):
        res = self.client.get('/api/settings/')
        data = res.json()
        self.assertIn('min_notice_days', data)
        self.assertIn('allow_pay_on_day', data)
        self.assertIn('min_booking_hours', data)

    def test_default_values(self):
        res = self.client.get('/api/settings/')
        data = res.json()
        self.assertEqual(data['min_notice_days'], 0)
        self.assertEqual(data['allow_pay_on_day'], False)
        self.assertEqual(data['min_booking_hours'], 1)

    def test_reflects_saved_values(self):
        s = StudioSettings.get_solo()
        s.min_notice_days = 3
        s.allow_pay_on_day = True
        s.min_booking_hours = 2
        s.save()

        res = self.client.get('/api/settings/')
        data = res.json()
        self.assertEqual(data['min_notice_days'], 3)
        self.assertEqual(data['allow_pay_on_day'], True)
        self.assertEqual(data['min_booking_hours'], 2)

    def test_no_auth_required(self):
        # Endpoint must be public — unauthenticated request returns 200
        res = self.client.get('/api/settings/')
        self.assertEqual(res.status_code, 200)

    def test_post_not_allowed(self):
        res = self.client.post('/api/settings/', {}, content_type='application/json')
        self.assertEqual(res.status_code, 405)
