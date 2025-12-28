import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')

if not os.path.exists(ENV_PATH):
    logger.warning(f".env file not found at {ENV_PATH}. Please create it based on .env.example.")
load_dotenv(dotenv_path=ENV_PATH)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise ValueError("Telegram bot token is not set. Please check your .env file.")

ADMIN_USER_IDS_STR = os.getenv("ADMIN_USER_IDS", "")
ADMIN_USER_IDS = [int(admin_id.strip()) for admin_id in ADMIN_USER_IDS_STR.split(',') if admin_id.strip()]
if not ADMIN_USER_IDS:
    logger.warning("ADMIN_USER_IDS is not set. No users will have admin privileges.")

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'shop_bot.db')}"
