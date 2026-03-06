from django.test import TestCase
from django.urls import reverse

from .models import Order, User


class PosOrderApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="pass1234",
            full_name="Test User",
            email="tester@example.com",
        )
        self.client.force_login(self.user)

    def test_place_order_creates_order(self):
        response = self.client.post(
            reverse("pos_order_place"),
            data={
                "items": [
                    {"item_name": "Grilled Chicken", "quantity": 2, "unit_price": 33},
                    {"item_name": "Chicken Taco", "quantity": 1, "unit_price": 45},
                ],
                "order_type": "Dine In",
                "customer_name": "Walk-in Customer",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, "Placed")
        self.assertEqual(order.items.count(), 2)

    def test_place_order_rejects_empty_cart(self):
        response = self.client.post(
            reverse("pos_order_place"),
            data={"items": []},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
