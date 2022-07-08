# DJANGO
from django.test import TestCase, RequestFactory
from django.db.models import F

# PYTHON
import json
import asyncio

# DJANGO REST FRAMEWORK
from rest_framework.test import APITestCase
from rest_framework import status

# MODELS
from cupon.models import CuponModel

# VIEWS
from cupon.views import CuponView

# UTILS
from cupon.utils import get_number_items, perform_db, remove_empty_equals_items


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
                "amount": 3533.28,
            },
        )

    def test_bad_payload(self):
        sample_payload = {"amount": 12}
        sample_payload_2 = {
            "item_ids": [
                "MLM13877783",
                "MLM1392572571",
                "MLM1336615409",
                "MLM1346645397",
                "MLM1330350407",
            ],
            "amount": "testing bad amount",
        }

        sample_payload_3 = {
            "item_ids": [
                "MLM13877783",
                "MLM1392572571",
                "MLM1336615409",
                "MLM1346645397",
                "MLM1330350407",
            ],
        }

        response = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_2 = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload_2),
            content_type="application/json",
        )
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

        response_3 = self.client.post(
            "http://127.0.0.1:8000/cupon/",
            json.dumps(sample_payload_3),
            content_type="application/json",
        )
        self.assertEqual(response_3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_stats(self):

        response = self.client.get("http://127.0.0.1:8000/cupon/stats/")
        self.assertAlmostEqual(response.status_code, status.HTTP_200_OK)


class CreateUpdatedb(TestCase):
    def test_model_fields(self):

        item = CuponModel.objects.create(item_id="TEST1", price=129.12)
        self.assertEquals(str(item), "TEST1")
        self.assertTrue(isinstance(item, CuponModel))


class TestInternalFunctions(TestCase):
    def setUp(self) -> None:

        self.LIST_EQUALS = [
            "MLM13877783",
            "MLM1392572571",
            "MLM1336615409",
            "MLM1346645397",
            "MLM1330350407",
            "MLM1392572571",
        ]

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
        without_empty = remove_empty_equals_items(response)

        for each in without_empty:
            self.assertIsNotNone(next(iter(each.keys())))
            self.assertIsNotNone(next(iter(each.values())))

    def test_remove_equals_items_none(self):
        response = asyncio.run(self.view.get_all_items(self.LIST_EQUALS))
        without_equals = remove_empty_equals_items(response)
        equals_items = []
        for each in without_equals:
            key = next(iter(each.keys()))
            if key in without_equals:
                equals_items.append()
        print(equals_items)
        self.assertListEqual(equals_items, [])


class TestDB(TestCase):
    def setUp(self):
        self.cupon = CuponModel.objects.create(item_id="TESTINGDB1", price=12345)

    def test_send_data_db(self):

        response_db = perform_db({"TESTINGDB2": 3949.58})
        self.assertIsInstance(response_db, dict)
        self.assertEquals(
            CuponModel.objects.get(item_id="TESTINGDB2").item_id, "TESTINGDB2"
        )

    def test_send_several_data_db(self):
        elements = [
            {"TESTINGSEVERAL1": 3949.58},
            {"TESTINGSEVERAL2": 635.28},
            {"TESTINGSEVERAL3": 1499},
            {"TESTINGSEVERAL14": 1399},
        ]
        for each_element in elements:

            response_db = perform_db(each_element)
            key = next(iter(response_db.keys()))
            self.assertIsInstance(response_db, dict)
            self.assertEquals(CuponModel.objects.get(item_id=key).item_id, key)

    def test_increment(self):
        increment, _ = CuponModel.objects.update_or_create(item_id=self.cupon.item_id)
        increment.quantity = F("quantity") + 1
        increment.save(update_fields=["quantity"])
        self.assertEquals(CuponModel.objects.get(item_id="TESTINGDB1").quantity, 2)

    def test_increment_function(self):
        perform_db({"TESTINGDB1": 12345})
        self.assertEquals(CuponModel.objects.get(item_id="TESTINGDB1").quantity, 2)


class TestRetriveItems(TestCase):
    def setUp(self) -> None:
        self.list_items = {
            "TESTFINAL1": 100,
            "TESTFINAL2": 210,
            "TESTFINAL3": 260,
            "TESTFINAL4": 80,
            "TESTFINAL5": 90,
        }
        self.amount = 500

    def test_get_items(self):
        items_amount = get_number_items(self.list_items, self.amount)
        self.assertDictEqual(
            items_amount,
            {
                "items_ids": [
                    "TESTFINAL4",
                    "TESTFINAL5",
                    "TESTFINAL1",
                    "TESTFINAL2",
                ],
                "amount": 480,
            },
        )
