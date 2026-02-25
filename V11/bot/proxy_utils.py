import socket
import time
import re
import logging
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

def test_proxy_connectivity(proxy_url, proxy_type):
    """تست کلی اتصال بر اساس نوع پروکسی"""
    if proxy_type == 'v2ray':
        data = parse_v2ray_link(proxy_url)
        if data and data['address']:
            return tcp_ping(data['address'], data['port'])
    else:
        # برای HTTP/SOCKS5
        try:
            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port or (80 if parsed.scheme == 'http' else 1080)
            if host:
                return tcp_ping(host, port)
        except:
            pass
    return -2
