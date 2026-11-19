import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# the secret configuration specific things
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

def _normalize_db_uri(uri):
    if isinstance(uri, str):
        uri = uri.strip()
    if not uri:
        return None
    # Compatibility: some platforms provide postgres:// which SQLAlchemy 1.3 may not accept
    if uri.startswith("postgres://"):
        uri = "postgresql://" + uri[len("postgres://"):]
    return uri


def _is_durable_db_required():
    # Hosted/platform deployments with ephemeral filesystems must use durable DB.
    hosted_keys = (
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_PROJECT_ID",
        "RAILWAY_SERVICE_ID",
        "DYNO",
        "RENDER",
        "RENDER_SERVICE_ID",
        "KUBERNETES_SERVICE_HOST",
    )
    if any(os.environ.get(k) for k in hosted_keys):
        return True
    # Explicit opt-in for environments that require PostgreSQL.
    val = str(os.environ.get("T3RMX_REQUIRE_POSTGRES", "") or "").strip().lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    return False


def _resolve_db_uri():
    uri = _normalize_db_uri(getattr(Config, "DB_URI", None))
    if uri:
        # Normalize for SQLAlchemy compatibility
        return uri
    if _is_durable_db_required():
        raise RuntimeError(
            "DATABASE_URL is required for this deployment environment. "
            "Configure a PostgreSQL database URL (Railway Postgres reference recommended). "
            "Ephemeral SQLite fallback is disabled to prevent data loss."
        )
    # Safe local fallback for local/non-hosted development when no DB is configured
    return "sqlite:///t3rmx.db"


BASE = declarative_base()
# Keep a stable session object so `from . import SESSION` bindings remain valid
SESSION = scoped_session(sessionmaker())


def start() -> scoped_session:
    uri = _resolve_db_uri()
    try:
        engine = create_engine(uri)
    except Exception as e:
        if _is_durable_db_required():
            LOGS.error(f"Database engine init failed for configured URI: {e}")
            raise
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
    if _is_durable_db_required():
        LOGS.error("Database initialization failed in a durable-DB-required environment; aborting startup.")
        raise
    LOGS.error(
        "Database initialization failed. Features depending on the database may not work."
    )
    LOGS.exception(e)

