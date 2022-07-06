# DJANGO
from django.urls import reverse

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
        print(sample_payload)
        response = self.client.post("http://127.0.0.1:8000/cupon/", sample_payload)
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """def test_bad_payload(self):
        sample_payload = {[]}

        response = self.client.post("http://127.0.0.1:8000/cupon/", sample_payload)
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)"""
