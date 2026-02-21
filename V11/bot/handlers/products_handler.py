import math
import logging
from pathlib import Path
from typing import List, Optional
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from bot.utils import run_db
from db import crud, models
from bot import keyboards, responses
from config import BASE_DIR

logger = logging.getLogger("ProductsHandler")

# تنظیم تعداد نمایش محصول در هر صفحه
PRODUCTS_PER_PAGE = 6

# ==============================================================================
# توابع کمکی (Navigation Helpers)
# ==============================================================================

async def build_breadcrumb(cat_id: int) -> str:
    """
    ساخت نوار ناوبری متنی به صورت بازگشتی.
    خروجی: 🏠 خانه > دسته اصلی > زیردسته
    """
    path_names = []
    current_id = cat_id

    def get_cat_sync(db, cid):
        return db.query(models.Category).filter_by(id=cid).first()

    while current_id:
        cat = await run_db(get_cat_sync, current_id)
        if cat:
            path_names.append(cat.name)
            current_id = cat.parent_id
        else:
            break
            
    path_names.reverse()
    breadcrumb = "🏠 <b>خانه</b>"
    if path_names:
        breadcrumb += " > " + " > ".join(f"<b>{n}</b>" for n in path_names)
    return breadcrumb

# ==============================================================================
# مدیریت دسته‌بندی‌ها
# ==============================================================================

