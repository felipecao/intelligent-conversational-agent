from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.repositories.db_functions import ilike_partial
from app.entities.orm_models import Order


class OrderRepository:
    def __init__(self, session: Session):
        self._session = session

    def get(self, _id: UUID) -> Optional[Order]:
        return self._session.get(Order, _id)

    def list(self, order_number: Optional[str] = None) -> list[Order]:
        query = select(Order)

        if order_number is not None and order_number.strip() != "":
            query = query.where(ilike_partial(Order.number, order_number))

        query = query.order_by(Order.number.desc())

        return list(self._session.exec(query))
