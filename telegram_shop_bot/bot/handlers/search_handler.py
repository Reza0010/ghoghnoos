import math
from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext, ConversationHandler, MessageHandler,
    Filters, CallbackQueryHandler
)
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud
from telegram_shop_bot.bot import keyboards

SEARCH_QUERY, APPLY_FILTER = range(2)
PRODUCTS_PER_PAGE = 6

async def start_search(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("لطفاً نام محصول یا برند مورد نظر خود را وارد کنید:")
    return SEARCH_QUERY

async def handle_search_query(update: Update, context: CallbackContext) -> int:
    query = update.message.text
    if not query or len(query) < 2:
        await update.message.reply_text("متن جستجو باید حداقل ۲ حرف باشد. لطفاً دوباره تلاش کنید:")
        return SEARCH_QUERY
    context.user_data['search_query'] = query
    kbd = keyboards.get_search_filter_keyboard(query)
    await update.message.reply_text(f"نتایج جستجو برای: '{query}'\nمرتب‌سازی بر اساس:", reply_markup=kbd)
    return APPLY_FILTER

async def show_search_results(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(':')
    user_query, sort, page = parts[2], parts[3], int(parts[4]) if len(parts) > 4 else 1
    with next(get_db()) as db:
        prods, total = crud.search_products(db, query=user_query, page=page, page_size=PRODUCTS_PER_PAGE, sort_by=sort)
    total_pages = math.ceil(total / PRODUCTS_PER_PAGE)
    kbd = keyboards.build_search_results_keyboard(prods, user_query, sort, page, total_pages)
    msg = f"نتایج جستجو برای: '{user_query}' (صفحه {page}/{total_pages})" if prods else f"هیچ محصولی برای '{user_query}' یافت نشد."
    await query.edit_message_text(msg, reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)
    return APPLY_FILTER

async def cancel_search(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("جستجو لغو شد.")
    return ConversationHandler.END

search_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_search, pattern='^search:start$')],
    states={
        SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, handle_search_query)],
        APPLY_FILTER: [
            CallbackQueryHandler(show_search_results, pattern='^search:filter:'),
            CallbackQueryHandler(show_search_results, pattern='^search:page:')
        ],
    },
    fallbacks=[MessageHandler(Filters.command, cancel_search)],
)
