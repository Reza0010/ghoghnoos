import os
import logging
from dotenv import load_dotenv

# --- Basic Logging Setup ---
# Configure logger to be used before the main app logger is configured
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Path Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')

# --- Load Environment Variables ---
if not os.path.exists(ENV_PATH):
    logger.warning(
        f".env file not found at {ENV_PATH}. "
        "Please create it based on .env.example."
    )
load_dotenv(dotenv_path=ENV_PATH)

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise ValueError(
        "Telegram bot token is not set or is set to the default placeholder. "
        "Please check your .env file."
    )

# --- Admin Configuration ---
ADMIN_USER_IDS_STR = os.getenv("ADMIN_USER_IDS", "")
ADMIN_USER_IDS = [
    int(admin_id.strip()) for admin_id in ADMIN_USER_IDS_STR.split(',') if admin_id.strip()
]
if not ADMIN_USER_IDS:
    logger.warning(
        "ADMIN_USER_IDS is not set in the .env file. "
        "No users will have admin privileges."
    )

# --- Database Configuration ---
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'shop_bot.db')}"
