from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db import models
from . import responses

# ==============================================================================
# تابع کمکی (Helper Function) برای چیدمان گرید
# ==============================================================================
def _build_grid(buttons: List[InlineKeyboardButton], n_cols: int) -> List[List[InlineKeyboardButton]]:
    """تبدیل یک لیست تخت از دکمه‌ها به یک ساختار چند ستونه (Grid) تمیز."""
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

# ==============================================================================
# بخش ۱: منوی اصلی (Main Menu)
# ==============================================================================
def get_main_menu_keyboard(channel_url: Optional[str] = None) -> InlineKeyboardMarkup:
    """
    منوی شبکه‌ای مدرن و کاربرپسند
    """
    keyboard = [
        # ردیف اول: دکمه اصلی (بزرگ)
        [InlineKeyboardButton(f"🛍 {responses.PRODUCTS_BUTTON.replace('🛍 ', '')}", callback_data="products")],
        
        # ردیف دوم: جستجو و پیشنهادات
        [
            InlineKeyboardButton(f"🔍 {responses.SEARCH_BUTTON.replace('🔍 ', '')}", callback_data="search:start"),
            InlineKeyboardButton(f"🔥 {responses.SPECIAL_OFFERS_BUTTON.replace('🔥 ', '')}", callback_data="special_offers")
        ],
        
        # ردیف سوم: دسترسی‌های سریع کاربر
        [
            InlineKeyboardButton("🛒 سبد خرید", callback_data="cart:view"),
            InlineKeyboardButton("📦 پیگیری", callback_data="track_order"),
            InlineKeyboardButton("👤 حساب من", callback_data="user_profile")
        ],
        
        # ردیف چهارم: اطلاعات و تماس
        [
            InlineKeyboardButton(responses.SUPPORT_BUTTON, callback_data="support"),
            InlineKeyboardButton(responses.ABOUT_US_BUTTON, callback_data="about_us")
        ]
    ]
    
    if channel_url and channel_url.startswith("http"):
        keyboard.append([InlineKeyboardButton("📢 عضویت در کانال تخفیف‌ها", url=channel_url)])
        
    return InlineKeyboardMarkup(keyboard)

# ==============================================================================
# بخش ۲: محصولات و دسته‌بندی‌ها (Products & Categories)
# ==============================================================================
def build_category_keyboard(categories: List[models.Category], current_cat_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """کیبورد انتخاب دسته‌بندی با پشتیبانی از زیرمجموعه و بازگشت هوشمند."""
    buttons = [InlineKeyboardButton(cat.name, callback_data=f"cat:list:{cat.id}") for cat in categories]
    keyboard = _build_grid(buttons, 2)

    # مدیریت دکمه بازگشت (اگر در ریشه نیستیم، به والد برگرد)
    back_cb = f"cat:back:{current_cat_id}" if current_cat_id else "main_menu"
    keyboard.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data=back_cb)])
    
    return InlineKeyboardMarkup(keyboard)

