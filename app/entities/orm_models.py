import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM, JSONB
from sqlmodel import Field, Relationship, SQLModel


class IssueStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    waiting_on_customer = "waiting_on_customer"
    resolved = "resolved"
    closed = "closed"


ISSUE_STATUS_DISPLAY: dict[IssueStatus, str] = {
    IssueStatus.open: "Open",
    IssueStatus.in_progress: "In progress",
    IssueStatus.waiting_on_customer: "Waiting on customer",
    IssueStatus.resolved: "Resolved",
    IssueStatus.closed: "Closed",
}


class IssueCategory(str, enum.Enum):
    billing = "billing"
    shipping = "shipping"
    product_defect = "product_defect"
    account = "account"
    technical_support = "technical_support"


ISSUE_CATEGORY_DISPLAY: dict[IssueCategory, str] = {
    IssueCategory.billing: "Billing",
    IssueCategory.shipping: "Shipping",
    IssueCategory.product_defect: "Product defect",
    IssueCategory.account: "Account",
    IssueCategory.technical_support: "Technical support",
}


class IssueUrgency(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


ISSUE_URGENCY_DISPLAY: dict[IssueUrgency, str] = {
    IssueUrgency.low: "Low",
    IssueUrgency.medium: "Medium",
    IssueUrgency.high: "High",
    IssueUrgency.critical: "Critical",
}


_issue_status_pg = PG_ENUM(
    IssueStatus,
    name="issue_status",
    create_type=False,
)
_issue_category_pg = PG_ENUM(
    IssueCategory,
    name="issue_category",
    create_type=False,
)
_issue_urgency_pg = PG_ENUM(
    IssueUrgency,
    name="issue_urgency",
    create_type=False,
)


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    number: str
    po_number: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Issue(SQLModel, table=True):
    __tablename__ = "issues"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    number: str
    description: str
    conversation_summary: str

    order_id: uuid.UUID = Field(foreign_key="orders.id")
    order: Optional[Order] = Relationship()

    category: Optional[IssueCategory] = Field(
        default=None,
        sa_column=Column(_issue_category_pg, nullable=True),
    )
    urgency: Optional[IssueUrgency] = Field(
        default=None,
        sa_column=Column(_issue_urgency_pg, nullable=True),
    )
    status: IssueStatus = Field(sa_column=Column(_issue_status_pg, nullable=False))


class Chat(SQLModel, table=True):
    __tablename__ = "chats"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    chat_history: list[Any] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
