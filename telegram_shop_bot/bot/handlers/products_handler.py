import math
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from telegram_shop_bot.db.database import get_db
from telegram_shop_bot.db import crud
from telegram_shop_bot.bot import keyboards, responses

PRODUCTS_PER_PAGE = 6

async def list_categories(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parent_id = None if query.data.split(':')[2] == 'root' else int(query.data.split(':')[2])
    with next(get_db()) as db:
        categories = crud.get_categories(db, parent_id=parent_id)
    kbd = keyboards.build_category_keyboard(categories, parent_id)
    await query.edit_message_text("لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=kbd)

async def list_products(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(':')
    cat_id = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 1
    with next(get_db()) as db:
        prods = crud.get_products_by_category(db, cat_id=cat_id, page=page, page_size=PRODUCTS_PER_PAGE)
        count = crud.get_product_count_by_category(db, cat_id=cat_id)
        cat = crud.get_category(db, cat_id)
    if not cat:
        await query.edit_message_text(responses.ERROR_MESSAGE)
        return
    total_pages = math.ceil(count / PRODUCTS_PER_PAGE)
    kbd = keyboards.build_product_keyboard(prods, cat_id, page, total_pages)
    await query.edit_message_text(f"محصولات دسته‌بندی: *{cat.name}*", reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)

async def show_product_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split(':')[2])
    with next(get_db()) as db:
        prod = crud.get_product(db, prod_id)
    if not prod:
        await query.edit_message_text(responses.ERROR_MESSAGE)
        return
    text = f"""
*نام محصول:* {prod.name}
*برند:* {prod.brand or 'متفرقه'}
*قیمت:* {prod.price:,.0f} تومان
*موجودی:* {'موجود' if prod.stock > 0 else 'ناموجود'}

*توضیحات:*
{prod.description}
    """
    kbd = keyboards.product_details_keyboard(prod)
    await query.edit_message_text(text, reply_markup=kbd, parse_mode=ParseMode.MARKDOWN)
