import importlib
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

importlib.import_module("tests.unit.agents.tools")

from app.entities.orm_mappers import map_issue, map_issues
from app.entities.orm_models import (
    Issue,
    IssueCategory,
    IssueStatus,
    IssueUrgency,
    Order,
)

from app.agents.tools import issues as issues_tools


class TestIssuesTools(TestCase):
    def test_list_all_issues_tool_description_mentions_issues(self):
        self.assertIn("issues", issues_tools.list_all_issues.description.lower())

    def test_search_issues_tool_description_mentions_search(self):
        self.assertIn("search", issues_tools.search_issues.description.lower())

    def test_get_issue_details_tool_description_mentions_issue(self):
        desc = issues_tools.get_issue_details.description.lower()
        self.assertIn("issue", desc)

    def test_update_issue_tool_description_mentions_update(self):
        desc = issues_tools.update_issue.description.lower()
        self.assertIn("update", desc)

    def test_create_issue_tool_description_mentions_create(self):
        desc = issues_tools.create_issue.description.lower()
        self.assertIn("create", desc)

    @patch("app.agents.tools.issues._issue_repository")
    def test_list_all_issues_returns_empty_when_repository_list_empty(
        self, mock_issue_repository: MagicMock
    ):
        mock_issue_repository.return_value.list.return_value = []

        result = issues_tools.list_all_issues.invoke({})

        self.assertEqual(result, [])
        mock_issue_repository.assert_called_once()
        self.assertIsInstance(mock_issue_repository.call_args.args[0], MagicMock)

    @patch("app.agents.tools.issues._issue_repository")
    def test_list_all_issues_returns_map_issues_of_repository_list(
        self, mock_issue_repository: MagicMock
    ):
        order_id = uuid4()
        rows = [
            Issue(
                id=uuid4(),
                number="ISS-A",
                description="a",
                conversation_summary="",
                order_id=order_id,
                status=IssueStatus.open,
            ),
            Issue(
                id=uuid4(),
                number="ISS-B",
                description="b",
                conversation_summary="",
                order_id=order_id,
                status=IssueStatus.resolved,
            ),
        ]
        mock_issue_repository.return_value.list.return_value = rows

        result = issues_tools.list_all_issues.invoke({})

        self.assertEqual(result, map_issues(rows))
        mock_issue_repository.assert_called_once()

    @patch("app.agents.tools.issues._issue_repository")
    def test_search_issues_passes_filters_to_repository_list(
        self, mock_issue_repository: MagicMock
    ):
        mock_issue_repository.return_value.list.return_value = []
        oid = uuid4()

        issues_tools.search_issues.invoke(
            {
                "number": "SO-1",
                "description": "outage",
                "urgency": IssueUrgency.high,
                "category": IssueCategory.billing,
                "order_id": oid,
                "status": IssueStatus.open,
            }
        )

        mock_issue_repository.return_value.list.assert_called_once_with(
            "SO-1",
            "outage",
            IssueUrgency.high,
            IssueCategory.billing,
            oid,
            IssueStatus.open,
        )

    @patch("app.agents.tools.issues._issue_repository")
    def test_get_issue_details_returns_map_issue_when_found(
        self, mock_issue_repository: MagicMock
    ):
        issue_id = uuid4()
        order_id = uuid4()
        row = Issue(
            id=issue_id,
            number="ISS-1",
            description="Printer jam",
            conversation_summary="summary",
            order_id=order_id,
            status=IssueStatus.in_progress,
            category=IssueCategory.technical_support,
            urgency=IssueUrgency.medium,
        )
        mock_issue_repository.return_value.get.return_value = row

        result = issues_tools.get_issue_details.invoke({"issue_id": issue_id})

        self.assertEqual(result, map_issue(row))
        mock_issue_repository.return_value.get.assert_called_once_with(issue_id)

    @patch("app.agents.tools.issues._issue_repository")
    def test_get_issue_details_returns_none_when_missing(
        self, mock_issue_repository: MagicMock
    ):
        issue_id = uuid4()
        mock_issue_repository.return_value.get.return_value = None

        result = issues_tools.get_issue_details.invoke({"issue_id": issue_id})

        self.assertIsNone(result)

    @patch("app.agents.tools.issues._issue_repository")
    def test_update_issue_returns_map_issue_when_repository_updates(
        self, mock_issue_repository: MagicMock
    ):
        issue_id = uuid4()
        order_id = uuid4()
        updated = Issue(
            id=issue_id,
            number="NEW",
            description="New desc",
            conversation_summary="S",
            order_id=order_id,
            status=IssueStatus.closed,
            category=IssueCategory.account,
            urgency=IssueUrgency.low,
        )
        mock_issue_repository.return_value.update.return_value = updated

        result = issues_tools.update_issue.invoke(
            {
                "issue_id_to_be_updated": issue_id,
                "number": "NEW",
                "description": "New desc",
                "conversation_summary": "S",
                "urgency": IssueUrgency.low,
                "category": IssueCategory.account,
                "order_id": order_id,
                "status": IssueStatus.closed,
            }
        )

        self.assertEqual(result, map_issue(updated))
        mock_issue_repository.return_value.update.assert_called_once_with(
            issue_id,
            number="NEW",
            description="New desc",
            urgency=IssueUrgency.low,
            category=IssueCategory.account,
            order_id=order_id,
            status=IssueStatus.closed,
            conversation_summary="S",
        )

    @patch("app.agents.tools.issues._issue_repository")
    def test_update_issue_returns_none_when_repository_returns_none(
        self, mock_issue_repository: MagicMock
    ):
        issue_id = uuid4()
        mock_issue_repository.return_value.update.return_value = None

        result = issues_tools.update_issue.invoke(
            {"issue_id_to_be_updated": issue_id, "number": "X"}
        )

        self.assertIsNone(result)

    @patch("app.agents.tools.issues._issue_repository")
    @patch("app.agents.tools.issues._order_repository")
    def test_create_issue_returns_new_id_when_order_exists(
        self,
        mock_order_repository: MagicMock,
        mock_issue_repository: MagicMock,
    ):
        order = Order(id=uuid4(), number="ORD-9", po_number="PO-9")
        mock_order_repository.return_value.list.return_value = [order]
        created = Issue(
            id=uuid4(),
            number="ISS-NEW",
            description="D",
            conversation_summary="",
            order_id=order.id,
            status=IssueStatus.open,
        )
        mock_issue_repository.return_value.create.return_value = created

        result = issues_tools.create_issue.invoke(
            {
                "number": "ISS-NEW",
                "description": "D",
                "order_number": "ORD-9",
                "category": IssueCategory.shipping,
                "urgency": IssueUrgency.critical,
            }
        )

        self.assertEqual(result, created.id)
        mock_order_repository.return_value.list.assert_called_once_with(
            order_number="ORD-9"
        )
        mock_issue_repository.return_value.create.assert_called_once_with(
            number="ISS-NEW",
            description="D",
            order_id=order.id,
            status=IssueStatus.open,
            category=IssueCategory.shipping,
            urgency=IssueUrgency.critical,
        )

    @patch("app.agents.tools.issues._issue_repository")
    @patch("app.agents.tools.issues._order_repository")
    def test_create_issue_raises_when_order_not_found(
        self,
        mock_order_repository: MagicMock,
        mock_issue_repository: MagicMock,
    ):
        mock_order_repository.return_value.list.return_value = []

        with self.assertRaises(ValueError) as ctx:
            issues_tools.create_issue.invoke(
                {
                    "number": "ISS-1",
                    "description": "D",
                    "order_number": "missing",
                }
            )

        self.assertIn("missing", str(ctx.exception))
        mock_issue_repository.return_value.create.assert_not_called()
