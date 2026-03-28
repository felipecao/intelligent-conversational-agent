import uuid

from app.entities.orm_models import Order
from app.repositories.order_repository import OrderRepository
from tests.support.repositories.base_repository_test import BaseRepositoryTest


class TestOrderRepository(BaseRepositoryTest):
    def setUp(self):
        super().setUp()
        self._repository = OrderRepository(self.session)

    def test_get_returns_order_when_it_exists(self):
        saved = super().save_entity(Order(number="SO-1001", po_number="PO-500"))

        found = self._repository.get(saved.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.number, "SO-1001")
        self.assertEqual(found.po_number, "PO-500")

    def test_get_returns_none_when_order_does_not_exist(self):
        found = self._repository.get(uuid.uuid4())

        self.assertIsNone(found)

    def test_list_returns_all_orders_ordered_by_number_descending(self):
        self.save_entities(
            [
                Order(number="ORD-A", po_number="P1"),
                Order(number="ORD-C", po_number="P2"),
                Order(number="ORD-B", po_number="P3"),
            ]
        )

        rows = self._repository.list()

        self.assertEqual(len(rows), 3)
        self.assertEqual([o.number for o in rows], ["ORD-C", "ORD-B", "ORD-A"])

    def test_list_filters_by_partial_case_insensitive_order_number(self):
        self.save_entities(
            [
                Order(number="SO-1001", po_number="P1"),
                Order(number="SO-2002", po_number="P2"),
                Order(number="OTHER-1", po_number="P3"),
            ]
        )

        rows = self._repository.list(order_number="so-10")

        self.assertEqual(len(rows), 1)
        self.assertEqual([o.number for o in rows], ["SO-1001"])

    def test_list_with_none_order_number_returns_all_orders(self):
        self.save_entities(
            [
                Order(number="X-1", po_number="P1"),
                Order(number="Y-2", po_number="P2"),
            ]
        )

        rows = self._repository.list(None)

        self.assertEqual(len(rows), 2)
        self.assertCountEqual([o.number for o in rows], ["X-1", "Y-2"])

    def test_list_with_blank_order_number_returns_all_orders(self):
        self.save_entities(
            [
                Order(number="ONLY", po_number="P1"),
            ]
        )

        rows = self._repository.list("     ")

        self.assertEqual(len(rows), 1)
        self.assertEqual(len(self._repository.list("   ")), 1)
