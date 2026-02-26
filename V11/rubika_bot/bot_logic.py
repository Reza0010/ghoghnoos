import asyncio
import logging
import json
from typing import Optional, Dict, Any, List

# واردات نسبتی به ساختار پروژه
from .rubika_client import RubikaAPI, RubikaError
from bot.utils import run_db
from db.database import SessionLocal
from db import crud, models

logger = logging.getLogger("RubikaBot")

class RubikaWorker:
    def __init__(self, token: str, proxy: str = None):
        self.api = RubikaAPI(token, proxy=proxy)
        self.running = False
        self.bot_guid: Optional[str] = None

    async def _initialize_bot(self):
        """دریافت شناسه ربات و تنظیم دستورات"""
        try:
            res = await self.api.get_me()
            # ساختار پاسخ getMe طبق مستندات: {'bot': {'bot_id': ...}}
            if res and "bot" in res:
                self.bot_guid = res["bot"]["bot_id"]
                logger.info(f"Rubika Bot ID identified: {self.bot_guid}")

            # تنظیم منوی دستورات
            await self.api.set_commands([
                {"command": "start", "description": "🏠 منوی اصلی"},
                {"command": "search", "description": "🔍 جستجوی محصول"},
                {"command": "cart", "description": "🛒 سبد خرید"},
                {"command": "support", "description": "📞 پشتیبانی"}
            ])
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")

    async def start_polling(self):
        """شروع حلقه دریافت پیام‌ها"""
        self.running = True
        await self._initialize_bot()
        logger.info("🚀 Rubika Polling Service Started...")

        while self.running:
            try:
                # دریافت آپدیت‌ها (مدیریت offset داخل کلاینت انجام می‌شود)
                updates = await self.api.get_updates(limit=20)

                if updates:
                    for update in updates:
                        try:
                            await self.process_update(update)
                        except Exception as inner_e:
                            logger.error(f"Error processing update: {inner_e}")

                # وقفه کوتاه برای کاهش فشار سرور
                await asyncio.sleep(1.5)

            except RubikaError as e:
                logger.warning(f"Rubika API Error: {e}. Retrying...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Polling Loop Critical Error: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        self.running = False
        await self.api.close()

    async def process_update(self, update: Dict[str, Any]):
        """توزیع‌کننده رویدادها (Dispatcher)"""
        update_type = update.get("type")

        if update_type == "NewMessage":
            msg = update.get("new_message", {})
            chat_id = update.get("chat_id")
            sender_id = msg.get("sender_id")

            if sender_id == self.bot_guid: return

            # دریافت اطلاعات کاربر برای CRM
            with SessionLocal() as db:
                # تلاش برای دریافت نام کاربر اگر در آپدیت باشد (روبیکا در NewMessage معمولا فقط sender_id را می‌دهد)
                # اما می‌توان از getChat برای تکمیل پروفایل استفاده کرد در صورت لزوم
                crud.get_or_create_user(db, sender_id, "کاربر روبیکا", None, "rubika")

            text = msg.get("text", "")
            aux_data = msg.get("aux_data", {})
            button_id = aux_data.get("button_id")

            if button_id:
                await self.handle_button_click(chat_id, sender_id, button_id, aux_data)
            elif text:
                await self.handle_text_message(chat_id, sender_id, text)

        # ۲. سایر رویدادها (StartedBot, StoppedBot, etc.)
        elif update_type == "StartedBot":
            user_id = update.get("chat_id") # در StartedBot معمولا chat_id همان کاربر است
            # ارسال پیام خوش‌آمدگویی
            await self.send_main_menu(user_id)

    # ================= Handlers =================

    async def handle_text_message(self, chat_id: str, user_id: str, text: str):
        """مدیریت پیام‌های متنی"""
        text = text.strip()

        # ۱. بررسی پاسخگوی خودکار کلمات کلیدی
        auto_reply = await run_db(crud.find_auto_response, text)
        if auto_reply:
            return await self.api.send_message(chat_id, auto_reply)

        if text == "/start" or text == "🏠 بازگشت به منو":
            await self.send_main_menu(chat_id)
        elif text == "🛍 محصولات":
            await self.send_categories(chat_id)
        elif text == "🛒 سبد خرید":
            await self.send_cart(chat_id, user_id)
        elif text == "📞 پشتیبانی":
            await self.send_support_menu(chat_id, user_id)
        elif text == "👤 پروفایل":
            await self.send_user_profile(chat_id, user_id)
        elif text.startswith("/search") or text == "🔍 جستجو":
            q = text.replace("/search", "").strip()
            if not q:
                await self.api.send_message(chat_id, "🔎 لطفا عبارت مورد نظر برای جستجو را وارد کنید:")
            else:
                await self.handle_search(chat_id, q)
        elif text == "💳 شارژ کیف پول":
             await self.api.send_message(chat_id, "بزودی...")
        else:
            # اگر پیام متنی معمولی بود، شاید جستجو باشد یا ثبت تیکت
            if len(text) > 2:
                 await self.handle_support_text(chat_id, user_id, text)

    async def handle_button_click(self, chat_id: str, user_id: str, btn_id: str, aux_data: Dict):
        """مدیریت کلیک روی دکمه‌های Inline"""
        parts = btn_id.split(":")
        action = parts[0]
        data = parts[1] if len(parts) > 1 else None

        if action == "cat":
            await self.send_products(chat_id, int(data))
        elif action == "prod":
            await self.send_product_detail(chat_id, int(data))
        elif action == "add":
            await self.add_to_cart(chat_id, user_id, int(data))
        elif action == "checkout":
            await self.process_checkout(chat_id, user_id)
        elif action == "t_list":
            await self.send_ticket_list(chat_id, user_id)
        elif action == "t_show":
            await self.send_ticket_details(chat_id, user_id, int(data))
        elif action == "t_new":
            await self.api.send_message(chat_id, "💡 لطفا موضوع و متن تیکت خود را در یک پیام بفرستید:")
        elif action == "nav":
            if data == "back_cat":
                await self.send_categories(chat_id)
            elif data == "main":
                await self.send_main_menu(chat_id)

    # ================= UI Methods =================

    async def send_main_menu(self, chat_id: str):
        """ارسال منوی اصلی با Reply Keyboard"""
        text = "👋 به فروشگاه خوش آمدید!\nلطفا یکی از گزینه‌های زیر را انتخاب کنید."

        # ساختار Reply Keyboard طبق مستندات (لیست سطرها)
        keyboard = [
            [{"id": "menu:shop", "text": "🛍 محصولات"}],
            [{"id": "menu:cart", "text": "🛒 سبد خرید"}, {"id": "menu:profile", "text": "👤 پروفایل"}],
            [{"id": "menu:support", "text": "📞 پشتیبانی"}]
        ]

        await self.api.send_message(chat_id, text, reply_keyboard=keyboard)

    async def send_categories(self, chat_id: str):
        """نمایش لیست دسته‌بندی‌ها"""
        with SessionLocal() as db:
            cats = crud.get_root_categories(db)

        if not cats:
            return await self.api.send_message(chat_id, "هیچ دسته‌بندی وجود ندارد.")

        text = "📂 لطفا دسته‌بندی مورد نظر را انتخاب کنید:"
        inline_rows = []
        for c in cats:
            # ID دکمه باید یکتا باشد
            inline_rows.append([{"id": f"cat:{c.id}", "text": c.name, "type": "Simple"}])

        await self.api.send_message(chat_id, text, inline_keyboard=inline_rows)

    async def send_products(self, chat_id: str, cat_id: int):
        """نمایش محصولات یک دسته"""
        with SessionLocal() as db:
            prods = crud.get_active_products_by_category(db, cat_id)

        if not prods:
            return await self.api.send_message(chat_id, "❌ محصولی یافت نشد.")

        text = f"تعداد {len(prods)} محصول یافت شد:"
        inline_rows = []
        for p in prods[:10]:
            inline_rows.append([{"id": f"prod:{p.id}", "text": f"{p.name} - {int(p.price):,} تومان"}])

        # دکمه بازگشت
        inline_rows.append([{"id": "nav:back_cat", "text": "↩ بازگشت به دسته‌ها"}])

        await self.api.send_message(chat_id, text, inline_keyboard=inline_rows)

    async def send_product_detail(self, chat_id: str, prod_id: int):
        """جزئیات محصول (حرفه‌ای با پشتیبانی از گالری تصاویر)"""
        with SessionLocal() as db:
            p = crud.get_product(db, prod_id)
            if not p: return

        # آماده سازی متن
        is_disc = crud.is_product_discount_active(p)
        final_price = p.discount_price if is_disc else p.price
        price_text = f"{int(final_price):,} تومان"
        if is_disc:
            price_text = f"<s>{int(p.price):,}</s> ➡️ {price_text} 🔥"

        txt = (
            f"🛍 **{p.name}**\n"
            f"━━━━━━━━━━━━\n"
            f"📑 برند: {p.brand or 'متفرقه'}\n"
            f"💰 قیمت: {price_text}\n"
            f"📦 وضعیت: {'✅ موجود' if p.stock > 0 else '❌ ناموجود'}\n\n"
            f"📝 توضیحات:\n{p.description or 'توضیحاتی ثبت نشده است.'}"
        )

        # افزودن فوتر برندینگ
        with SessionLocal() as db:
            footer = crud.get_setting(db, "bot_footer_text", "")
        if footer: txt += f"\n\n---\n{footer}"

        inline_rows = [
            [{"id": f"add:{p.id}", "text": "➕ افزودن به سبد"}] if p.stock > 0 else [],
            [{"id": "nav:back_cat", "text": "↩ بازگشت به لیست"}]
        ]
        # فیلتر کردن سطرهای خالی
        inline_rows = [r for r in inline_rows if r]

        # مدیریت تصاویر (Gallery)
        images = p.images if p.images else []
        if not images and p.image_path:
             from bot.models import ProductImage
             images = [{"image_path": p.image_path}] # ساختار ساده برای آپلود

        if images:
            try:
                # ارسال تصویر اول با کپشن و کیبورد
                main_img = images[0]
                # در روبیکا باید فایل آپلود شود تا file_id بگیریم
                # برای بهینه‌سازی می‌توان file_id های روبیکا را هم در دیتابیس ذخیره کرد
                from config import BASE_DIR
                from pathlib import Path
                full_path = str(Path(BASE_DIR) / main_img.image_path)

                # آپلود و ارسال
                f_id = await self.api.upload_file(full_path)
                await self.api.send_file(chat_id, f_id, caption=txt, inline_keyboard=inline_rows)

                # ارسال سایر تصاویر بدون کپشن
                for other_img in images[1:3]: # محدود به ۳ عکس برای جلوگیری از اسپم
                    other_path = str(Path(BASE_DIR) / other_img.image_path)
                    f_id_other = await self.api.upload_file(other_path)
                    await self.api.send_file(chat_id, f_id_other)

            except Exception as e:
                logger.error(f"Gallery Error: {e}")
                await self.api.send_message(chat_id, txt, inline_keyboard=inline_rows)
        else:
            await self.api.send_message(chat_id, txt, inline_keyboard=inline_rows)

    async def handle_search(self, chat_id: str, query: str):
        """جستجوی محصول در روبیکا"""
        with SessionLocal() as db:
            prods = crud.advanced_search_products(db, query=query)

        if not prods:
            return await self.api.send_message(chat_id, f"❌ متاسفانه محصولی برای عبارت '{query}' یافت نشد.")

        text = f"🔎 نتایج جستجو برای '{query}':"
        inline_rows = []
        for p in prods[:10]:
            inline_rows.append([{"id": f"prod:{p.id}", "text": f"🔹 {p.name}"}])

        await self.api.send_message(chat_id, text, inline_keyboard=inline_rows)

    async def add_to_cart(self, chat_id: str, user_id: str, prod_id: int):
        try:
            with SessionLocal() as db:
                crud.add_to_cart(db, user_id, prod_id, 1)
            await self.api.send_message(chat_id, "✅ به سبد خرید اضافه شد.")
        except ValueError as e:
            await self.api.send_message(chat_id, f"⚠️ {str(e)}")

    async def send_cart(self, chat_id: str, user_id: str):
        """نمایش سبد خرید (بهینه شده)"""
        with SessionLocal() as db:
            items = crud.get_cart_items(db, user_id)

        if not items:
            return await self.api.send_message(chat_id, "🛒 سبد خرید شما در حال حاضر خالی است.")

        msg = "🛒 **جزئیات سبد خرید شما:**\n"
        msg += "━━━━━━━━━━━━\n"
        total = 0
        for item in items:
            p = item.product
            price = p.discount_price if crud.is_product_discount_active(p) else p.price
            line_total = price * item.quantity
            total += line_total
            msg += f"🔹 {p.name}\n   تعداد: {item.quantity} | قیمت: {int(line_total):,} ت\n"

        msg += "━━━━━━━━━━━━\n"
        msg += f"💰 **جمع کل: {int(total):,} تومان**"

        inline_rows = [
            [{"id": "checkout", "text": "💳 ثبت و پرداخت نهایی"}],
            [{"id": "nav:back_cat", "text": "🛍 ادامه خرید"}]
        ]
        await self.api.send_message(chat_id, msg, inline_keyboard=inline_rows)

    async def process_checkout(self, chat_id: str, user_id: str):
        """ثبت سفارش نهایی"""
        try:
            with SessionLocal() as db:
                # چک کردن وضعیت ساعات کاری
                if not crud.is_shop_currently_open(db):
                    return await self.api.send_message(chat_id, "⛔️ پوزش می‌طلبیم، فروشگاه در حال حاضر (خارج از ساعات کاری) سفارش جدید نمی‌پذیرد.")

                items = crud.get_cart_items(db, user_id)
                if not items:
                    return await self.api.send_message(chat_id, "🛒 سبد خرید شما خالی است.")

                items_total = sum(float(item.product.price) * item.quantity for item in items)
                ship_cost = int(crud.get_setting(db, "shipping_cost", "0"))
                free_limit = int(crud.get_setting(db, "free_shipping_limit", "0"))
                final_ship = 0 if (free_limit > 0 and items_total >= free_limit) else ship_cost
                final_total = items_total + final_ship

                zp_enabled = crud.get_setting(db, "zarinpal_enabled", "false") == "true"
                merchant_id = crud.get_setting(db, "zarinpal_merchant", "")

                order = crud.create_order_from_cart(db, user_id, {
                    "address": "نیاز به هماهنگی (روبیکا)",
                    "phone": "روبیکا",
                    "postal_code": ""
                })

                if zp_enabled and merchant_id:
                    from bot.zarinpal import ZarinPal
                    zp = ZarinPal(merchant_id)
                    description = f"خرید روبیکا - سفارش #{order.id}"
                    callback_url = "https://rubika.ir"
                    url, authority = await zp.request_payment(final_total, description, callback_url)

                    if url:
                        msg = (
                            f"✅ سفارش #{order.id} ثبت شد.\n"
                            f"💰 مبلغ کل: {int(final_total):,} تومان\n\n"
                            f"برای پرداخت آنلاین روی دکمه زیر کلیک کنید:"
                        )
                        inline_kb = [[{"id": "pay", "text": "💳 پرداخت آنلاین", "url": url}]]
                        return await self.api.send_message(chat_id, msg, inline_keyboard=inline_kb)

                # پرداخت دستی (کارت به کارت)
                raw_cards = crud.get_setting(db, "bank_cards", "[]")
                card_info = "لطفا برای دریافت اطلاعات کارت به پشتیبانی پیام دهید."
                try:
                    cards = json.loads(raw_cards)
                    if cards:
                        card_info = f"💳 شماره کارت: {cards[0]['number']}\n👤 بنام: {cards[0]['owner']}"
                except: pass

                msg = (
                    f"✅ سفارش #{order.id} ثبت شد.\n"
                    f"💰 مبلغ کل: {int(final_total):,} تومان\n\n"
                    f"{card_info}\n\n"
                    f"لطفا پس از واریز، تصویر فیش را به پشتیبانی ارسال کنید."
                )
                await self.api.send_message(chat_id, msg)

        except Exception as e:
            logger.error(f"Checkout Error: {e}")
            await self.api.send_message(chat_id, "❌ مشکلی در ثبت سفارش پیش آمد.")

    async def send_support_menu(self, chat_id: str, user_id: str):
        with SessionLocal() as db:
            tickets = crud.get_user_tickets(db, user_id)

        msg = "📞 **مرکز پشتیبانی و تیکتینگ**\n\nدر این بخش می‌توانید درخواست‌های خود را ثبت و پیگیری کنید."
        inline_kb = [[{"id": "t_new", "text": "➕ ثبت تیکت جدید"}]]
        if tickets:
            inline_kb.append([{"id": "t_list", "text": "📂 مشاهده تیکت‌های من"}])

        await self.api.send_message(chat_id, msg, inline_keyboard=inline_kb)

    async def send_ticket_list(self, chat_id: str, user_id: str):
        with SessionLocal() as db:
            tickets = crud.get_user_tickets(db, user_id)

        if not tickets:
            return await self.api.send_message(chat_id, "تیکتی یافت نشد.")

        msg = "📂 **لیست تیکت‌های شما:**"
        inline_kb = []
        for t in tickets[:10]:
            status = "🟢" if t.status == "pending" else ("🟡" if t.status == "open" else "⚪️")
            inline_kb.append([{"id": f"t_show:{t.id}", "text": f"{status} #{t.id} - {t.subject}"}])

        await self.api.send_message(chat_id, msg, inline_keyboard=inline_kb)

    async def send_user_profile(self, chat_id: str, user_id: str):
        """نمایش پروفایل کاربری در روبیکا"""
        with SessionLocal() as db:
            user = crud.get_user_by_id(db, user_id)
            stats = crud.get_user_stats(db, user_id)

        if not user: return

        msg = (
            f"👤 **پروفایل کاربری شما**\n"
            f"━━━━━━━━━━━━\n"
            f"🆔 شناسه: `{user.user_id}`\n"
            f"💎 امتیاز وفاداری: `{user.loyalty_points}`\n\n"
            f"📊 آمار خرید شما:\n"
            f"📦 تعداد سفارشات: {stats.get('total_orders', 0)}\n"
            f"💰 مجموع خرید: {int(stats.get('total_spent', 0)):,} تومان\n"
            f"━━━━━━━━━━━━\n"
            f"🔗 لینک دعوت اختصاصی شما (برای تلگرام):\n"
            f"https://t.me/{(await self.api.get_me())['bot']['username']}?start=ref_{user.user_id}"
        )
        await self.api.send_message(chat_id, msg)

    async def send_ticket_details(self, chat_id: str, user_id: str, ticket_id: int):
        with SessionLocal() as db:
            t = crud.get_ticket_with_messages(db, ticket_id)

        if not t: return

        status_map = {"open": "🆕 باز", "pending": "⏳ در انتظار پاسخ", "closed": "✅ بسته شده"}
        status_text = status_map.get(t.status, t.status)

        msg = f"🎫 **تیکت پشتیبانی #{t.id}**\n"
        msg += f"📌 موضوع: {t.subject}\n"
        msg += f"📊 وضعیت: {status_text}\n"
        msg += "━━━━━━━━━━━━\n\n"

        for m in t.messages[-5:]:
            sender = "👤 شما" if not m.is_admin else "👨‍💻 پشتیبان"
            time_str = m.created_at.strftime("%H:%M")
            msg += f"{sender} ({time_str}):\n{m.text}\n\n"

        if t.status != 'closed':
            msg += "✍️ برای ارسال پاسخ، متن خود را در یک پیام بفرستید."
        else:
            msg += "🚫 این تیکت بسته شده است."

        await self.api.send_message(chat_id, msg)

    async def handle_support_text(self, chat_id: str, user_id: str, text: str):
        # منطق ساده برای ثبت تیکت جدید یا پاسخ
        # در دنیای واقعی باید وضعیت کاربر را چک کنیم. اینجا اگر تیکت بازی داشته باشد به آن پاسخ می‌دهد
        # در غیر این صورت تیکت جدید می‌سازد
        with SessionLocal() as db:
            tickets = crud.get_user_tickets(db, user_id)
            open_tickets = [t for t in tickets if t.status != 'closed']

            if open_tickets:
                # پاسخ به آخرین تیکت باز
                t = open_tickets[0]
                crud.add_ticket_message(db, t.id, user_id, text)
                await self.api.send_message(chat_id, f"✅ پاسخ شما به تیکت #{t.id} ثبت شد.")
            else:
                # ثبت تیکت جدید
                subject = text[:30] + "..." if len(text) > 30 else text
                t = crud.create_ticket(db, user_id, subject, text)
                await self.api.send_message(chat_id, f"✅ تیکت جدید با موفقیت ثبت شد.\n🆔 شماره تیکت: #{t.id}")
