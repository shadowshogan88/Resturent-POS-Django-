from django.test import TestCase
from django.urls import reverse

from .models import AuditLog, DiningTable, Order, User


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


class TableManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager",
            password="pass1234",
            full_name="Table Manager",
            email="manager@example.com",
            role="Admin",
        )
        self.client.force_login(self.user)

    def test_table_create_writes_audit_log_and_shows_in_audit_page(self):
        response = self.client.post(
            reverse("tables_add"),
            data={
                "name": "VIP Table",
                "floor": "2nd",
                "image_name": "tables-14.svg",
                "guest_capacity": "8",
                "status": "Available",
                "next": reverse("page", kwargs={"page": "table"}),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(DiningTable.objects.filter(name="VIP Table").exists())
        log = AuditLog.objects.filter(action="table_created", target="VIP Table").first()
        self.assertIsNotNone(log)

        audit_response = self.client.get(reverse("page", kwargs={"page": "audit-report"}))
        self.assertContains(audit_response, "VIP Table")
        self.assertContains(audit_response, "Table Created")

    def test_table_update_writes_audit_log(self):
        table = DiningTable.objects.create(
            name="Garden Table",
            floor="1st",
            image_name="tables-01.svg",
            guest_capacity=4,
            status="Available",
        )

        response = self.client.post(
            reverse("tables_update"),
            data={
                "table_id": str(table.id),
                "name": "Garden Table Updated",
                "floor": "3rd",
                "image_name": "tables-06.svg",
                "guest_capacity": "10",
                "status": "Booked",
                "next": reverse("page", kwargs={"page": "table"}),
            },
        )

        self.assertEqual(response.status_code, 302)
        table.refresh_from_db()
        self.assertEqual(table.name, "Garden Table Updated")
        self.assertEqual(table.status, "Booked")
        self.assertTrue(
            AuditLog.objects.filter(action="table_updated", target="Garden Table Updated").exists()
        )

    def test_table_delete_writes_audit_log(self):
        table = DiningTable.objects.create(
            name="Delete Table",
            floor="1st",
            image_name="tables-02.svg",
            guest_capacity=4,
            status="Available",
        )

        response = self.client.post(
            reverse("tables_delete"),
            data={
                "table_id": str(table.id),
                "next": reverse("page", kwargs={"page": "table"}),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(DiningTable.objects.filter(id=table.id).exists())
        self.assertTrue(
            AuditLog.objects.filter(action="table_deleted", target="Delete Table").exists()
        )


class PosTableSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cashier",
            password="pass1234",
            full_name="Cashier User",
            email="cashier@example.com",
        )
        self.table = DiningTable.objects.create(
            name="Sync Table",
            floor="1st",
            image_name="tables-01.svg",
            guest_capacity=6,
            status="Available",
        )
        self.client.force_login(self.user)

    def test_place_order_marks_matching_table_booked(self):
        response = self.client.post(
            reverse("pos_order_place"),
            data={
                "items": [{"item_name": "Burger", "quantity": 1, "unit_price": 20}],
                "order_type": "Dine In",
                "customer_name": "Walk-in Customer",
                "table_name": self.table.name,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.table.refresh_from_db()
        self.assertEqual(self.table.status, "Booked")

    def test_cancel_order_releases_table_when_no_active_orders_exist(self):
        self.client.post(
            reverse("pos_order_place"),
            data={
                "items": [{"item_name": "Burger", "quantity": 1, "unit_price": 20}],
                "order_type": "Dine In",
                "customer_name": "Walk-in Customer",
                "table_name": self.table.name,
            },
            content_type="application/json",
        )

        cancel_response = self.client.post(reverse("pos_order_cancel"))

        self.assertEqual(cancel_response.status_code, 200)
        self.table.refresh_from_db()
        self.assertEqual(self.table.status, "Available")
