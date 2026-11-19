import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# the secret configuration specific things
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

def _resolve_db_uri():
    uri = getattr(Config, "DB_URI", None)
    if isinstance(uri, str):
        uri = uri.strip()
    if not uri:
        # Safe local fallback when DATABASE_URL/DB_URI is not provided
        return "sqlite:///t3rmx.db"
    # Compatibility: some platforms provide postgres:// which SQLAlchemy 1.3 may not accept
    if uri.startswith("postgres://"):
        uri = "postgresql://" + uri[len("postgres://"):]
    return uri


BASE = declarative_base()
# Keep a stable session object so `from . import SESSION` bindings remain valid
SESSION = scoped_session(sessionmaker())


def start() -> scoped_session:
    uri = _resolve_db_uri()
    try:
        engine = create_engine(uri)
    except Exception as e:
        LOGS.error(
            f"Database engine init failed for configured URI, falling back to local SQLite: {e}"
        )
        engine = create_engine("sqlite:///t3rmx.db")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    SESSION.remove()
    SESSION.configure(bind=engine, autoflush=False)
    return SESSION


try:
    start()
except Exception as e:
    LOGS.error(
        "Database initialization failed. Features depending on the database may not work."
    )
    LOGS.exception(e)

