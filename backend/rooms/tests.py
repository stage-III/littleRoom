import io
import tempfile

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Equipment, Room

TEMP_MEDIA = tempfile.mkdtemp()


def make_png(width=400, height=300):
    img = Image.new('RGB', (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())


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

    def test_image_is_null_when_not_set(self):
        Room.objects.create(name='Room', slug='room', hourly_rate='10.00')
        res = self.client.get(self.url)
        self.assertIsNone(res.data[0]['image'])

    @override_settings(MEDIA_ROOT=TEMP_MEDIA)
    def test_image_url_is_absolute(self):
        room = Room.objects.create(name='Room', slug='room', hourly_rate='10.00')
        room.image.save('test.png', make_png(), save=True)
        res = self.client.get(self.url)
        self.assertTrue(res.data[0]['image'].startswith('http'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA)
    def test_image_url_contains_media_path(self):
        room = Room.objects.create(name='Room', slug='room', hourly_rate='10.00')
        room.image.save('test.png', make_png(), save=True)
        res = self.client.get(self.url)
        self.assertIn('/media/rooms/', res.data[0]['image'])


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class RoomImageCompressionTests(TestCase):

    def _room_with_image(self, width, height):
        room = Room.objects.create(name='Room', slug='room', hourly_rate='10.00')
        room.image.save('test.png', make_png(width, height), save=True)
        return room

    def test_large_image_is_resized_to_800px(self):
        room = self._room_with_image(1200, 800)
        with Image.open(room.image.path) as img:
            self.assertLessEqual(img.width, 800)

    def test_small_image_is_not_enlarged(self):
        room = self._room_with_image(400, 300)
        with Image.open(room.image.path) as img:
            self.assertEqual(img.width, 400)

    def test_image_is_converted_to_jpeg(self):
        room = self._room_with_image(400, 300)
        with Image.open(room.image.path) as img:
            self.assertEqual(img.format, 'JPEG')

    def test_aspect_ratio_preserved_on_resize(self):
        room = self._room_with_image(1600, 800)
        with Image.open(room.image.path) as img:
            self.assertAlmostEqual(img.width / img.height, 2.0, places=1)
