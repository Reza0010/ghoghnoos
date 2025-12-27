import logging
import sys
from telegram.ext import Application, CommandHandler

# --- Adjust Python Path ---
# This is a common pattern to make sure the script can find local modules
# irrespective of the directory from which it's run.
sys.path.append('.')

# --- Local Imports ---
from config import TELEGRAM_BOT_TOKEN
from db.database import init_db
from bot.handlers.start import start as start_handler

# --- Logging Configuration ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout) # Log to console
    ]
)
# Reduce httpx logging noise
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    The main function to initialize and run the Telegram bot.
    """
    logger.info("Initializing database...")
    init_db()

    logger.info("Setting up Telegram bot application...")
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not found. Please check your .env file.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- Register Handlers ---
    logger.info("Registering command handlers...")
    application.add_handler(CommandHandler("start", start_handler))
    # Add other handlers (CallbackQueryHandler, MessageHandler, etc.) here in the future

    # --- Start Polling ---
    logger.info("Starting bot polling...")
    application.run_polling()
    logger.info("Bot has stopped.")


if __name__ == "__main__":
    main()
