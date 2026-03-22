from typing import Any, Optional

from app.entities.orm_models import (
    Issue,
    Order,
    ISSUE_CATEGORY_DISPLAY,
    ISSUE_URGENCY_DISPLAY,
    ISSUE_STATUS_DISPLAY,
)


def map_order(order: Optional[Order]) -> Optional[dict[str, str]]:
    if not order:
        return None

    return {"id": str(order.id), "number": order.number, "po_number": order.po_number}


def map_orders(orders: list[Order]) -> list[dict[str, Any]]:
    return [map_order(o) for o in orders]


def map_issue(issue: Issue) -> Optional[dict[str, Any]]:
    if not issue:
        return None

    return {
        "id": str(issue.id),
        "number": issue.number,
        "description": issue.description,
        "order": map_order(issue.order),
        "category": ISSUE_CATEGORY_DISPLAY.get(issue.category),
        "urgency": ISSUE_URGENCY_DISPLAY.get(issue.urgency),
        "status": ISSUE_STATUS_DISPLAY.get(issue.status),
    }


def map_issues(issues: list[Issue]) -> list[dict[str, Any]]:
    return [map_issue(i) for i in issues]
