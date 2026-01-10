from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv
from models import User, Task  # Import all models to register them

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./task_management.db")

# For testing with in-memory database, use: sqlite:///:memory:
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session