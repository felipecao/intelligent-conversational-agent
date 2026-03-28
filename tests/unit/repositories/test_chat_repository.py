from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.entities.orm_models import Chat
from app.repositories.chat_repository import ChatRepository
from tests.support.repositories.base_repository_test import BaseRepositoryTest


class TestChatRepository(BaseRepositoryTest):
    def setUp(self):
        super().setUp()
        self._repository = ChatRepository(self.session)

    def test_get_returns_chat_when_it_exists(self):
        saved = self._save_chat(
            "Support thread",
            chat_history=[{"role": "user", "content": "Hi"}],
        )

        found = self._repository.get(saved.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.title, "Support thread")
        self.assertEqual(found.chat_history, [{"role": "user", "content": "Hi"}])

    def test_get_returns_none_when_chat_does_not_exist(self):
        found = self._repository.get(uuid4())

        self.assertIsNone(found)

    def test_list_all_returns_chats_ordered_by_created_at_descending(self):
        base_timestamp = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        self.save_entities(
            [
                Chat(
                    title="Older",
                    chat_history=[],
                    created_at=base_timestamp,
                ),
                Chat(
                    title="Newer",
                    chat_history=[],
                    created_at=base_timestamp + timedelta(hours=1),
                ),
            ]
        )

        rows = self._repository.list_all()

        self.assertEqual(len(rows), 2)
        self.assertEqual([c.title for c in rows], ["Newer", "Older"])

    def test_create_persists_chat_with_default_empty_history(self):
        created = self._repository.create(title="Empty history")

        self.assertIsNotNone(created.id)
        self.assertEqual(created.title, "Empty history")
        self.assertEqual(created.chat_history, [])

        loaded = self._repository.get(created.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.chat_history, [])

    def test_create_accepts_custom_chat_history(self):
        history = [{"role": "assistant", "content": "Hello"}]
        created = self._repository.create(title="With messages", chat_history=history)

        self.assertEqual(created.chat_history, history)

        loaded = self._repository.get(created.id)
        self.assertEqual(loaded.chat_history, history)

    def test_update_returns_none_when_chat_does_not_exist(self):
        updated = self._repository.update(uuid4(), title="X")

        self.assertIsNone(updated)

    def test_update_applies_only_provided_fields(self):
        chat = self._save_chat(
            "Original title",
            chat_history=[{"role": "user", "content": "ping"}],
        )

        result = self._repository.update(chat.id, title="Updated title")

        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Updated title")
        self.assertEqual(result.chat_history, [{"role": "user", "content": "ping"}])

    def test_update_can_replace_chat_history(self):
        chat = self._save_chat("T", chat_history=[{"role": "user", "content": "a"}])
        new_history = [{"role": "user", "content": "b"}]

        result = self._repository.update(chat.id, chat_history=new_history)

        self.assertEqual(result.title, "T")
        self.assertEqual(result.chat_history, new_history)

    def _save_chat(
        self,
        title: str,
        chat_history: list | None = None,
        created_at: datetime | None = None,
    ) -> Chat:
        data: dict = {
            "title": title,
            "chat_history": list(chat_history or []),
        }

        if created_at is not None:
            data["created_at"] = created_at

        return self.save_entity(Chat(**data))
