import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram_shop_bot.config import DATABASE_URL
from .models import Base

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        logger.info("Initializing database and creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}", exc_info=True)
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