async def list_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش لیست دسته‌بندی‌ها (اصلی یا زیرمجموعه) با مدیریت دکمه بازگشت"""
    query = update.callback_query
    await query.answer()
    
    parent_id = None
    data = query.data
    
    # 1. استخراج ID دسته از callback_data
    if ":" in data:
        parts = data.split(':')
        if len(parts) > 2 and parts[2] != 'None':
            parent_id = int(parts[2])

    # 2. مدیریت دکمه بازگشت (پیدا کردن والدِ والد)
    if "cat:back" in data and parent_id:
        def get_parent_sync(db, cid):
            c = db.query(models.Category).filter_by(id=cid).first()
            return c.parent_id if c else None
        parent_id = await run_db(get_parent_sync, parent_id)

    # 3. دریافت لیست دسته‌های مورد نظر
    if parent_id:
        categories = await run_db(crud.get_subcategories, parent_id)
    else:
        categories = await run_db(crud.get_root_categories)

    # 4. اگر این دسته هیچ زیرمجموعه‌ای نداشت، مستقیم لیست محصولاتش را نشان بده
    if not categories and parent_id:
        await render_products_page(update, context, cat_id=parent_id, page=1)
        return

    # 5. رندر نهایی کیبورد دسته‌بندی
    kbd = keyboards.build_category_keyboard(categories, parent_id)
    breadcrumb = await build_breadcrumb(parent_id) if parent_id else "🏠 <b>منوی دسته‌بندی‌ها</b>"
    text = f"{breadcrumb}\n\n{responses.CATEGORY_SELECT}"

    try:
        if query.message.photo:
            # اگر پیام فعلی عکس است، آن را حذف و متن بفرست (برای تمیزی منو)
            await query.message.delete()
            await context.bot.send_message(query.message.chat_id, text, reply_markup=kbd, parse_mode='HTML')
        else:
            await query.edit_message_text(text, reply_markup=kbd, parse_mode='HTML')
    except BadRequest:
        await context.bot.send_message(query.message.chat_id, text, reply_markup=kbd, parse_mode='HTML')

# ==============================================================================
# مدیریت لیست محصولات
# ==============================================================================

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """هندلر دکمه‌های صفحه‌بندی محصولات"""
    query = update.callback_query
    if query.data == "noop":
        await query.answer()
        return

    await query.answer()
    parts = query.data.split(':')
    cat_id = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 1
    
    await render_products_page(update, context, cat_id, page)

async def render_products_page(update: Update, context: ContextTypes.DEFAULT_TYPE, cat_id: int, page: int):
    """تابع مرکزی برای نمایش لیست محصولات یک دسته خاص"""
    query = update.callback_query
    
    # دریافت محصولات فعال دسته
    all_prods = await run_db(crud.get_active_products_by_category, cat_id)

    total_pages = max(1, math.ceil(len(all_prods) / PRODUCTS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * PRODUCTS_PER_PAGE
    prods = all_prods[start : start + PRODUCTS_PER_PAGE]

    breadcrumb = await build_breadcrumb(cat_id)
    kbd = keyboards.build_product_keyboard(prods, cat_id, page, total_pages)
    
    try:
        text = responses.PRODUCT_LIST.format(breadcrumbs=breadcrumb)
    except:
        text = f"{breadcrumb}\n\n📋 <b>لیست محصولات:</b>"

    if not prods:
        text += "\n\n❌ در این دسته هنوز محصولی ثبت نشده است."

    try:
        if query.message.photo:
            await query.message.delete()
            await context.bot.send_message(query.message.chat_id, text, reply_markup=kbd, parse_mode='HTML')
        else:
            await query.edit_message_text(text, reply_markup=kbd, parse_mode='HTML')
    except BadRequest:
        await context.bot.send_message(query.message.chat_id, text, reply_markup=kbd, parse_mode='HTML')

# ==============================================================================
# نمایش جزئیات محصول (Product Details)
# ==============================================================================

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش صفحه اختصاصی محصول شامل عکس، قیمت و دکمه خرید"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # مدیریت ورود از طریق کلیک یا لینک مستقیم (Deep Linking)
    if query:
        await query.answer()
        prod_id = int(query.data.split(':')[2])
        msg_obj = query.message
    else:
        # برای لینک هایی مثل t.me/bot?start=p_123
        try:
            prod_id = int(context.args[0].replace('p_', ''))
            msg_obj = update.message
        except: return

    # دریافت محصول با تمام متعلقات (Images, Variants)
    prod = await run_db(crud.get_product, prod_id)
    if not prod:
        await msg_obj.reply_text("❌ متاسفانه محصول یافت نشد یا حذف شده است.")
        return

    # دریافت وضعیت کاربر نسبت به محصول
    cart_items = await run_db(crud.get_cart_items, user_id)
    favs = await run_db(crud.get_user_favorites, user_id)
    is_fav = any(f.id == prod.id for f in favs)
    
    this_item = next((i for i in cart_items if i.product_id == prod.id), None)
    cart_qty = this_item.quantity if this_item else 0

    # آماده‌سازی متن قیمت (تخفیف هوشمند)
    is_disc = crud.is_product_discount_active(prod)
    final_price = prod.discount_price if is_disc else prod.price
    price_text = responses.format_price(final_price)
    if is_disc:
        price_text = f"<s>{responses.format_price(prod.price)}</s> ➡️ {price_text} 🔥"

    # ساخت متن نهایی
    text = responses.PRODUCT_DETAILS.format(
        name=prod.name,
        divider=responses.get_divider(),
        description=prod.description or "توضیحات ندارد.",
        brand=prod.brand or "متفرقه",
        stock_status="✅ موجود در انبار" if prod.stock > 0 else "❌ ناموجود",
        price_formatted=price_text,
        cart_preview=f"\n🛒 در سبد خرید شما: <b>{cart_qty} عدد</b>" if cart_qty > 0 else ""
    )

    # افزودن فوتر برندینگ
    from bot.utils import get_branded_text
    text = await get_branded_text(text)

    bot_info = await context.bot.get_me()
    kbd = keyboards.get_product_detail_keyboard(prod, is_fav, cart_qty, bot_info.username)

    # --- منطق ارسال آلبوم تصاویر (Media Group) ---
    media_list = []
    
    # جمع‌آوری تمام تصاویر محصول
    images = prod.images if prod.images else []
    if not images and hasattr(prod, 'image_path') and prod.image_path:
        # اگر در گالری نبود ولی در ستون قدیمی بود
        images = [models.ProductImage(image_path=prod.image_path, image_file_id=prod.image_file_id)]

    for idx, img in enumerate(images):
        media_item = None
        if img.image_file_id:
            media_item = img.image_file_id
        else:
            full_path = Path(BASE_DIR) / img.image_path
            if full_path.exists():
                media_item = open(full_path, 'rb')

        if media_item:
            # فقط اولین تصویر کپشن داشته باشد (استاندارد تلگرام برای آلبوم)
            caption = text if idx == 0 else ""
            media_list.append(InputMediaPhoto(media=media_item, caption=caption, parse_mode='HTML'))

    try:
        if len(media_list) > 1:
            # ارسال به صورت آلبوم (Media Group)
            # نکته: مدیاگروپ را نمی‌توان روی پیام قبلی Edit کرد، پس پیام قبلی حذف و جدید فرستاده می‌شود
            if query: await msg_obj.delete()

            sent_messages = await context.bot.send_media_group(chat_id=msg_obj.chat_id, media=media_list)
            # ارسال کیبورد زیر آلبوم (با یک پیام متنی کوچک)
            await context.bot.send_message(
                chat_id=msg_obj.chat_id,
                text="👆 <b>تصاویر محصول را مشاهده کنید.</b>\nبرای خرید یا اطلاعات بیشتر از دکمه‌های زیر استفاده کنید:",
                reply_markup=kbd,
                parse_mode='HTML'
            )

            # کش کردن File IDها برای دفعات بعد
            def cache_ids(db, pid, m_list):
                p_obj = db.query(models.Product).get(pid)
                for i, sent_m in enumerate(m_list):
                    if i < len(p_obj.images):
                        p_obj.images[i].image_file_id = sent_m.photo[-1].file_id
                    elif i == 0:
                        p_obj.image_file_id = sent_m.photo[-1].file_id
                db.commit()

            asyncio.create_task(run_db(cache_ids, prod.id, sent_messages))

        elif len(media_list) == 1:
            # تک تصویر (ارسال سریع‌تر و زیباتر با قابلیت ادیت)
            if msg_obj.photo:
                await msg_obj.edit_media(media=media_list[0], reply_markup=kbd)
            else:
                if query: await msg_obj.delete()
                sent = await context.bot.send_photo(
                    chat_id=msg_obj.chat_id,
                    photo=media_list[0].media,
                    caption=text,
                    reply_markup=kbd,
                    parse_mode='HTML'
                )
                # کش کردن File ID
                if not images[0].image_file_id:
                    def save_fid(db, pid, fid):
                        p = db.query(models.Product).get(pid)
                        if p.images: p.images[0].image_file_id = fid
                        p.image_file_id = fid
                        db.commit()
                    asyncio.create_task(run_db(save_fid, prod.id, sent.photo[-1].file_id))
        else:
            # بدون تصویر
            if query: await msg_obj.edit_text(text, reply_markup=kbd, parse_mode='HTML')
            else: await msg_obj.reply_text(text, reply_markup=kbd, parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Error in show_product_details: {e}")
        await msg_obj.reply_text(text, reply_markup=kbd, parse_mode='HTML')

# ==============================================================================
# تعاملات کاربر (Favorite, Notify, Variants)
# ==============================================================================

async def toggle_favorite_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """افزودن یا حذف از لیست علاقه‌مندی‌ها"""
    query = update.callback_query
    prod_id = int(query.data.split(':')[2])
    is_added = await run_db(crud.toggle_favorite, update.effective_user.id, prod_id)
    
    msg = responses.FAV_ADDED if is_added else responses.FAV_REMOVED
    await query.answer(msg)
    
    # رفرش صفحه برای آپدیت شدن آیکون دکمه
    await show_product_details(update, context)

async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست علاقه‌مندی‌های کاربر"""
    query = update.callback_query
    await query.answer()
    
    favs = await run_db(crud.get_user_favorites, update.effective_user.id)
    if not favs:
        await query.edit_message_text(responses.FAV_EMPTY, reply_markup=keyboards.get_main_menu_keyboard(), parse_mode='HTML')
        return

    btns = [[InlineKeyboardButton(f"❤️ {p.name}", callback_data=f"prod:show:{p.id}")] for p in favs]
    btns.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data="user_profile")])
    
    await query.edit_message_text("❤️ <b>محصولات مورد علاقه شما:</b>", reply_markup=InlineKeyboardMarkup(btns), parse_mode='HTML')

