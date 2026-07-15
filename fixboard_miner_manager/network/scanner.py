"""
FixBoard Miner Manager - Network Scan Engine
Implements a highly parallelized multi-threaded background network scanner utilizing PySide6 QThread
and sockets to discover WhatsMiner and Antminer devices on Port 4028, 4433, or HTTP.
"""

import socket
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QThread, Signal, QObject
from typing import List, Dict, Optional

from database.db_manager import DatabaseManager
from utils.helpers import parse_ip_range
from miners.cgminer_api import CGMinerAPI
from miners.whatsminer_api import WhatsMinerSecureAPI
from miners.http_api import HTTPFallbackAPI

class ScanSignals(QObject):
    progress = Signal(int, str)              # (percent_done, current_ip)
    miner_discovered = Signal(dict)         # Miner data dictionary
    finished = Signal(list)                 # List of all discovered miners

class NetworkScanner(QThread):
    def __init__(self, ip_range_str: str, max_threads: int = 50):
        super().__init__()
        self.ip_range_str = ip_range_str
        self.max_threads = max_threads
        self.signals = ScanSignals()
        self.is_running = True
        self.discovered_miners = []
        self.db = DatabaseManager()

    def stop(self):
        """Requests the scanner to stop immediately."""
        self.is_running = False

    def run(self):
        """Entry point for the QThread background process."""
        ips = parse_ip_range(self.ip_range_str)
        total_ips = len(ips)

        if total_ips == 0:
            self.signals.progress.emit(100, "بدون IP معتبر")
            self.signals.finished.emit([])
            return

        completed = 0
        lock = threading.Lock()

        def scan_ip(ip: str):
            if not self.is_running:
                return

            miner_info = self._probe_ip(ip)

            with lock:
                nonlocal completed
                completed += 1
                percent = int((completed / total_ips) * 100)
                self.signals.progress.emit(percent, ip)

                if miner_info:
                    self.discovered_miners.append(miner_info)
                    self.signals.miner_discovered.emit(miner_info)

                    # Store inside SQLite
                    self.db.add_or_update_miner(
                        ip=miner_info["ip"],
                        mac=miner_info["mac"],
                        name=miner_info["name"],
                        model=miner_info["model"],
                        brand=miner_info["brand"],
                        is_online=1
                    )

        # Execute parallel scans using ThreadPoolExecutor for speed
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            executor.map(scan_ip, ips)

        # Mark any miners that were not in this scan as offline in DB, if needed
        # (For simplicity and user requirements, we just keep their offline statuses correct)

        self.signals.finished.emit(self.discovered_miners)

    def _probe_ip(self, ip: str) -> Optional[dict]:
        """
        Probes a single IP address on various ports to detect if it is an Antminer or WhatsMiner.
        """
        # 1. Probe WhatsMiner modern Port 4433 first
        if self._is_port_open(ip, 4433):
            ws_api = WhatsMinerSecureAPI(ip, timeout=2.0)
            info = ws_api.get_device_info()
            if info and info.get("code") == 0:
                msg = info.get("msg", {})
                model = msg.get("model_type", "WhatsMiner")
                mac = msg.get("mac_addr", "دریافت نشد")
                # Clean up MAC format if needed
                return {
                    "ip": ip,
                    "mac": mac,
                    "name": f"WhatsMiner_{ip.split('.')[-1]}",
                    "model": model,
                    "brand": "WhatsMiner",
                    "source": "Port 4433 (Secure API)"
                }

        # 2. Probe CGMiner standard Port 4028
        if self._is_port_open(ip, 4028):
            cg_api = CGMinerAPI(ip, timeout=2.0)
            ver = cg_api.get_version()
            if ver:
                # Discovered a cgminer-compatible miner
                # Inspect response to differentiate between Antminer and WhatsMiner
                description = ""
                mac = "دریافت نشد"
                model = "دریافت نشد"
                brand = "Antminer"  # Default

                status_list = ver.get("STATUS", [])
                if status_list and isinstance(status_list, list):
                    description = status_list[0].get("Description", "").lower()

                version_list = ver.get("VERSION", [])
                if version_list and isinstance(version_list, list):
                    v_item = version_list[0]
                    model = v_item.get("Platform", v_item.get("Type", "Antminer"))
                    # Antminer often exposes MAC in VERSION as 'MAC' or 'Mac'
                    mac = v_item.get("MAC", v_item.get("Mac", "دریافت نشد"))

                if "whatsminer" in description or "btminer" in description:
                    brand = "WhatsMiner"
                    if model == "Antminer" or not model:
                        model = "WhatsMiner"
                else:
                    if "antminer" in description or "bmminer" in description:
                        brand = "Antminer"

                return {
                    "ip": ip,
                    "mac": mac,
                    "name": f"{brand}_{ip.split('.')[-1]}",
                    "model": model,
                    "brand": brand,
                    "source": "Port 4028 (CGMiner API)"
                }

        # 3. Probe HTTP Port 80 for older devices or custom firmware with disabled APIs
        if self._is_port_open(ip, 80):
            http_api = HTTPFallbackAPI(ip, timeout=2.0)
            success, body = http_api.send_request("/")
            if success:
                body_lower = body.lower()
                if "antminer" in body_lower or "bmminer" in body_lower or "luci-static" in body_lower:
                    return {
                        "ip": ip,
                        "mac": "دریافت نشد",
                        "name": f"Antminer_{ip.split('.')[-1]}",
                        "model": "Antminer (CGI-Web)",
                        "brand": "Antminer",
                        "source": "Port 80 (HTTP)"
                    }
                elif "whatsminer" in body_lower:
                    return {
                        "ip": ip,
                        "mac": "دریافت نشد",
                        "name": f"WhatsMiner_{ip.split('.')[-1]}",
                        "model": "WhatsMiner (CGI-Web)",
                        "brand": "WhatsMiner",
                        "source": "Port 80 (HTTP)"
                    }

        return None

    def _is_port_open(self, ip: str, port: int) -> bool:
        """Helper to quickly check if a socket port is responsive."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                s.connect((ip, port))
                return True
        except Exception:
            return False
