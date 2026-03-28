from typing import Any, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.entities.orm_models import Chat


class ChatRepository:
    def __init__(self, session: Session):
        self._session = session

    def get(self, _id: UUID) -> Optional[Chat]:
        return self._session.get(Chat, _id)

    def list_all(self) -> list[Chat]:
        query = select(Chat).order_by(Chat.created_at.desc())
        return list(self._session.exec(query))

    def create(self, title: str, chat_history: Optional[list[Any]] = None) -> Chat:
        chat = Chat(title=title, chat_history=list(chat_history or []))
        self._session.add(chat)
        self._session.commit()
        self._session.refresh(chat)
        return chat

    def update(
        self,
        _id: UUID,
        *,
        title: Optional[str] = None,
        chat_history: Optional[list[Any]] = None,
    ) -> Optional[Chat]:
        chat = self.get(_id)
        if chat is None:
            return None
        if title is not None:
            chat.title = title
        if chat_history is not None:
            chat.chat_history = list(chat_history)
        self._session.add(chat)
        self._session.commit()
        self._session.refresh(chat)
        return chat
