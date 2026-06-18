from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# The engine is the core interface to the database
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verifying connection before using
)

# SessionLocal  is a factory for database sessions
# Each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our models
class Base(DeclarativeBase):
   pass

# Dependency
def get_db():
   db = SessionLocal()
   try:
      yield db
   finally:
      db.close()
