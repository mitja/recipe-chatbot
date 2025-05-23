import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Changed from sqlalchemy.orm

# Default to a local SQLite DB. The actual path might need adjustment
# if the app runs from a different working directory (e.g., in Docker).
# For Docker, an absolute path like /app/app_data.db might be more robust if mapped to a volume.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app_data.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
