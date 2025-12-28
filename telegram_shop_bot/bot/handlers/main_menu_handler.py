from telegram import Update
from telegram.ext import ContextTypes
from telegram_shop_bot.bot import responses, keyboards

async def handle_special_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Special Offers' button."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=responses.SPECIAL_OFFERS_TEXT,
        reply_markup=keyboards.back_to_main_menu_keyboard()
    )

async def handle_track_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Track Order' button."""
    query = update.callback_query
    await query.answer()
    # In a real scenario, this would start a conversation to get the order ID.
    await query.edit_message_text(
        text=responses.TRACK_ORDER_TEXT,
        reply_markup=keyboards.back_to_main_menu_keyboard()
    )

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Support' button."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=responses.SUPPORT_TEXT,
        reply_markup=keyboards.back_to_main_menu_keyboard()
    )

async def handle_about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'About Us' button."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=responses.ABOUT_US_TEXT,
        reply_markup=keyboards.back_to_main_menu_keyboard()
    )
