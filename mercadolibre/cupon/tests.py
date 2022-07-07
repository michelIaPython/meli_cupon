# DJANGO
from django.urls import reverse
from django.test import TestCase, RequestFactory

# PYTHON
import json
import asyncio

# DJANGO REST FRAMEWORK
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

# MODELS
from cupon.models import CuponModel

# VIEWS
from cupon.views import CuponView

# UTILS
from cupon.utils import get_number_items, perform_db, remove_empty_items


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
                "amount": 3533.2799999999997,
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


class CreateUpdatedb(TestCase):
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


class TestInternalFunctions(TestCase):
    def setUp(self) -> None:
        self.LIST_ITEMS = [
            "MLM13877783",
            "MLM1392572571",
            "MLM1336615409",
            "MLM1346645397",
            "MLM1330350407",
        ]
        request = RequestFactory().post("http://127.0.0.1:8000/cupon/")
        self.view = CuponView()
        self.view.setup(request)
        return super().setUp()

    def test_method_get_all_items(self):

        response = asyncio.run(self.view.get_all_items(self.LIST_ITEMS))
        self.assertIsInstance(response, list)
        for each_element in response:
            self.assertTrue(isinstance(each_element, dict))

    def test_remove_empty_items_none(self):

        response = asyncio.run(self.view.get_all_items(self.LIST_ITEMS))
        without_empty = remove_empty_items(response)
        print(without_empty)
        for each in without_empty:
            self.assertIsNotNone(next(iter(each.keys())))
            self.assertIsNotNone(next(iter(each.values())))
