"""
FixBoard Miner Manager - WhatsMiner Port 4433 Secure API Client
Implements length-prefixed TCP framing and SHA256 Token Generation for WhatsMiner secure read/write commands.
"""

import socket
import struct
import json
import time
import hashlib
import base64
from typing import Optional, Dict, Tuple

class WhatsMinerSecureAPI:
    def __init__(self, ip: str, port: int = 4433, timeout: float = 5.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def send_raw_command(self, request_dict: dict) -> Optional[dict]:
        """
        Sends a JSON command over TCP Port 4433 with 4-byte little-endian length prefix.
        Reads response with the same 4-byte little-endian prefix.
        """
        try:
            payload_str = json.dumps(request_dict)
            payload_bytes = payload_str.encode("ascii")
            length_prefix = struct.pack("<I", len(payload_bytes))

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.ip, self.port))

                # Send 4-byte little-endian length + JSON payload
                s.sendall(length_prefix + payload_bytes)

                # Receive 4-byte response length
                length_bytes = s.recv(4)
                if len(length_bytes) < 4:
                    return None

                resp_length = struct.unpack("<I", length_bytes)[0]

                # Receive the full response string based on length
                chunks = []
                bytes_received = 0
                while bytes_received < resp_length:
                    chunk = s.recv(min(resp_length - bytes_received, 4096))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    bytes_received += len(chunk)

                full_resp = b"".join(chunks).decode("ascii", errors="ignore")
                if not full_resp:
                    return None

                return json.loads(full_resp)
        except Exception as e:
            # Silent logging
            return None

    def get_miner_status(self, filter_param: Optional[str] = None) -> Optional[dict]:
        """
        Retrieves real-time status from the miner.
        Read-only command. No authentication token required.
        """
        req = {"cmd": "get.miner.status"}
        if filter_param:
            req["param"] = filter_param
        return self.send_raw_command(req)

    def get_device_info(self) -> Optional[dict]:
        """
        Retrieves device info (model, firmware, salt, etc.).
        Read-only command. No authentication token required.
        """
        return self.send_raw_command({"cmd": "get.device.info"})

    def extract_salt(self) -> Optional[str]:
        """Helper to fetch salt from device info for token generation."""
        resp = self.get_device_info()
        if resp and resp.get("code") == 0:
            msg = resp.get("msg", {})
            if isinstance(msg, dict):
                return msg.get("salt")
        return None

    def generate_token(self, cmd: str, password: str, salt: str, timestamp: int) -> str:
        """
        Generates security token:
        1. Token = Base64(SHA256(command + password + salt + timestamp))
        2. First 8 characters are used as the token.
        """
        input_str = f"{cmd}{password}{salt}{timestamp}"
        sha = hashlib.sha256(input_str.encode("utf-8")).digest()
        b64_str = base64.b64encode(sha).decode("utf-8")
        return b64_str[:8]

    def execute_write_command(self, cmd: str, password: str, account: str = "super", param: Optional[dict] = None) -> Optional[dict]:
        """
        Executes privileged set.* write commands by performing authentication token handshake.
        """
        salt = self.extract_salt()
        if not salt:
            return {"code": -1, "desc": "Failed to retrieve salt from device"}

        ts = int(time.time())
        token = self.generate_token(cmd, password, salt, ts)

        req = {
            "cmd": cmd,
            "ts": ts,
            "token": token,
            "account": account,
            "param": param or {}
        }

        return self.send_raw_command(req)

    def reboot(self, password: str, account: str = "super") -> bool:
        """Triggers WhatsMiner reboot."""
        res = self.execute_write_command("set.miner.reboot", password, account)
        return res is not None and res.get("code") == 0

    def restart_mining(self, password: str, account: str = "super") -> bool:
        """Restarts the btminer mining process."""
        res = self.execute_write_command("set.miner.restart", password, account)
        return res is not None and res.get("code") == 0

    def set_led_blink(self, blink: bool, password: str, account: str = "super") -> bool:
        """Sets the locator LED blink state (True = Blink, False = Off)."""
        param = {"blink": 1 if blink else 0}
        res = self.execute_write_command("set.miner.led_blink", password, account, param)
        return res is not None and res.get("code") == 0

    def set_pools(self, pools_list: list, password: str, account: str = "super") -> bool:
        """
        Configures pools on the WhatsMiner.
        pools_list: List of dicts, e.g. [{"url": "...", "worker": "...", "passwd": "..."}]
        """
        param = {"pools": pools_list}
        res = self.execute_write_command("set.miner.pools", password, account, param)
        return res is not None and res.get("code") == 0
