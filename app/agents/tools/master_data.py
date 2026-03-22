from langchain_core.tools import tool
from sqlmodel import Session

from app.decorators.db_session import with_db_session
from app.entities.orm_mappers import (
    map_orders,
)
from app.entities.orm_models import (
    ISSUE_CATEGORY_DISPLAY,
    ISSUE_URGENCY_DISPLAY,
    ISSUE_STATUS_DISPLAY,
)
from app.repositories.order_repository import OrderRepository


def _order_repository(session: Session) -> OrderRepository:
    return OrderRepository(session)


@tool(
    description="Use this tool to list all valid issue category values (id is the enum value to pass to tools, e.g. billing, technical_support)."
)
def list_all_categories():
    return list(ISSUE_CATEGORY_DISPLAY.values())


@tool(
    description="Use this tool to list all valid issue urgency values (id is the enum value to pass to tools, e.g. high, low)."
)
def list_all_urgencies():
    return list(ISSUE_URGENCY_DISPLAY.values())


@tool(
    description="Use this tool to list all valid issue status values (id is the enum value to pass to tools, e.g. closed, open)."
)
def list_all_statuses():
    return list(ISSUE_STATUS_DISPLAY.values())


@tool(description="Use this tool to list all orders registered in the system.")
@with_db_session
def list_all_orders(session: Session):
    return map_orders(_order_repository(session).list())
