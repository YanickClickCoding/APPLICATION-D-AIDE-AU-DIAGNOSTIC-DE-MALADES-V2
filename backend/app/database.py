"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


def _build_engine_url() -> str | URL:
    """Build engine URL, using DB_NAME to handle database names with special characters."""
    if settings.DB_NAME:
        # Parse host/port/credentials from DATABASE_URL, override database name
        base = settings.DATABASE_URL
        # Extract driver, user, password, host, port from base URL
        # Format: driver://user:password@host:port/...
        from urllib.parse import urlparse
        parsed = urlparse(base)
        return URL.create(
            drivername=parsed.scheme,
            username=parsed.username or "root",
            password=parsed.password or None,
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            database=settings.DB_NAME,
        )
    return settings.DATABASE_URL


# Create database engine
engine = create_engine(
    _build_engine_url(),
    pool_pre_ping=True,
    pool_size=20,        # connexions persistantes dans le pool
    max_overflow=40,     # connexions temporaires supplémentaires
    pool_recycle=3600,   # recycle les connexions après 1h (évite les timeouts MySQL)
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
