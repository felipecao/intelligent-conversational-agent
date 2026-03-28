import importlib
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

# When unittest loads this module by file path, parent ``__init__.py`` is skipped; import the
# package so ``tests.unit.agents.tools`` applies the ``with_db_session`` patch before tools load.
importlib.import_module("tests.unit.agents.tools")

from app.entities.orm_mappers import map_orders
from app.entities.orm_models import (
    ISSUE_CATEGORY_DISPLAY,
    ISSUE_STATUS_DISPLAY,
    ISSUE_URGENCY_DISPLAY,
    Order,
)

from app.agents.tools.master_data import (
    list_all_categories,
    list_all_orders,
    list_all_statuses,
    list_all_urgencies,
)


class TestMasterDataTools(TestCase):
    def test_list_all_categories_returns_issue_category_display_values(self):
        result = list_all_categories.invoke({})

        self.assertEqual(result, list(ISSUE_CATEGORY_DISPLAY.values()))

    def test_list_all_urgencies_returns_issue_urgency_display_values(self):
        result = list_all_urgencies.invoke({})

        self.assertEqual(result, list(ISSUE_URGENCY_DISPLAY.values()))

    def test_list_all_statuses_returns_issue_status_display_values(self):
        result = list_all_statuses.invoke({})

        self.assertEqual(result, list(ISSUE_STATUS_DISPLAY.values()))

    def test_list_all_categories_tool_description_mentions_example_ids(self):
        description = list_all_categories.description

        self.assertIn("billing", description)
        self.assertIn("technical_support", description)

    def test_list_all_urgencies_tool_description_mentions_example_ids(self):
        description = list_all_urgencies.description

        self.assertIn("high", description)
        self.assertIn("low", description)

    def test_list_all_statuses_tool_description_mentions_example_ids(self):
        description = list_all_statuses.description

        self.assertIn("closed", description)
        self.assertIn("open", description)

    def test_list_all_orders_tool_description_mentions_orders(self):
        self.assertIn("orders", list_all_orders.description.lower())

    @patch("app.agents.tools.master_data._order_repository")
    def test_list_all_orders_returns_empty_list_when_repository_returns_no_orders(
        self, mock_order_repository: MagicMock
    ):
        mock_order_repository.return_value.list.return_value = []

        result = list_all_orders.invoke({})

        self.assertEqual(result, [])
        mock_order_repository.assert_called_once()
        self.assertIsInstance(mock_order_repository.call_args.args[0], MagicMock)

    @patch("app.agents.tools.master_data._order_repository")
    def test_list_all_orders_returns_map_orders_of_repository_list(
        self, mock_order_repository: MagicMock
    ):
        orders = [
            Order(id=uuid4(), number="ORD-C", po_number="PO-C"),
            Order(id=uuid4(), number="ORD-B", po_number="PO-B"),
        ]
        mock_order_repository.return_value.list.return_value = orders

        result = list_all_orders.invoke({})

        self.assertEqual(result, map_orders(orders))
        mock_order_repository.assert_called_once()
        self.assertIsInstance(mock_order_repository.call_args.args[0], MagicMock)
