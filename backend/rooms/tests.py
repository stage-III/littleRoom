from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Equipment, Room


class RoomListViewTests(APITestCase):
    url = '/api/rooms/'

    def test_returns_only_active_rooms(self):
        Room.objects.create(name='Active', slug='active', hourly_rate='10.00', is_active=True)
        Room.objects.create(name='Inactive', slug='inactive', hourly_rate='10.00', is_active=False)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'Active')

    def test_includes_equipment_list(self):
        room = Room.objects.create(name='Room A', slug='room-a', hourly_rate='10.00')
        Equipment.objects.create(room=room, name='Drum kit')
        Equipment.objects.create(room=room, name='Bass amp')
        res = self.client.get(self.url)
        equipment_names = [e['name'] for e in res.data[0]['equipment']]
        self.assertIn('Drum kit', equipment_names)
        self.assertIn('Bass amp', equipment_names)

    def test_no_authentication_required(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