def build_product_keyboard(products: List[models.Product], cat_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """لیست محصولات با نمایش قیمت و صفحه‌بندی هوشمند."""
    keyboard = []
    for p in products:
        # انتخاب قیمت (اگر تخفیف داشت، قیمت تخفیفی نمایش داده شود)
        price = p.discount_price if (p.discount_price and p.discount_price > 0) else p.price
        price_str = f"{int(price):,}"
        keyboard.append([InlineKeyboardButton(f"📦 {p.name} | {price_str} ت", callback_data=f"prod:show:{p.id}")])

    # کنترلر صفحه‌بندی
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"prod:list:{cat_id}:{page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
        
        if page < total_pages:
            nav_row.append(InlineKeyboardButton("بعدی ▶️", callback_data=f"prod:list:{cat_id}:{page+1}"))
        keyboard.append(nav_row)

    # دکمه‌های ناوبری اضافه
    keyboard.append([
        InlineKeyboardButton("🔍 جستجو", callback_data="search:start"),
        InlineKeyboardButton(responses.BACK_BUTTON, callback_data=f"cat:list:{cat_id}")
    ])
    return InlineKeyboardMarkup(keyboard)

def get_product_detail_keyboard(product: models.Product, is_favorite: bool, cart_qty: int, bot_username: str) -> InlineKeyboardMarkup:
    """کیبورد صفحه جزئیات محصول با مدیریت موجودی و متغیرها."""
    keyboard = []
    
    # 1. بخش خرید یا اطلاع‌رسانی
    if product.stock > 0:
        label = f"🛒 خرید سریع ({cart_qty} عدد)" if cart_qty > 0 else "🛒 افزودن به سبد خرید"
        # اگر محصول متغیر (رنگ/سایز) داشته باشد، ابتدا باید انتخاب کند
        if product.variants:
            cb_data = f"attr:start:{product.id}"
        else:
            cb_data = f"cart:add:{product.id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=cb_data)])
    else:
        keyboard.append([InlineKeyboardButton("🔔 موجود شد خبرم کن", callback_data=f"notify:{product.id}")])

    # 2. دکمه‌های تعاملی (علاقه‌مندی و اشتراک)
    fav_text = "❤️ حذف از موردعلاقه" if is_favorite else "🤍 افزودن به موردعلاقه"
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=p_{product.id}"
    
    keyboard.append([
        InlineKeyboardButton(fav_text, callback_data=f"fav:toggle:{product.id}"),
        InlineKeyboardButton("🛒 مشاهده سبد", callback_data="cart:view")
    ])

    keyboard.append([
        InlineKeyboardButton("🔗 اشتراک‌گذاری", url=share_url),
        InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
    ])

    # 3. دکمه بازگشت
    back_cb = f"prod:list:{product.category_id}:1" if product.category_id else "products"
    keyboard.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data=back_cb)])
    
    return InlineKeyboardMarkup(keyboard)

