import logging
import shutil
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Tuple
from functools import lru_cache
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from config import DATABASE_URL, LOG_DIR, DB_FOLDER

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. ابزارهای کمکی دیتابیس
# ==============================================================================
def ensure_db_directory():
    """اطمینان از وجود پوشه دیتابیس و ایجاد بک‌آپ استارتاپ"""
    if "sqlite" in DATABASE_URL:
        db_path_str = DATABASE_URL.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        if db_path.parent and not db_path.parent.exists():
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.critical(f"Failed to create database directory: {e}")
                raise
        
        # بک‌آپ هوشمند قبل از هر بار اجرا (فقط اگر دیتابیس وجود داشت)
        if db_path.exists() and db_path.stat().st_size > 0:
            backup_dir = db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            # پاکسازی بک‌آپ‌های خیلی قدیمی (نگهداری ۵ تای آخر)
            backups = sorted(backup_dir.glob("startup_*.db"), key=os.path.getmtime)
            while len(backups) >= 5:
                try:
                    os.remove(backups.pop(0))
                except: pass
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                shutil.copy2(db_path, backup_dir / f"startup_{timestamp}.db")
            except Exception as e:
                logger.warning(f"Startup backup failed: {e}")

ensure_db_directory()

# ==============================================================================
# 2. پیکربندی موتور دیتابیس (Concurrency Optimized)
# ==============================================================================
@lru_cache(maxsize=1)
def get_engine():
    """ایجاد موتور دیتابیس با تنظیمات بهینه برای همزمانی"""
    connect_args = {}
    if "sqlite" in DATABASE_URL:
        connect_args = {
            "check_same_thread": False,  # حیاتی: اجازه استفاده در ترد‌های مختلف
            "timeout": 20                # افزایش زمان انتظار برای باز شدن قفل
        }
    
    echo_mode = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
    
    try:
        engine = create_engine(
            DATABASE_URL,
            connect_args=connect_args,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=echo_mode
        )
        return engine
    except Exception as e:
        logger.critical(f"Failed to create engine: {e}")
        raise

engine = get_engine()

# ==============================================================================
# 3. بهینه‌سازی‌های SQLite (WAL Mode)
# ==============================================================================
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        try:
            # WAL Mode: کلید اصلی برای جلوگیری از ارور Database Locked
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            # افزایش حافظه کش برای سرعت بیشتر
            cursor.execute("PRAGMA cache_size=-64000") # 64MB
            cursor.execute("PRAGMA busy_timeout=20000")
        except Exception as e:
            logger.warning(f"SQLite PRAGMA setup warning: {e}")
        finally:
            cursor.close()

# ==============================================================================
# 4. مدیریت نشست‌ها (Session Management)
# ==============================================================================
# استفاده از scoped_session برای Thread-Safety کامل در پنل ادمین
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
SessionLocal = scoped_session(session_factory)

def init_db():
    """ساخت جداول و اجرای مایگریشن‌های خودکار"""
    from .models import Base
    try:
        Base.metadata.create_all(bind=engine)
        run_auto_migrations()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"DB Init Failed: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Dependency برای استفاده در توابع"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Session Error: {e}")
        raise
    finally:
        db.close()
        SessionLocal.remove() # پاکسازی ترد

# ==============================================================================
# 5. سیستم مایگریشن خودکار (Auto Migration)
# ==============================================================================
def run_auto_migrations():
    """بررسی و افزودن ستون‌های جدید به جداول قدیمی"""
    if "sqlite" not in DATABASE_URL:
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    # تعریف تغییرات جدید اسکیما
    schema_updates = {
        "products": {
            "image_file_id": "VARCHAR(255)",
            "related_product_ids": "VARCHAR(255)",
            "tags": "TEXT",
            "is_top_seller": "BOOLEAN DEFAULT 0",
            "image_path": "VARCHAR(512)" # بازگرداندن ستون قدیمی برای سازگاری
        },
        "users": {
            "platform": "VARCHAR(20) DEFAULT 'telegram'",
            "saved_address": "TEXT",
            "saved_phone": "VARCHAR(20)",
            "private_note": "TEXT",
            "is_banned": "BOOLEAN DEFAULT 0"
        },
        "orders": {
            "tracking_code": "VARCHAR(100)",
            "payment_receipt_photo_id": "VARCHAR(255)",
            "postal_code": "VARCHAR(20)"
        }
    }

    with engine.begin() as conn:
        for table, cols in schema_updates.items():
            if table in existing_tables:
                existing_cols = {c["name"] for c in inspector.get_columns(table)}
                for col_name, col_type in cols.items():
                    if col_name not in existing_cols:
                        try:
                            logger.info(f"MIGRATION: Adding '{col_name}' to '{table}'")
                            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
                        except OperationalError:
                            pass # ستون ممکن است وجود داشته باشد