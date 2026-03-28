import os
import sys
import importlib
from pathlib import Path
from unittest import TestCase
from urllib.parse import urlparse

import psycopg2
from sqlalchemy import text
from sqlmodel import Session
from testcontainers.postgres import PostgresContainer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_INITIAL_SCHEMA_SQL = PROJECT_ROOT / "db-migrations" / "0001_initial-schema.sql"


class BaseRepositoryTest(TestCase):
    _postgres = PostgresContainer("postgres:15")

    @classmethod
    def setUpClass(cls):
        cls._postgres.start()

        cls.create_schemas(cls._postgres)
        os.environ["DATABASE_URL"] = cls._postgres.get_connection_url(
            cls._postgres.get_container_host_ip()
        )

        # orm_session reads DATABASE_URL at import time; reload if already loaded (e.g. full suite).
        name = "app.entities.orm_session"
        if name in sys.modules:
            orm_session_module = importlib.reload(sys.modules[name])
        else:
            orm_session_module = importlib.import_module(name)

        cls._engine = orm_session_module.engine

        # Register table metadata on SQLModel (no-op if only using migration SQL for DDL).
        import app.entities.orm_models  # noqa: F401

    @classmethod
    def tearDownClass(cls):
        cls._engine.dispose()
        cls._postgres.stop()

    @classmethod
    def create_schemas(cls, postgres: PostgresContainer):
        url = urlparse(postgres.get_connection_url())

        dbname = url.path.lstrip("/")
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        try:
            schema_sql = _INITIAL_SCHEMA_SQL.read_text()
            statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
            with connection.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
            connection.commit()
        finally:
            connection.close()

    def setUp(self):
        self.session = Session(self._engine)

    def tearDown(self):
        self.session.rollback()
        self.session.close()
        with Session(self._engine) as cleanup:
            cleanup.execute(
                text("TRUNCATE TABLE issues, chats, orders RESTART IDENTITY CASCADE")
            )
            cleanup.commit()

    def save_entity(self, entity):
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def save_entities(self, entities):
        self.session.add_all(entities)
        self.session.commit()
