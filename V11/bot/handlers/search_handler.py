import math
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CommandHandler
)
from telegram.error import BadRequest

from bot.utils import run_db
from db import crud, models
from bot import keyboards, responses

logger = logging.getLogger("SearchHandler")

# وضعیت‌های گفتگو (Conversation States)
SEARCH_QUERY_STATE, APPLY_FILTER_STATE = range(2)

# تنظیمات نمایش
PRODUCTS_PER_PAGE = 6

# ==============================================================================
# تابع کمکی (Helper)
# ==============================================================================
async def _safe_edit(update: Update, text: str, reply_markup: InlineKeyboardMarkup = None):
    """ویرایش یا ارسال پیام جدید بدون خطا"""
    query = update.callback_query
    try:
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.effective_chat.send_message(text, reply_markup=reply_markup, parse_mode='HTML')
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            # اگر پیام قابل ویرایش نبود (مثلاً عکس‌دار بود)، حذف و ارسال جدید
            try: await query.message.delete()
            except: pass
            await update.effective_chat.send_message(text, reply_markup=reply_markup, parse_mode='HTML')

# ==============================================================================
# شروع پروسه جستجو
# ==============================================================================
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """درخواست کلمه کلیدی از کاربر"""
    if update.callback_query:
        await update.callback_query.answer()

    kbd = InlineKeyboardMarkup([[InlineKeyboardButton(responses.BACK_BUTTON, callback_data="main_menu")]])
    await _safe_edit(update, responses.SEARCH_PROMPT, kbd)
    
    return SEARCH_QUERY_STATE

async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت متن و نمایش گزینه‌های فیلتر"""
    query_text = update.message.text.strip()
    
    if len(query_text) < 2:
        await update.message.reply_text("⚠️ کلمه کلیدی بسیار کوتاه است. لطفاً حداقل ۲ حرف وارد کنید:")
        return SEARCH_QUERY_STATE

    # ذخیره کوئری در دیتای کاربر برای مراحل بعد
    context.user_data['search_query'] = query_text

    kbd = keyboards.get_search_filter_keyboard(query_text)
    msg_text = (
        f"{responses.SEARCH_RESULT_TITLE.format(query=query_text)}\n\n"
        f"🔻 <b>نحوه نمایش نتایج را انتخاب کنید:</b>"
    )
    await update.message.reply_text(msg_text, reply_markup=kbd, parse_mode='HTML')

    return APPLY_FILTER_STATE

# ==============================================================================
# نمایش نتایج با فیلتر و صفحه‌بندی
# ==============================================================================
async def show_search_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """واکشی محصولات بر اساس فیلتر و رندر کردن لیست"""
    query = update.callback_query
    await query.answer()
    
    try:
        # استخراج پارامترها از Callback Data
        # الگو: search:filter:QUERY:SORT یا search:page:QUERY:SORT:PAGE
        parts = query.data.split(':')
        action = parts[1]        # filter / page
        search_term = parts[2]
        sort_by = parts[3]
        page = int(parts[4]) if action == "page" and len(parts) > 4 else 1

        # 1. دریافت تعداد کل نتایج (برای محاسبه صفحات)
        total_items = await run_db(crud.get_product_search_count, query=search_term)
        
        total_pages = max(1, math.ceil(total_items / PRODUCTS_PER_PAGE))
        current_page = max(1, min(page, total_pages))
        
        # 2. دریافت محصولات صفحه فعلی
        limit = PRODUCTS_PER_PAGE
        offset = (current_page - 1) * limit
        
        products = await run_db(
            crud.advanced_search_products,
            query=search_term,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )

        # 3. ساخت کیبورد نتایج
        kbd = keyboards.build_search_results_keyboard(
            products=products,
            query=search_term,
            sort_by=sort_by,
            current_page=current_page,
            total_pages=total_pages
        )

        if products:
            msg_text = (
                f"🔎 نتایج جستجو برای: <b>{search_term}</b>\n"
                f"📄 صفحه <b>{current_page}</b> از <b>{total_pages}</b>\n\n"
                f"تعداد کل نتایج: {total_items} کالا"
            )
        else:
            msg_text = responses.SEARCH_NO_RESULT

        await _safe_edit(update, msg_text, kbd)

    except Exception as e:
        logger.error(f"Search Execution Error: {e}")
        await query.message.reply_text("❌ خطایی در انجام جستجو رخ داد.")
        return ConversationHandler.END

    return APPLY_FILTER_STATE

# ==============================================================================
# لغو و بازگشت
# ==============================================================================
async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پاکسازی داده‌ها و بازگشت به منوی اصلی"""
    context.user_data.pop('search_query', None)
    
    kbd = keyboards.get_main_menu_keyboard()
    msg = "🔍 جستجو لغو شد. به منوی اصلی بازگشتید."
    
    await _safe_edit(update, msg, kbd)
    return ConversationHandler.END

# ==============================================================================
# تعریف هندلر نهایی (Router)
# ==============================================================================
search_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_search, pattern=r'^search:start$'),
        CommandHandler("search", start_search),
        MessageHandler(filters.Text(responses.SEARCH_BUTTON), start_search)
    ],
    states={
        SEARCH_QUERY_STATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query)
        ],
        APPLY_FILTER_STATE: [
            # تغییر فیلتر یا جابجایی صفحه
            CallbackQueryHandler(show_search_results, pattern=r'^search:(filter|page):'),
            # شروع مجدد جستجو
            CallbackQueryHandler(start_search, pattern=r'^search:start$')
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_search, pattern=r'^main_menu$'),
        CommandHandler("cancel", cancel_search),
        CommandHandler("start", cancel_search)
    ],
    allow_reentry=True,
    per_chat=True,
    per_user=True,
)