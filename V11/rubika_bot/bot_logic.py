import asyncio
import logging
import json
from typing import Optional, Dict, Any, List

# واردات نسبتی به ساختار پروژه
from .rubika_client import RubikaAPI, RubikaError
from db.database import SessionLocal
from db import crud, models

logger = logging.getLogger("RubikaBot")

class RubikaWorker:
    def __init__(self, token: str):
        self.api = RubikaAPI(token)
        self.running = False
        self.bot_guid: Optional[str] = None

    async def _initialize_bot(self):
        """دریافت شناسه ربات برای جلوگیری از لوپ"""
        try:
            res = await self.api.get_me()
            # ساختار پاسخ getMe طبق مستندات: {'bot': {'bot_id': ...}}
            if res and "bot" in res:
                self.bot_guid = res["bot"]["bot_id"]
                logger.info(f"Rubika Bot ID identified: {self.bot_guid}")
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")

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
        # ساختار آپدیت طبق مدل Update در 03.txt
        update_type = update.get("type")

        # ۱. پیام جدید (NewMessage)
        if update_type == "NewMessage":
            msg = update.get("new_message", {})
            chat_id = update.get("chat_id")
            sender_id = msg.get("sender_id")

            # فیلتر پیام‌های خود ربات (جلوگیری از لوپ)
            if sender_id == self.bot_guid:
                return

            text = msg.get("text", "")
            aux_data = msg.get("aux_data", {})
            button_id = aux_data.get("button_id")

            if button_id:
                # اگر روی دکمه ای کلیک شده باشد
                await self.handle_button_click(chat_id, sender_id, button_id, aux_data)
            elif text:
                # اگر متن ارسال شده باشد
                await self.handle_text_message(chat_id, sender_id, text)

        # ۲. سایر رویدادها (StartedBot, StoppedBot, etc.)
        elif update_type == "StartedBot":
            user_id = update.get("chat_id") # در StartedBot معمولا chat_id همان کاربر است
            # ارسال پیام خوش‌آمدگویی
            await self.send_main_menu(user_id)

    # ================= Handlers =================

    async def handle_text_message(self, chat_id: str, user_id: str, text: str):
        """مدیریت پیام‌های متنی"""
        # ثبت یا آپدیت کاربر در دیتابیس
        with SessionLocal() as db:
            user = crud.get_or_create_user(db, user_id, "کاربر روبیکا", None, "rubika")

        text = text.strip()

        if text == "/start" or text == "🏠 بازگشت به منو":
            await self.send_main_menu(chat_id)
        elif text == "🛍 محصولات":
            await self.send_categories(chat_id)
        elif text == "🛒 سبد خرید":
            await self.send_cart(chat_id, user_id)
        elif text == "📞 پشتیبانی":
            await self.send_support(chat_id)
        else:
            # پاسخ پیش‌فرض
            await self.api.send_message(chat_id, "متوجه نشدم. لطفا از منو استفاده کنید.")

    async def handle_button_click(self, chat_id: str, user_id: str, btn_id: str, aux_data: Dict):
        """مدیریت کلیک روی دکمه‌های Inline"""

        # ساختار ID دکمه‌ها: `action:data` مثلا `cat:5`
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

    # ================= UI Methods =================

    async def send_main_menu(self, chat_id: str):
        """ارسال منوی اصلی با Reply Keyboard"""
        text = "👋 به فروشگاه خوش آمدید!\nلطفا یکی از گزینه‌های زیر را انتخاب کنید."

        # ساختار Reply Keyboard طبق مستندات (لیست سطرها)
        keyboard = [
            [{"id": "menu:shop", "text": "🛍 محصولات"}],
            [{"id": "menu:cart", "text": "🛒 سبد خرید"}, {"id": "menu:support", "text": "📞 پشتیبانی"}]
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
        """جزئیات محصول"""
        with SessionLocal() as db:
            p = crud.get_product(db, prod_id)
            if not p: return

        txt = (
            f"🛍 <b>{p.name}</b>\n\n"
            f"💰 قیمت: {int(p.price):,} تومان\n"
            f"📦 موجودی: {p.stock}\n\n"
            f"{p.description or ''}"
        )

        inline_rows = [
            [{"id": f"add:{p.id}", "text": "➕ افزودن به سبد", "type": "Simple"}],
            [{"id": "nav:back_cat", "text": "↩ بازگشت"}]
        ]

        await self.api.send_message(chat_id, txt, inline_keyboard=inline_rows)

    async def add_to_cart(self, chat_id: str, user_id: str, prod_id: int):
        try:
            with SessionLocal() as db:
                crud.add_to_cart(db, user_id, prod_id, 1)
            await self.api.send_message(chat_id, "✅ به سبد خرید اضافه شد.")
        except ValueError as e:
            await self.api.send_message(chat_id, f"⚠️ {str(e)}")

    async def send_cart(self, chat_id: str, user_id: str):
        """نمایش سبد خرید"""
        with SessionLocal() as db:
            items = crud.get_cart_items(db, user_id)

        if not items:
            return await self.api.send_message(chat_id, "🛒 سبد خرید شما خالی است.")

        msg = "🛒 سبد خرید شما:\n\n"
        total = 0
        for item in items:
            p = item.product
            total += p.price * item.quantity
            msg += f"• {p.name} x {item.quantity}\n"

        msg += f"\n💰 جمع کل: {int(total):,} تومان"

        inline_rows = [[{"id": "checkout", "text": "✅ نهایی کردن سفارش"}]]
        await self.api.send_message(chat_id, msg, inline_keyboard=inline_rows)

    async def process_checkout(self, chat_id: str, user_id: str):
        """ثبت سفارش نهایی"""
        try:
            with SessionLocal() as db:
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

    async def send_support(self, chat_id: str):
        msg = "📞 برای ارتباط با پشتیبانی به آیدی زیر پیام دهید:\n@YourSupportID"
        await self.api.send_message(chat_id, msg)
