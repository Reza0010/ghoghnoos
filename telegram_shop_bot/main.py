import logging
import sys
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Ensure the project root is in the Python path
if '.' not in sys.path:
    sys.path.append('.')

from telegram_shop_bot.config import TELEGRAM_BOT_TOKEN
from telegram_shop_bot.db.database import init_db
from telegram_shop_bot.bot.handlers import (
    start, products_handler, search_handler, cart_handler, main_menu_handler
)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class BotApp:
    """
    A class to encapsulate the Telegram bot application, its setup, and execution.
    """
    def __init__(self, run_bot=True):
        """
        Initializes the BotApp.

        Args:
            run_bot (bool): If True, creates the full PTB Application.
                            Set to False for environments where you only need
                            access to other components (like DB).
        """
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not found in config.")

        self.application = None
        if run_bot:
            self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            self._setup_handlers()

    def _setup_handlers(self):
        """Sets up all the handlers for the bot."""
        if not self.application:
            return

        # Core handlers
        self.application.add_handler(CommandHandler("start", start.start))
        self.application.add_handler(CallbackQueryHandler(start.start, pattern=r"^main_menu$"))

        # Conversation handlers
        self.application.add_handler(search_handler.search_conversation_handler)
        self.application.add_handler(cart_handler.checkout_conversation_handler)

        # Main menu handlers
        self.application.add_handler(CallbackQueryHandler(products_handler.list_categories, pattern=r"^products$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler.handle_special_offers, pattern=r"^special_offers$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler.handle_track_order, pattern=r"^track_order$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler.handle_support, pattern=r"^support$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler.handle_about_us, pattern=r"^about_us$"))

        # Product and category navigation
        self.application.add_handler(CallbackQueryHandler(products_handler.list_categories, pattern=r"^cat:list:"))
        self.application.add_handler(CallbackQueryHandler(products_handler.list_products, pattern=r"^cat:show:"))
        self.application.add_handler(CallbackQueryHandler(products_handler.list_products, pattern=r"^prod:list:"))
        self.application.add_handler(CallbackQueryHandler(products_handler.show_product_details, pattern=r"^prod:show:"))

        # Cart handlers
        self.application.add_handler(CallbackQueryHandler(cart_handler.view_cart, pattern=r"^cart:view$"))
        self.application.add_handler(CallbackQueryHandler(cart_handler.add_to_cart_handler, pattern=r"^cart:add:"))
        self.application.add_handler(CallbackQueryHandler(cart_handler.update_cart_item_handler, pattern=r"^cart:update:"))
        self.application.add_handler(CallbackQueryHandler(cart_handler.clear_cart_handler, pattern=r"^cart:clear$"))

    @property
    def bot(self):
        """Provides direct access to the bot instance."""
        return self.application.bot if self.application else None

    async def run(self):
        """Initializes and runs the bot application."""
        if not self.application:
            logger.error("Application not initialized. Cannot run.")
            return

        logger.info("Starting bot...")
        async with self.application:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Bot is running.")
            # Keep the bot running indefinitely
            await asyncio.Event().wait()

async def main():
    """Main entry point to run the bot."""
    init_db()  # Ensure the database is initialized
    bot_app = BotApp()
    await bot_app.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}", exc_info=True)
