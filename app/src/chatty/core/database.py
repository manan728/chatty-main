"""
Database configuration and session management.
"""
import uuid
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from chatty.core.config import settings

# Create SQLAlchemy engine with configuration from settings
config = settings.database_config.copy()
config.pop('url', None)  # Remove url from config since we pass it separately

engine = create_engine(
    settings.database_url,
    **config,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# TODO - Probs best to move to models folder
class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True,  default=lambda: str(uuid.uuid4()))
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated_date = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
