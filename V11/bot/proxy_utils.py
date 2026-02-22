import re
import json
import base64
import logging
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, Any

logger = logging.getLogger("ProxyUtils")

def parse_v2ray_link(link: str) -> Optional[Dict[str, Any]]:
    """
    پارس کردن لینک‌های V2Ray/Xray شامل VLESS, VMESS, SS, Trojan
    """
    link = link.strip()
    try:
        if link.startswith("vless://"):
            return _parse_vless(link)
        elif link.startswith("vmess://"):
            return _parse_vmess(link)
        elif link.startswith("ss://"):
            return _parse_ss(link)
        elif link.startswith("trojan://"):
            return _parse_trojan(link)
    except Exception as e:
        logger.error(f"Error parsing link {link[:20]}...: {e}")

    return None

def _parse_vless(link: str) -> Dict[str, Any]:
    parsed = urlparse(link)
    # vless://uuid@host:port
    user_info = parsed.netloc.split('@')
    uuid = user_info[0]
    host_port = user_info[1].split(':')
    host = host_port[0]
    port = int(host_port[1])

    params = parse_qs(parsed.query)
    name = unquote(parsed.fragment) or f"VLESS-{host}"

    return {
        "protocol": "vless",
        "name": name,
        "host": host,
        "port": port,
        "uuid": uuid,
        "params": {k: v[0] for k, v in params.items()},
        "raw_link": link,
        "config_type": "link"
    }

def _parse_vmess(link: str) -> Dict[str, Any]:
    # vmess://base64
    b64_data = link[8:]
    # رفع مشکل padding در base64
    missing_padding = len(b64_data) % 4
    if missing_padding:
        b64_data += '=' * (4 - missing_padding)

    decoded = base64.b64decode(b64_data).decode('utf-8')
    data = json.loads(decoded)

    return {
        "protocol": "vmess",
        "name": data.get("ps", "VMESS-Config"),
        "host": data.get("add"),
        "port": int(data.get("port", 443)),
        "uuid": data.get("id"),
        "params": data,
        "raw_link": link,
        "config_type": "link"
    }

def _parse_ss(link: str) -> Dict[str, Any]:
    parsed = urlparse(link)
    # ss://base64(method:password)@host:port#name
    name = unquote(parsed.fragment) or "Shadowsocks"

    if '@' in parsed.netloc:
        user_info_b64, host_port = parsed.netloc.split('@')
        # باز کردن userinfo
        missing_padding = len(user_info_b64) % 4
        if missing_padding: user_info_b64 += '=' * (4 - missing_padding)
        user_info = base64.b64decode(user_info_b64).decode('utf-8')

        host, port = host_port.split(':')
        return {
            "protocol": "ss",
            "name": name,
            "host": host,
            "port": int(port),
            "username": user_info.split(':')[0], # Method
            "password": user_info.split(':')[1],
            "raw_link": link,
            "config_type": "link"
        }
    else:
        # متد قدیمی یا SIP002 بدون @
        # اینجا پیچیده‌تر است، فعلاً ساده‌ترین حالت را ساپورت می‌کنیم
        return {
            "protocol": "ss",
            "name": name,
            "host": parsed.hostname,
            "port": parsed.port,
            "raw_link": link,
            "config_type": "link"
        }

def _parse_trojan(link: str) -> Dict[str, Any]:
    parsed = urlparse(link)
    user_info = parsed.netloc.split('@')
    password = user_info[0]
    host_port = user_info[1].split(':')
    host = host_port[0]
    port = int(host_port[1])

    name = unquote(parsed.fragment) or f"Trojan-{host}"

    return {
        "protocol": "trojan",
        "name": name,
        "host": host,
        "port": port,
        "password": password,
        "raw_link": link,
        "config_type": "link"
    }

async def tcp_ping(host: str, port: int, timeout: float = 3.0) -> Optional[int]:
    """
    تست در دسترس بودن سرور (Latency ساده TCP)
    """
    import time
    import asyncio

    start = time.time()
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        latency = int((time.time() - start) * 1000)
        writer.close()
        await writer.wait_closed()
        return latency
    except:
        return None

def generate_xray_config(proxy_data: Dict[str, Any], local_port: int = 2080) -> Dict[str, Any]:
    """
    تولید فایل کانفیگ JSON برای هسته Xray
    """
    protocol = proxy_data["protocol"]

    # تنظیمات خروجی (Outbound)
    outbound = {
        "protocol": protocol,
        "settings": {
            "vnext": [{
                "address": proxy_data["host"],
                "port": proxy_data["port"],
                "users": [{"id": proxy_data.get("uuid"), "encryption": "none"}]
            }]
        },
        "streamSettings": {
            "network": "tcp",
            "security": "none"
        }
    }

    if protocol == "trojan":
        outbound["settings"] = {
            "servers": [{"address": proxy_data["host"], "port": proxy_data["port"], "password": proxy_data.get("password")}]
        }

    # مدیریت پارامترهای پیشرفته (REALITY, TLS, etc)
    params = proxy_data.get("params", {})
    if params.get("security") in ["tls", "reality"]:
        outbound["streamSettings"]["security"] = params["security"]
        if params["security"] == "reality":
            outbound["streamSettings"]["realitySettings"] = {
                "fingerprint": params.get("fp", "chrome"),
                "serverName": params.get("sni", ""),
                "publicKey": params.get("pbk", ""),
                "shortId": params.get("sid", ""),
                "spiderX": params.get("spx", "")
            }
        else:
            outbound["streamSettings"]["tlsSettings"] = {
                "serverName": params.get("sni", "")
            }

    if params.get("type") == "ws":
        outbound["streamSettings"]["network"] = "ws"
        outbound["streamSettings"]["wsSettings"] = {
            "path": params.get("path", "/"),
            "headers": {"Host": params.get("host", "")}
        }
    elif params.get("type") == "grpc":
        outbound["streamSettings"]["network"] = "grpc"
        outbound["streamSettings"]["grpcSettings"] = {"serviceName": params.get("serviceName", "")}

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": local_port,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": True}
        }],
        "outbounds": [outbound, {"protocol": "freedom", "tag": "direct"}]
    }

class XrayManager:
    """
    مدیریت اجرای هسته Xray در پس‌زمینه
    """
    def __init__(self, executable_path: str = "tools/xray/xray.exe"):
        import os
        from config import BASE_DIR
        self.path = os.path.join(BASE_DIR, executable_path)
        self.process = None
        self.config_path = os.path.join(BASE_DIR, "temp/xray_config.json")

    def is_available(self):
        import os
        return os.path.exists(self.path)

    async def start(self, proxy_data: Dict[str, Any], port: int = 2080):
        import json
        import os
        import subprocess

        if not self.is_available():
            raise FileNotFoundError(f"Xray core not found at {self.path}")

        config = generate_xray_config(proxy_data, port)
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f)

        # اجرا در پس‌زمینه
        self.process = subprocess.Popen(
            [self.path, "run", "-c", self.config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return f"socks5://127.0.0.1:{port}"

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
