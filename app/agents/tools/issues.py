from typing import Optional
from uuid import UUID

from langchain_core.tools import tool
from sqlmodel import Session

from app.decorators.db_session import with_db_session
from app.entities.orm_mappers import map_issue, map_issues
from app.entities.orm_models import IssueCategory, IssueStatus, IssueUrgency
from app.repositories.issue_repository import IssueRepository
from app.repositories.order_repository import OrderRepository


def _issue_repository(session: Session) -> IssueRepository:
    return IssueRepository(session)


def _order_repository(session: Session) -> OrderRepository:
    return OrderRepository(session)


@tool(description="Use this tool to list all issues available in the database.")
@with_db_session
def list_all_issues(session: Session):
    return map_issues(_issue_repository(session).list())


@tool(description="Use this tool to search for issues in the database.")
@with_db_session
def search_issues(
    session: Session,
    number: Optional[str] = None,
    description: Optional[str] = None,
    urgency: Optional[IssueUrgency] = None,
    category: Optional[IssueCategory] = None,
    order_id: Optional[UUID] = None,
    status: Optional[IssueStatus] = None,
):
    return map_issues(
        _issue_repository(session).list(
            number,
            description,
            urgency,
            category,
            order_id,
            status,
        )
    )


@tool(
    description="Use this tool to fetch the details of an issue given a specific issue ID."
)
@with_db_session
def get_issue_details(session: Session, issue_id: UUID):
    return map_issue(_issue_repository(session).get(issue_id))


@tool(
    description="Use this tool to update an issue's details given a specific issue ID."
)
@with_db_session
def update_issue(
    session: Session,
    issue_id_to_be_updated: UUID,
    number: Optional[str] = None,
    description: Optional[str] = None,
    conversation_summary: Optional[str] = None,
    urgency: Optional[IssueUrgency] = None,
    category: Optional[IssueCategory] = None,
    order_id: Optional[UUID] = None,
    status: Optional[IssueStatus] = None,
):
    repo = _issue_repository(session)
    updated = repo.update(
        issue_id_to_be_updated,
        number=number,
        description=description,
        urgency=urgency,
        category=category,
        order_id=order_id,
        status=status,
        conversation_summary=conversation_summary,
    )

    return map_issue(updated)


@tool(description="Use this tool to create a new issue in the database.")
@with_db_session
def create_issue(
    session: Session,
    number: str,
    description: str,
    order_number: str,
    category: Optional[IssueCategory] = None,
    urgency: Optional[IssueUrgency] = None,
) -> UUID:
    orders = _order_repository(session).list(order_number=order_number)

    if not orders:
        raise ValueError(f"Could not find order with number '{order_number}'")

    created = _issue_repository(session).create(
        number=number,
        description=description,
        order_id=orders[0].id,
        status=IssueStatus.open,
        category=category,
        urgency=urgency,
    )

    return created.id
