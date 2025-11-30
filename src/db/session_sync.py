# src/db/session_sync.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Use NON-ASYNC URL
engine_sync = create_engine(
    settings.database_sync_url,  # must be postgresql:// not asyncpg
    future=True,
)

SessionLocalSync = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_sync,
)
