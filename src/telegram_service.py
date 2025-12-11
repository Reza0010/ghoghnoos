import configparser
import os
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import socks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_proxy_settings():
    try:
        if 'proxy' in config and config['proxy'].get('server'):
            proxy_type = config['proxy'].get('type', 'SOCKS5').upper()
            server = config['proxy']['server']
            port = int(config['proxy']['port'])

            if proxy_type == 'MTPROTO':
                secret = config['proxy'].get('secret', '')
                return ('mtproxy', server, port, secret)
            else:
                username = config['proxy'].get('username')
                password = config['proxy'].get('password')
                proxy_protocol = socks.SOCKS5 if proxy_type == 'SOCKS5' else socks.HTTP

                return {
                    'proxy_type': proxy_protocol,
                    'addr': server,
                    'port': port,
                    'username': username,
                    'password': password
                }
    except (ValueError, KeyError) as e:
        logging.warning(f"Invalid proxy settings in '{CONFIG_FILE}': {e}. Proceeding without proxy.")
    return None

class TelegramService:
    def __init__(self, session_file='telegram_session.session'):
        self.proxy = get_proxy_settings()
        self.client = TelegramClient(session_file, API_ID, API_HASH, proxy=self.proxy)
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

    def save_proxy_settings(self, proxy_type, server, port, username, password, secret):
        if 'proxy' not in config:
            config.add_section('proxy')

        config.set('proxy', 'type', proxy_type)
        config.set('proxy', 'server', server)
        config.set('proxy', 'port', str(port))
        config.set('proxy', 'username', username)
        config.set('proxy', 'password', password)
        config.set('proxy', 'secret', secret)

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
