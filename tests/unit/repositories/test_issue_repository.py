from uuid import uuid4, UUID

from app.entities.orm_models import (
    Issue,
    IssueCategory,
    IssueStatus,
    IssueUrgency,
    Order,
)
from app.repositories.issue_repository import IssueRepository
from tests.support.repositories.base_repository_test import BaseRepositoryTest


class TestIssueRepository(BaseRepositoryTest):
    def setUp(self):
        super().setUp()
        self._repository = IssueRepository(self.session)

    def test_get_returns_issue_when_it_exists(self):
        order = self._save_order()
        saved = self._save_issue(
            number="ISS-1",
            description="Printer jam",
            order_id=order.id,
            status=IssueStatus.in_progress,
        )

        found = self._repository.get(saved.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.number, "ISS-1")
        self.assertEqual(found.description, "Printer jam")
        self.assertEqual(found.status, IssueStatus.in_progress)

    def test_get_returns_none_when_issue_does_not_exist(self):
        found = self._repository.get(uuid4())

        self.assertIsNone(found)

    def test_list_returns_all_issues_ordered_by_number_descending(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="ISS-A",
                    description="a",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="ISS-C",
                    description="c",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="ISS-B",
                    description="b",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list()

        self.assertEqual(len(rows), 3)
        self.assertEqual([i.number for i in rows], ["ISS-C", "ISS-B", "ISS-A"])

    def test_list_filters_by_partial_case_insensitive_number(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="ISS-1001",
                    description="d1",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="ISS-2002",
                    description="d2",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="OTHER-1",
                    description="d3",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list(number="iss-10")

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["ISS-1001"])

    def test_list_with_empty_string_number_returns_all_issues(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="X-1",
                    description="a",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="Y-2",
                    description="b",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list(number="")

        self.assertEqual(len(rows), 2)
        self.assertCountEqual([i.number for i in rows], ["X-1", "Y-2"])

    def test_list_filters_by_partial_case_insensitive_description(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="N1",
                    description="Network outage in building A",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="N2",
                    description="Billing question",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list(description="BUILDING a")

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["N1"])

    def test_list_with_empty_string_description_returns_all_issues(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="A1",
                    description="one",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="A2",
                    description="two",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list(description="")

        self.assertEqual(len(rows), 2)

    def test_list_filters_by_urgency(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="U1",
                    description="a",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    urgency=IssueUrgency.high,
                ),
                Issue(
                    number="U2",
                    description="b",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    urgency=IssueUrgency.low,
                ),
            ]
        )

        rows = self._repository.list(urgency=IssueUrgency.high)

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["U1"])

    def test_list_filters_by_category(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="C1",
                    description="a",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    category=IssueCategory.billing,
                ),
                Issue(
                    number="C2",
                    description="b",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    category=IssueCategory.shipping,
                ),
            ]
        )

        rows = self._repository.list(category=IssueCategory.billing)

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["C1"])

    def test_list_filters_by_order_id(self):
        order_one = self._save_order("O-1", "P1")
        order_two = self._save_order("O-2", "P2")
        self.save_entities(
            [
                Issue(
                    number="F1",
                    description="a",
                    conversation_summary="",
                    order_id=order_one.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="F2",
                    description="b",
                    conversation_summary="",
                    order_id=order_two.id,
                    status=IssueStatus.open,
                ),
            ]
        )

        rows = self._repository.list(order_id=order_two.id)

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["F2"])

    def test_list_filters_by_status(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="S1",
                    description="a",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                ),
                Issue(
                    number="S2",
                    description="b",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.resolved,
                ),
            ]
        )

        rows = self._repository.list(status=IssueStatus.resolved)

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["S2"])

    def test_list_combines_filters(self):
        order = self._save_order()
        self.save_entities(
            [
                Issue(
                    number="M1",
                    description="match",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    urgency=IssueUrgency.critical,
                ),
                Issue(
                    number="M2",
                    description="match",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.closed,
                    urgency=IssueUrgency.critical,
                ),
                Issue(
                    number="M3",
                    description="other",
                    conversation_summary="",
                    order_id=order.id,
                    status=IssueStatus.open,
                    urgency=IssueUrgency.critical,
                ),
            ]
        )

        rows = self._repository.list(
            description="match",
            status=IssueStatus.open,
            urgency=IssueUrgency.critical,
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual([i.number for i in rows], ["M1"])

    def test_create_persists_issue_and_returns_it(self):
        order = self._save_order()

        created = self._repository.create(
            number="NEW-1",
            description="New ticket",
            order_id=order.id,
            status=IssueStatus.open,
            category=IssueCategory.account,
            urgency=IssueUrgency.medium,
        )

        self.assertIsNotNone(created.id)
        self.assertEqual(created.number, "NEW-1")
        self.assertEqual(created.description, "New ticket")
        self.assertEqual(created.order_id, order.id)
        self.assertEqual(created.status, IssueStatus.open)
        self.assertEqual(created.category, IssueCategory.account)
        self.assertEqual(created.urgency, IssueUrgency.medium)

        loaded = self._repository.get(created.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.number, "NEW-1")

    def test_update_returns_none_when_issue_does_not_exist(self):
        updated = self._repository.update(uuid4(), number="X")

        self.assertIsNone(updated)

    def test_update_applies_only_provided_fields(self):
        order_one = self._save_order("O-1", "P1")
        order_two = self._save_order("O-2", "P2")
        issue = self._save_issue(
            number="OLD-NUM",
            description="Old desc",
            order_id=order_one.id,
            status=IssueStatus.open,
            category=IssueCategory.billing,
            urgency=IssueUrgency.low,
            conversation_summary="Old summary",
        )

        result = self._repository.update(
            issue.id,
            number="NEW-NUM",
            order_id=order_two.id,
            status=IssueStatus.resolved,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.number, "NEW-NUM")
        self.assertEqual(result.description, "Old desc")
        self.assertEqual(result.conversation_summary, "Old summary")
        self.assertEqual(result.order_id, order_two.id)
        self.assertEqual(result.category, IssueCategory.billing)
        self.assertEqual(result.urgency, IssueUrgency.low)
        self.assertEqual(result.status, IssueStatus.resolved)

    def test_update_can_set_conversation_summary(self):
        order = self._save_order()
        issue = self._save_issue(
            number="E1",
            description="d",
            order_id=order.id,
            status=IssueStatus.open,
        )

        result = self._repository.update(
            issue.id,
            conversation_summary="Synced from chat",
        )

        self.assertEqual(result.conversation_summary, "Synced from chat")
        self.assertEqual(result.description, "d")

    def _save_order(self, number: str = "ORD-1", po_number: str = "PO-1") -> Order:
        return self.save_entity(Order(number=number, po_number=po_number))

    def _save_issue(
        self,
        number: str,
        description: str,
        order_id: UUID,
        status: IssueStatus = IssueStatus.open,
        category: IssueCategory | None = None,
        urgency: IssueUrgency | None = None,
        conversation_summary: str = "",
    ) -> Issue:
        return self.save_entity(
            Issue(
                number=number,
                description=description,
                conversation_summary=conversation_summary,
                order_id=order_id,
                status=status,
                category=category,
                urgency=urgency,
            )
        )
