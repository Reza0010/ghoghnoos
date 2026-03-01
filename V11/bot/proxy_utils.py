import socket
import time
import re
import logging
import httpx
from urllib.parse import urlparse

logger = logging.getLogger("ProxyUtils")

def tcp_ping(host, port, timeout=5):
    """تست پینگ TCP برای بررسی در دسترس بودن سرور"""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, int(port)))
        sock.close()
        return int((time.time() - start_time) * 1000)
    except socket.timeout:
        return -1 # Timeout
    except Exception as e:
        logger.debug(f"Ping failed for {host}:{port} -> {e}")
        return -2 # Error

def parse_v2ray_link(link):
    """
    پارسر هوشمند برای استخراج تمام مشخصات از لینک‌های V2Ray
    پشتیبانی از VLESS, VMESS, SS, Trojan
    """
    try:
        res = {"protocol": None, "address": None, "port": 443, "id": None, "security": "tls", "type": "tcp"}

        if link.startswith("vmess://"):
            import base64, json
            data_b64 = link.replace("vmess://", "")
            data_b64 += "=" * ((4 - len(data_b64) % 4) % 4)
            data = json.loads(base64.b64decode(data_b64).decode('utf-8'))
            res.update({
                "protocol": "vmess", "address": data.get('add'),
                "port": int(data.get('port', 443)), "id": data.get('id'),
                "security": data.get('tls', 'none'), "type": data.get('net', 'tcp')
            })
            return res

        parsed = urlparse(link)
        res["protocol"] = parsed.scheme

        # netloc: uuid@host:port
        netloc = parsed.netloc
        if "@" in netloc:
            res["id"], host_port = netloc.split("@")
        else:
            host_port = netloc

        if ":" in host_port:
            res["address"], port = host_port.split(":")
            res["port"] = int(port)
        else:
            res["address"] = host_port

        # Parse query params for security, sni, etc.
        from urllib.parse import parse_qs
        query = parse_qs(parsed.query)
        if 'security' in query: res["security"] = query['security'][0]
        if 'type' in query: res["type"] = query['type'][0]
        if 'sni' in query: res["sni"] = query['sni'][0]
        if 'fp' in query: res["fp"] = query['fp'][0]

        return res
    except Exception as e:
        logger.error(f"Failed to parse V2Ray link: {e}")
        return None

def get_proxy_location(host):
    """تشخیص کشور سرور با استفاده از Geo-IP API"""
    if not host or host == "127.0.0.1": return None
    try:
        # استفاده از یک API رایگان و سریع
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"http://ip-api.com/json/{host}?fields=status,countryCode")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("countryCode")
    except:
        pass
    return None

def test_proxy_connectivity(proxy_url, proxy_type):
    """تست کلی اتصال بر اساس نوع پروکسی"""
    host = None
    port = None

    if proxy_type == 'v2ray':
        data = parse_v2ray_link(proxy_url)
        if data and data['address']:
            host = data['address']
            port = data['port']
    else:
        try:
            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port or (80 if parsed.scheme == 'http' else 1080)
        except: pass

    if host and port:
        return tcp_ping(host, port), get_proxy_location(host)

    return -2, None
