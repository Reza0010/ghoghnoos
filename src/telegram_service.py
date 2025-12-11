import configparser
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

CONFIG_FILE = 'config.ini'

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(
        f"Configuration file '{CONFIG_FILE}' not found. "
        f"Please create it by copying 'config.ini.example' and filling in your details. "
        f"See README.md for more information."
    )

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

try:
    API_ID = int(config['telegram']['api_id'])
    API_HASH = config['telegram']['api_hash']
except (KeyError, ValueError):
    raise ValueError(
        f"Configuration file '{CONFIG_FILE}' is missing required keys or has invalid values. "
        f"Please ensure 'api_id' and 'api_hash' are present under the [telegram] section."
    )

class TelegramService:
    def __init__(self, session_file='telegram_session.session'):
        self.client = TelegramClient(session_file, API_ID, API_HASH)
        self.phone_number = None

    async def connect(self):
        await self.client.connect()

    def is_connected(self):
        return self.client.is_connected()

    async def send_code(self, phone_number):
        self.phone_number = phone_number
        try:
            await self.client.send_code_request(phone_number)
            return True, "Verification code sent."
        except Exception as e:
            return False, str(e)

    async def login(self, code, password=None):
        try:
            await self.client.sign_in(self.phone_number, code)
            return True, "Login successful!"
        except SessionPasswordNeededError:
            try:
                await self.client.sign_in(password=password)
                return True, "Login successful!"
            except Exception as e_pass:
                return False, str(e_pass)
        except Exception as e:
            return False, str(e)

    async def get_dialogs(self):
        return await self.client.get_dialogs()

    async def disconnect(self):
        await self.client.disconnect()
