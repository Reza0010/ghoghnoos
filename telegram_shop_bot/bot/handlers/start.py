from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from db.database import get_db
from db.crud import get_or_create_user
from bot import responses, keyboards

async def start(update: Update, context: CallbackContext) -> None:
    """
    Handles the /start command.

    Greets the user, registers or updates them in the database,
    and displays the main menu.
    """
    user = update.effective_user
    if not user:
        return

    # Using a context manager for the database session
    with next(get_db()) as db:
        get_or_create_user(
            db, user_id=user.id, full_name=user.full_name or "کاربر"
        )

    # Prepare the welcome message
    welcome_text = responses.WELCOME_MESSAGE.format(
        shop_name="دیجی‌تل",  # This could come from a config file
        user_name=user.first_name,
    )

    # Send the welcome message
    if update.message:
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=keyboards.get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
