# DJANGO
from django.urls import reverse
from django.test import TestCase

# PYTHON
import json

# DJANGO REST FRAMEWORK
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

# MODELS
from cupon.models import CuponModel


class ItemTestCase(APITestCase):
    def test_items(self):
        sample_payload = {
            "item_ids": [
                "MLM13877783",
                "MLM1392572571",
                "MLM1336615409",
                "MLM1346645397",
                "MLM1330350407",
            ],
            "amount": 3789,
        }

        response = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_2 = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload),
            content_type="application/json",
        )

        self.assertEqual(
            json.loads(response_2.content),
            {
                "items_ids": ["MLM1336615409", "MLM1330350407", "MLM1346645397"],
                "amount": 3540.88,
            },
        )

    def test_bad_payload(self):
        sample_payload = {"amount": 12}

        response = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_stats(self):

        response = self.client.get("http://127.0.0.1:8000/cupon/stats/")
        self.assertAlmostEqual(response.status_code, status.HTTP_200_OK)


class Create_Update_db(TestCase):
    """@classmethod
    def setUpTestModel(cls):
        cls.item = CuponModel.objects.create(item_id="TEST1", price=129.12)

    def test_information(self):
        self.assertIsInstance(self.item.item_id, str)
        self.assertIsInstance(self.item.price, int)"""

    def test_model_fields(self):

        item = CuponModel.objects.create(item_id="TEST1", price=129.12)
        self.assertEquals(str(item), "TEST1")
        self.assertTrue(isinstance(item, CuponModel))
