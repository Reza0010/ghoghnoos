import aiohttp
import logging
import os
import json
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

logger = logging.getLogger("RubikaAPI")

class RubikaError(Exception):
    """خطای اختصاصی برای روبیکا"""
    pass

class RubikaAPI:
    """
    کلاینت ناهمگام (Async) برای API نسخه 3 روبیکا.
    مستندات: https://botapi.rubika.ir
    """
    BASE_URL = "https://botapi.rubika.ir/v3/"

    def __init__(self, token: str):
        self.token = token
        self.url = f"{self.BASE_URL}{token}/"
        self.session: Optional[aiohttp.ClientSession] = None
        # ذخیره آخرین آفست برای جلوگیری از دریافت پیام تکراری
        self._last_offset_id: Optional[str] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=40, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def _request(self, method: str, payload: Dict[str, Any] = None) -> Dict:
        """ارسال درخواست استاندارد POST و مدیریت خطاها"""
        session = await self._get_session()
        full_url = f"{self.url}{method}"
        
        try:
            async with session.post(full_url, json=payload or {}) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"HTTP Error {resp.status}: {text}")
                    raise RubikaError(f"HTTP Error {resp.status}")
                
                data = await resp.json()
                
                status = data.get("status")
                if status == "ERROR":
                    desc = data.get("description", "Unknown Error")
                    logger.error(f"Rubika Logic Error: {desc}")
                    raise RubikaError(desc)
                
                # برگرداندن بخش data (اگر وجود داشته باشد) یا کل دیتا
                return data.get("data", data)

        except aiohttp.ClientError as e:
            logger.error(f"Connection Error: {e}")
            raise RubikaError(f"Connection Error: {e}")

    def _build_keypad(self, buttons: List[List[Dict]]) -> Dict:
        """
        ساخت ساختار استاندارد کیبورد طبق مستندات:
        { "rows": [ {"buttons": [...]} ] }
        """
        rows = []
        for row in buttons:
            row_buttons = []
            for btn in row:
                # هر دکمه باید حداقل id و text داشته باشد
                btn_obj = {
                    "id": str(btn.get("id", "unknown")),
                    "type": btn.get("type", "Simple"),
                    "button_text": btn.get("text", "Button")
                }
                # پشتیبانی از لینک در دکمه‌های شیشه‌ای روبیکا
                if btn.get("url"):
                    btn_obj["url"] = btn["url"]
                    btn_obj["type"] = "OpenUrl"

                # اگر دکمه نوع دیگری مثل Selection است
                if btn.get("selection"):
                     btn_obj["button_selection"] = btn["selection"]
                
                row_buttons.append(btn_obj)
            rows.append({"buttons": row_buttons})
            
        return {"rows": rows}

    # =========================================================================
    # متدهای اصلی (Core Methods)
    # =========================================================================

    async def get_me(self) -> Dict:
        """دریافت اطلاعات ربات"""
        return await self._request("getMe")

    async def send_message(
        self, 
        chat_id: str, 
        text: str, 
        reply_keyboard: List[List[Dict]] = None, 
        inline_keyboard: List[List[Dict]] = None,
        reply_to_message_id: str = None
    ) -> str:
        """
        ارسال پیام متنی با یا بدون کیبورد.
        خروجی: message_id
        """
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        if reply_keyboard:
            payload["chat_keypad_type"] = "New"
            payload["chat_keypad"] = self._build_keypad(reply_keyboard)
            
        if inline_keyboard:
            payload["inline_keypad"] = self._build_keypad(inline_keyboard)
            
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        result = await self._request("sendMessage", payload)
        return result.get("message_id")

    async def edit_message_text(self, chat_id: str, message_id: str, text: str, inline_keyboard: List[List[Dict]] = None):
        """ویرایش متن پیام قبلی"""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if inline_keyboard:
            payload["inline_keypad"] = self._build_keypad(inline_keyboard)
        
        await self._request("editMessageText", payload)

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keyboard: List[List[Dict]]):
        """
        فقط تغییر دکمه‌های شیشه‌ای (مثلا برای صفحه بندی)
        """
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_keypad": self._build_keypad(inline_keyboard)
        }
        await self._request("editMessageKeypad", payload)

    async def delete_message(self, chat_id: str, message_id: str):
        """حذف پیام"""
        await self._request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    # =========================================================================
    # دریافت آپدیت‌ها (Polling)
    # =========================================================================

    async def get_updates(self, limit: int = 100) -> List[Dict]:
        """
        دریافت پیام‌های جدید.
        مدیریت خودکار offset_id برای جلوگیری از دریافت پیام تکراری.
        """
        payload = {"limit": limit}
        
        # ارسال آخرین آفست برای دریافت پیام‌های جدیدتر
        if self._last_offset_id:
            payload["offset_id"] = self._last_offset_id
            
        result = await self._request("getUpdates", payload)
        
        updates = result.get("updates", [])
        next_offset = result.get("next_offset_id")
        
        # اگر آفست جدیدی داریم، ذخیره می‌کنیم
        if next_offset:
            self._last_offset_id = next_offset
            
        return updates

    # =========================================================================
    # فایل‌ها (Files)
    # =========================================================================

    async def request_send_file(self, file_type: str = "Image") -> Dict:
        """مرحله ۱: درخواست آدرس آپلود"""
        return await self._request("requestSendFile", {"type": file_type})

    async def upload_file(self, file_path: str, file_type: str = "Image") -> str:
        """
        آپلود فایل و برگرداندن file_id.
        شامل دو مرحله: درخواست URL و آپلود فایل.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Get Upload URL
        req_data = await self.request_send_file(file_type)
        upload_url = req_data.get("upload_url")
        
        if not upload_url:
            raise RubikaError("Could not get upload URL")

        # 2. Upload File
        session = await self._get_session()
        file_name = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('file', f, filename=file_name)
            
            async with session.post(upload_url, data=form) as resp:
                if resp.status != 200:
                    raise RubikaError("File upload failed")
                
                up_data = await resp.json()
                if up_data.get("status") == "OK":
                    return up_data["data"]["file_id"]
                else:
                    raise RubikaError(up_data.get("description", "Upload error"))

    async def send_file(self, chat_id: str, file_id: str, caption: str = None, inline_keyboard: List[List[Dict]] = None):
        """ارسال فایل با file_id"""
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": caption or ""
        }
        if inline_keyboard:
            payload["inline_keypad"] = self._build_keypad(inline_keyboard)
            
        return await self._request("sendFile", payload)

    # =========================================================================
    # متدهای کاربران و گروه‌ها
    # =========================================================================

    async def ban_chat_member(self, chat_id: str, user_id: str):
        """مسدود کردن کاربر در گروه/کانال"""
        await self._request("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def unban_chat_member(self, chat_id: str, user_id: str):
        """رفع مسدودیت کاربر"""
        await self._request("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def get_chat(self, chat_id: str) -> Dict:
        """دریافت اطلاعات چت"""
        return await self._request("getChat", {"chat_id": chat_id})

    async def set_commands(self, commands: List[Dict]):
        """
        تنظیم منوی دستورات (Commands)
        ورودی: لیستی از {command: "start", description: "شروع"}
        """
        formatted = [{"command": c["command"], "description": c["description"]} for c in commands]
        await self._request("setCommands", {"bot_commands": formatted})

    async def close(self):
        """بستن سشن"""
        if self.session and not self.session.closed:
            await self.session.close()