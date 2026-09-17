"""
Database engine + session factory.

Reads the database URL from app.core.config.settings (which loads
URBANSENSE_DATABASE_URL from .env) so this always stays in sync with the rest
of the app's configuration. Defaults to a local SQLite file so the prototype
runs with zero external services. Switch to a PostgreSQL/PostGIS DSN in
production — no other code changes required (see docs/ARCHITECTURE.md §9).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.models import Base

DATABASE_URL = settings.database_url

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # SQLite's `:memory:` DB is per-connection by default — without a shared
    # StaticPool, every new session would see a *different*, empty database.
    # This matters for the test suite (tests/conftest.py) and for anyone who
    # points DATABASE_URL at :memory: outside of tests.
    engine_kwargs = {"poolclass": StaticPool} if ":memory:" in DATABASE_URL else {}
else:
    connect_args = {}
    engine_kwargs = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables. Called on backend startup for the SIH prototype
    (a real deployment would use Alembic migrations instead)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session per-request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
