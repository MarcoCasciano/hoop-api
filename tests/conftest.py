# tests/conftest.py
import os

# Imposta le variabili d'ambiente PRIMA di importare qualsiasi modulo dell'app
os.environ.setdefault("DATABASE_URL", "postgresql://hoop:hoop@localhost:5432/hoop_db")
os.environ.setdefault("TEST_DATABASE_URL", "postgresql://hoop:hoop@localhost:5432/hoop_test_db")

from unittest.mock import patch

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.db.database import get_conn
from app.main import app

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS brews (
    id          BIGSERIAL PRIMARY KEY,
    coffee      TEXT NOT NULL,
    dose        DOUBLE PRECISION NOT NULL,
    ratio       DOUBLE PRECISION NOT NULL,
    water       DOUBLE PRECISION NOT NULL,
    temperature INTEGER NOT NULL DEFAULT 94,
    grind       TEXT NOT NULL DEFAULT 'medium',
    rating      INTEGER NULL,
    notes       TEXT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


@pytest.fixture(scope="session")
def db_session():
    """Connessione al DB di test per l'intera sessione. Crea e distrugge la tabella."""
    conn = psycopg.connect(TEST_DATABASE_URL, row_factory=dict_row)
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
    yield conn
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS brews;")
    conn.commit()
    conn.close()


@pytest.fixture
def client(db_session):
    """TestClient con DB di test iniettato e init_db disabilitato. Pulisce la tabella dopo ogni test."""
    def _override():
        yield db_session

    app.dependency_overrides[get_conn] = _override
    with patch("app.main.init_db"):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
    app.dependency_overrides.clear()

    try:
        with db_session.cursor() as cur:
            cur.execute("TRUNCATE brews RESTART IDENTITY;")
        db_session.commit()
    except Exception:
        db_session.rollback()
