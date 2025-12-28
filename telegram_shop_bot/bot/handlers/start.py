from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud
from telegram_shop_bot.bot import responses, keyboards

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user: return

    with next(get_db()) as db:
        crud.get_or_create_user(db, user_id=user.id, full_name=user.full_name or "کاربر")
        shop_name = crud.get_setting(db, "shop_name", "فروشگاه شما")

    text = responses.WELCOME_MESSAGE.format(shop_name=shop_name, user_name=user.first_name)
    kbd = keyboards.get_main_menu_keyboard()

    if update.message:
        await update.message.reply_text(text, reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)
