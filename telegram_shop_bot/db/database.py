import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from .models import Base

# --- Logger ---
logger = logging.getLogger(__name__)

# --- Database Engine ---
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# --- Session Factory ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database by creating all tables.
    """
    try:
        logger.info("Initializing database and creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}", exc_info=True)
        raise

def get_db():
    """
    Generator function that yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