# ==============================================================================
# بخش ۳: سبد خرید و مراحل نهایی (Shopping Cart & Checkout)
# ==============================================================================
def view_cart_keyboard(items: List[models.CartItem]) -> InlineKeyboardMarkup:
    """مدیریت سبد خرید با کنترلر تعداد برای هر آیتم."""
    keyboard = []
    for item in items:
        # نام محصول (نمایش در دکمه غیرفعال برای زیبایی)
        display_name = item.product.name
        if item.selected_attributes:
            display_name += f" ({item.selected_attributes})"
            
        keyboard.append([InlineKeyboardButton(f"🔸 {display_name}", callback_data=f"prod:show:{item.product_id}")])
        
        # کنترلر تعداد (- عدد +)
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"cart:update:{item.product_id}:-1"),
            InlineKeyboardButton(f"{item.quantity} عدد", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"cart:update:{item.product_id}:1"),
        ])
    
    if items:
        keyboard.append([
            InlineKeyboardButton("🗑 خالی کردن سبد", callback_data="cart:clear"),
            InlineKeyboardButton("✅ نهایی‌سازی خرید", callback_data="cart:checkout")
        ])
        
    keyboard.append([InlineKeyboardButton(responses.MAIN_MENU_BUTTON, callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_address_book_keyboard(addresses: List[models.UserAddress], is_checkout: bool = True) -> InlineKeyboardMarkup:
    """لیست آدرس‌های ذخیره شده برای انتخاب سریع یا مدیریت."""
    keyboard = []
    for addr in addresses:
        # نمایش خلاصه آدرس
        short_addr = addr.address_text[:25] + "..." if len(addr.address_text) > 25 else addr.address_text
        cb_action = f"use_addr:{addr.id}" if is_checkout else "noop"
        
        row = [InlineKeyboardButton(f"📍 {addr.title}: {short_addr}", callback_data=cb_action)]
        
        if not is_checkout:
            row.append(InlineKeyboardButton("❌ حذف", callback_data=f"addr_del:{addr.id}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("➕ ثبت آدرس جدید", callback_data="new_address")])
    
    back_to = "cart:view" if is_checkout else "user_profile"
    keyboard.append([InlineKeyboardButton(responses.BACK_BUTTON, callback_data=back_to)])
    
    return InlineKeyboardMarkup(keyboard)

# ==============================================================================
# بخش ۴: پروفایل و تاریخچه (User Profile)
# ==============================================================================
def get_user_profile_keyboard() -> InlineKeyboardMarkup:
    """منوی اصلی حساب کاربری."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 تاریخچه سفارشات من", callback_data="order_history")],
        [
            InlineKeyboardButton("📍 دفترچه آدرس", callback_data="user_addresses"),
            InlineKeyboardButton("💎 زیرمجموعه‌گیری", callback_data="user_referral")
        ],
        [InlineKeyboardButton(responses.MAIN_MENU_BUTTON, callback_data="main_menu")]
    ])

def get_order_history_keyboard() -> InlineKeyboardMarkup:
    """دکمه بازگشت از لیست سفارشات."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="user_profile")]
    ])

# ==============================================================================
# بخش ۵: جستجو و فیلتر (Search & Filter)
# ==============================================================================
def get_search_filter_keyboard(query: str) -> InlineKeyboardMarkup:
    """انتخاب نوع مرتب‌سازی نتایج جستجو."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 ارزان‌ترین", callback_data=f"search:filter:{query}:price_asc"),
            InlineKeyboardButton("💎 گران‌ترین", callback_data=f"search:filter:{query}:price_desc")
        ],
        [
            InlineKeyboardButton("🆕 جدیدترین", callback_data=f"search:filter:{query}:newest"),
            InlineKeyboardButton("🔥 پرفروش‌ترین", callback_data=f"search:filter:{query}:top_seller")
        ],
        [InlineKeyboardButton("🔙 انصراف", callback_data="main_menu")]
    ])

def build_search_results_keyboard(products: List[models.Product], query: str, sort_by: str, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """نمایش نتایج جستجو با صفحه‌بندی اختصاصی."""
    keyboard = []
    for p in products:
        price = p.discount_price if (p.discount_price and p.discount_price > 0) else p.price
        keyboard.append([InlineKeyboardButton(f"{p.name} | {int(price):,} ت", callback_data=f"prod:show:{p.id}")])
    
    if total_pages > 1:
        nav = []
        if current_page > 1:
            nav.append(InlineKeyboardButton("◀️", callback_data=f"search:page:{query}:{sort_by}:{current_page-1}"))
        nav.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        if current_page < total_pages:
            nav.append(InlineKeyboardButton("▶️", callback_data=f"search:page:{query}:{sort_by}:{current_page+1}"))
        keyboard.append(nav)
        
    keyboard.append([InlineKeyboardButton("🔍 جستجوی مجدد", callback_data="search:start")])
    keyboard.append([InlineKeyboardButton(responses.MAIN_MENU_BUTTON, callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

# ==============================================================================
# بخش ۶: ادمین و سایر (Admin & Misc)
# ==============================================================================
def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """درخواست شماره موبایل به صورت دکمه Reply."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 اشتراک‌گذاری شماره موبایل", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_payment_method_keyboard(zarinpal_enabled: bool = False) -> InlineKeyboardMarkup:
    """انتخاب روش پرداخت."""
    btns = []
    if zarinpal_enabled:
        btns.append([InlineKeyboardButton("💳 پرداخت آنلاین (زرین‌پال)", callback_data="pay_online")])

    btns.append([InlineKeyboardButton("🧾 ارسال فیش واریزی (کارت به کارت)", callback_data="pay_receipt")])
    btns.append([InlineKeyboardButton("🔙 انصراف", callback_data="main_menu")])
    return InlineKeyboardMarkup(btns)

def get_admin_order_keyboard(order_id: int, user_id: int) -> InlineKeyboardMarkup:
    """پنل مدیریت سفارش که به پی‌وی ادمین ارسال می‌شود."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تایید نهایی", callback_data=f"adm_approve:{order_id}"),
            InlineKeyboardButton("❌ رد سفارش", callback_data=f"adm_reject:{order_id}")
        ],
        [InlineKeyboardButton("🚚 ثبت کد رهگیری پستی", callback_data=f"adm_ship:{order_id}")],
        [InlineKeyboardButton("👤 پیام به مشتری", url=f"tg://user?id={user_id}")]
    ])