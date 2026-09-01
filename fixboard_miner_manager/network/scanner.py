"""
FixBoard Miner Manager - Network Scan Engine (Enhanced)
Implements a highly parallelized multi-threaded background network scanner.
Enhances exact miner model detection (e.g. S19 Pro, S9, M30S, M50) by parsing VERSION, DEVDETAILS, and STATS.
"""

import socket
import json
import threading
import re
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
    def __init__(self, ip_range_str: str, max_threads: int = 60):
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

        self.signals.finished.emit(self.discovered_miners)

    def _probe_ip(self, ip: str) -> Optional[dict]:
        """
        Probes a single IP address on various ports to detect if it is an Antminer or WhatsMiner.
        Extracts exact device models (e.g. S19, S9, M30S, M50) via stats/devdetails.
        """
        # 1. Probe WhatsMiner modern Port 4433 first
        if self._is_port_open(ip, 4433):
            ws_api = WhatsMinerSecureAPI(ip, timeout=2.0)
            info = ws_api.get_device_info()
            if info and info.get("code") == 0:
                msg = info.get("msg", {})
                model = msg.get("model_type", "WhatsMiner")

                # Clean up WhatsMiner exact model variants (e.g., M30S+, M50, etc.)
                if not model or model == "WhatsMiner":
                    model = msg.get("model", "WhatsMiner M30S")

                mac = msg.get("mac_addr", "دریافت نشد")
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

            # Fetch Version, devdetails, and stats to pinpoint exact model
            ver = cg_api.get_version()
            devs = cg_api.send_command("devdetails")
            stats = cg_api.get_stats()

            if ver:
                # Discovered a cgminer-compatible miner
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
                    # Generic model placeholder
                    model = v_item.get("Platform", v_item.get("Type", ""))
                    mac = v_item.get("MAC", v_item.get("Mac", "دریافت نشد"))

                # Try parsing DEVDETAILS for exact model (S19, S17, S9, etc.)
                if devs:
                    dev_items = devs.get("DEVDETAILS", [])
                    if dev_items and isinstance(dev_items, list):
                        dev_model = dev_items[0].get("Model", "")
                        if dev_model:
                            model = dev_model

                # Try parsing STATS for exact model signatures
                if stats:
                    stat_items = stats.get("STATS", [])
                    if stat_items and isinstance(stat_items, list):
                        s_item = stat_items[0]
                        # S19 / S19 Pro often reports type/model in STATS
                        stats_model = s_item.get("Type", s_item.get("ID", s_item.get("old_version", "")))
                        if stats_model:
                            # Clean up compile strings or generic hashes (e.g. S19 XP, S19J Pro)
                            clean_match = re.search(r'(S9|S17|S19|T19|T17|T9|L7|D7|E9|Z15|M20|M30|M50)\s?[A-Za-z0-9\+\-\s]*', str(stats_model))
                            if clean_match:
                                model = clean_match.group(0).strip()
                            else:
                                model = stats_model

                # Brand categorization
                if "whatsminer" in description or "btminer" in description:
                    brand = "WhatsMiner"
                    if not model or model in ("am", "c5", "bmminer", "cgminer"):
                        model = "WhatsMiner M30S"
                else:
                    if "antminer" in description or "bmminer" in description:
                        brand = "Antminer"
                    # If model is blank or generic (like 'am' or 'c5'), deduce S9/S19 based on stats keys
                    if not model or model.lower() in ("am", "c5", "bmminer", "cgminer", "platform"):
                        if stats:
                            s_item = stats.get("STATS", [{}])[0]
                            if "chain_rate0" in s_item or "chain_rate1" in s_item:
                                model = "Antminer S19"
                            elif "temp3_1" in s_item:
                                model = "Antminer S17"
                            else:
                                model = "Antminer S9"
                        else:
                            model = "Antminer S9"

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
                    # Extract title / headers if possible
                    model = "Antminer"
                    title_match = re.search(r"<title>([A-Za-z0-9\s\-]+)</title>", body)
                    if title_match:
                        model = title_match.group(1).replace("LuCI", "").strip() or "Antminer"
                    return {
                        "ip": ip,
                        "mac": "دریافت نشد",
                        "name": f"Antminer_{ip.split('.')[-1]}",
                        "model": model,
                        "brand": "Antminer",
                        "source": "Port 80 (HTTP)"
                    }
                elif "whatsminer" in body_lower:
                    return {
                        "ip": ip,
                        "mac": "دریافت نشد",
                        "name": f"WhatsMiner_{ip.split('.')[-1]}",
                        "model": "WhatsMiner",
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
