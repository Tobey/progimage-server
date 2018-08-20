import base64
import os
from unittest import mock

import magic
from django.test import TestCase
from rest_framework.test import APIClient

from prog_image.models import Image


root_dir = os.path.dirname(os.path.abspath(__file__))


class FakeResponse:

    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    @property
    def content(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception


class SiteTests(TestCase):

    fixtures = ['test']

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token a45e0eb347cc2d39a71a522c6c3f850ab577e73e')

    def test_upload_1_by_file(self):
        response = self.client.post('/images/', data={'image': self.image_file})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.all().count(), 1)

    def test_upload_2_by_file(self):
        response = self.client.post('/images/', data={'image': [self.image_file, self.image_file]})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.all().count(), 2)

    @mock.patch('requests.get')
    def test_upload_1_by_url(self, request_mock):
        request_mock.return_value = FakeResponse(self.image_file.read(), 200)

        response = self.client.post(
            '/images/', data={'image_url': ['https://fake-url.com/image.jpg']}
        )

        request_mock.assert_called()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.all().count(), 1)

    @mock.patch('requests.get')
    def test_upload_2_by_url(self, request_mock):
        image = open(os.path.join(root_dir, 'img', 'test_image_1.jpg'), 'rb')
        request_mock.return_value = FakeResponse(image.read(), 200)

        response = self.client.post(
            '/images/', data={"image_url": ["https://fake-url.com/image.jpg", "https://fake-url.com/image.jpg"]}
        )

        request_mock.assert_called()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.all().count(), 2)

    def test_retrieve_1(self):
        response = self.client.post('/images/', data={'image': self.image_file})
        pk = response.json()[0]['id']

        response = self.client.get(f'/images/{pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], pk)

    def test_retrieve_2(self):
        response = self.client.post(
            '/images/', data={'image': [self.image_file, self.image_file, self.image_file]}
        )

        # retrieve only 2
        ids = [image['id'] for image in response.json()[:2]]

        response = self.client.get(f'/images/?id__in=' + ','.join(ids))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(Image.objects.all().count(), 3)

    def test_convert_jpg_to_png(self):
        response = self.client.post('/images/', data={'image': self.image_file})
        pk = response.json()[0]['id']

        response = self.client.get(f'/images/{pk}/')
        image_data = base64.b64decode(response.json()['image']['data'])
        image_type = magic.from_buffer(image_data, mime=True)
        self.assertEqual(image_type, 'image/jpeg')

        response = self.client.get(f'/images/png/?id__in={pk}')
        image_data = base64.b64decode(response.json()['results'][0]['image']['data'])
        image_type = magic.from_buffer(image_data, mime=True)
        self.assertEqual(image_type, 'image/png')




    @property
    def image_file(self):
        return open(os.path.join(root_dir, 'img', 'test_image_1.jpg'), 'rb')