import logging
from sqlalchemy.orm import Session
from . import models
from config import ADMIN_USER_IDS

# --- Logger ---
logger = logging.getLogger(__name__)

def get_or_create_user(db: Session, user_id: int, full_name: str) -> models.User:
    """
    Retrieves a user by their Telegram user_id. If the user does not exist,
    it creates a new one. Also, syncs the admin status from the config.
    """
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()

    # Determine admin status from the config file
    is_admin = user_id in ADMIN_USER_IDS

    if not db_user:
        # User does not exist, create a new one
        logger.info(f"Creating new user for ID {user_id} with admin status: {is_admin}")
        db_user = models.User(
            user_id=user_id,
            full_name=full_name,
            is_admin=is_admin,
        )
        db.add(db_user)
    else:
        # User exists, update their details if necessary
        if db_user.full_name != full_name or db_user.is_admin != is_admin:
            logger.info(f"Updating user {user_id}. Name: '{db_user.full_name}' -> '{full_name}'. Admin: {db_user.is_admin} -> {is_admin}")
            db_user.full_name = full_name
            db_user.is_admin = is_admin

    db.commit()
    db.refresh(db_user)
    return db_user
