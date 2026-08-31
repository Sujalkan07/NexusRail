from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

FALLBACK_SQLITE_URL = "sqlite:///./nexusrail.db"


def _build_engine(database_url: str):
    connect_args = {}
    engine_kwargs = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        engine_kwargs = {"pool_pre_ping": True, "future": True}
        return create_engine(database_url, connect_args=connect_args, **engine_kwargs)

    if database_url.startswith("postgresql"):
        connect_args = {"connect_timeout": 3}
        engine = create_engine(database_url, connect_args=connect_args, **engine_kwargs)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except (OperationalError, Exception):
            engine.dispose()
            fallback_engine = create_engine(
                FALLBACK_SQLITE_URL,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
                future=True,
            )
            return fallback_engine

    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)


engine = _build_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