async def notify_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ثبت درخواست اطلاع‌رسانی برای محصول ناموجود"""
    query = update.callback_query
    prod_id = int(query.data.split(':')[1])
    await run_db(crud.add_product_notification, update.effective_user.id, prod_id)
    await query.answer(responses.NOTIFY_SUCCESS, show_alert=True)

async def start_attribute_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی انتخاب متغیر (مثلاً رنگ یا سایز) پیش از افزودن به سبد"""
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.split(':')[2])
    
    prod = await run_db(crud.get_product, prod_id)
    if not prod or not prod.variants:
        # اگر متغیر نداشت، مستقیماً اضافه کن
        await run_db(crud.add_to_cart, query.from_user.id, prod_id, 1)
        await show_product_details(update, context)
        return

    btns = []
    for v in prod.variants:
        if v.stock > 0:
            adj = f" ({int(v.price_adjustment):+,} ت)" if v.price_adjustment != 0 else ""
            btns.append([InlineKeyboardButton(f"🔹 {v.name}{adj}", callback_data=f"attr:sel:{prod.id}:{v.id}")])
    
    btns.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data=f"prod:show:{prod.id}")])
    
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))

async def confirm_attribute_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ثبت محصول با متغیر انتخاب شده در سبد خرید"""
    query = update.callback_query
    parts = query.data.split(':')
    prod_id, variant_id = int(parts[2]), int(parts[3])
    
    def get_v_sync(db, vid): return db.query(models.ProductVariant).get(vid)
    variant = await run_db(get_v_sync, variant_id)
    
    if variant:
        try:
            # ذخیره نام متغیر در فیلد attributes سبد خرید
            await run_db(crud.add_to_cart, query.from_user.id, prod_id, 1, attributes=variant.name)
            await query.answer(f"✅ {variant.name} به سبد خرید اضافه شد.")
            await show_product_details(update, context)
        except ValueError as e:
            await query.answer(str(e), show_alert=True)