from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.repositories.db_functions import ilike_partial
from app.entities.orm_models import Issue, IssueCategory, IssueStatus, IssueUrgency


class IssueRepository:
    def __init__(self, session: Session):
        self._session = session

    def get(self, _id: UUID) -> Optional[Issue]:
        return self._session.get(Issue, _id)

    def list(
        self,
        number: Optional[str] = None,
        description: Optional[str] = None,
        urgency: Optional[IssueUrgency] = None,
        category: Optional[IssueCategory] = None,
        order_id: Optional[UUID] = None,
        status: Optional[IssueStatus] = None,
    ) -> list[Issue]:
        query = select(Issue)

        if number is not None and number != "":
            query = query.where(ilike_partial(Issue.number, number))
        if description is not None and description != "":
            query = query.where(ilike_partial(Issue.description, description))
        if urgency is not None:
            query = query.where(Issue.urgency == urgency)
        if category is not None:
            query = query.where(Issue.category == category)
        if order_id is not None:
            query = query.where(Issue.order_id == order_id)
        if status is not None:
            query = query.where(Issue.status == status)

        query = query.order_by(Issue.number.desc())

        return list(self._session.exec(query))

    def create(
        self,
        number: str,
        description: str,
        order_id: UUID,
        status: IssueStatus,
        category: Optional[IssueCategory] = None,
        urgency: Optional[IssueUrgency] = None,
    ) -> Issue:
        issue = Issue(
            number=number,
            description=description,
            order_id=order_id,
            status=status,
            category=category,
            urgency=urgency,
        )

        self._session.add(issue)
        self._session.flush()
        self._session.refresh(issue)

        return issue

    def update(
        self,
        issue_id: UUID,
        number: Optional[str] = None,
        description: Optional[str] = None,
        conversation_summary: Optional[str] = None,
        order_id: Optional[UUID] = None,
        category: Optional[IssueCategory] = None,
        urgency: Optional[IssueUrgency] = None,
        status: Optional[IssueStatus] = None,
    ) -> Optional[Issue]:
        issue = self._session.get(Issue, issue_id)

        if issue is None:
            return None
        if number is not None:
            issue.number = number
        if description is not None:
            issue.description = description
        if conversation_summary is not None:
            issue.conversation_summary = conversation_summary
        if order_id is not None:
            issue.order_id = order_id
        if category is not None:
            issue.category = category
        if urgency is not None:
            issue.urgency = urgency
        if status is not None:
            issue.status = status

        self._session.add(issue)
        self._session.flush()
        self._session.refresh(issue)

        return issue
