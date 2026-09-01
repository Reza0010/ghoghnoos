"""
FixBoard Miner Manager - CGMiner TCP Socket Interface
Handles low-level TCP socket communication with Antminer and WhatsMiner CGMiner-based APIs on Port 4028.
"""

import socket
import json
from typing import Optional, Dict, Union

class CGMinerAPI:
    def __init__(self, ip: str, port: int = 4028, timeout: float = 4.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def send_command(self, command: str, parameter: Optional[str] = None) -> Optional[dict]:
        """
        Sends a command via TCP socket in CGMiner JSON format and parses the response.
        """
        payload = {"command": command}
        if parameter is not None:
            payload["parameter"] = parameter

        payload_str = json.dumps(payload)

        try:
            # Create a socket connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.ip, self.port))

                # Send payload
                s.sendall(payload_str.encode("utf-8"))

                # Receive response until socket is closed by the miner
                response_data = []
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response_data.append(chunk)

                full_response = b"".join(response_data).decode("utf-8", errors="ignore")

                # Clean up any potential garbage characters before/after JSON (e.g. null bytes)
                full_response = full_response.strip().replace("\x00", "")

                if not full_response:
                    return None

                # Parse JSON
                try:
                    return json.loads(full_response)
                except json.JSONDecodeError:
                    # Some older cgminer devices might respond with pipe-separated text or invalid JSON
                    # Let's try parsing custom text responses or return None
                    return {"raw_text": full_response}

        except (socket.timeout, socket.error) as e:
            # Silent logging to prevent UI console spamming, can be handled by the caller
            return None

    def get_summary(self) -> Optional[dict]:
        """Retrieves high-level summary information."""
        return self.send_command("summary")

    def get_stats(self) -> Optional[dict]:
        """Retrieves hardware and sensor statistics."""
        return self.send_command("stats")

    def get_pools(self) -> Optional[dict]:
        """Retrieves pool configurations and statistics."""
        return self.send_command("pools")

    def get_devs(self) -> Optional[dict]:
        """Retrieves device (hash board) statistics."""
        return self.send_command("devs")

    def get_version(self) -> Optional[dict]:
        """Retrieves miner API/firmware version."""
        return self.send_command("version")

    # Privileged write commands (requires API configuration access on Port 4028)
    def reboot(self) -> bool:
        """Triggers system reboot."""
        res = self.send_command("reboot")
        return self._is_success(res)

    def restart_mining(self) -> bool:
        """Restarts the mining process."""
        res = self.send_command("restart")
        return self._is_success(res)

    def add_pool(self, url: str, worker: str, password: str) -> bool:
        """Adds a new pool configuration."""
        param = f"{url},{worker},{password}"
        res = self.send_command("addpool", param)
        return self._is_success(res)

    def switch_pool(self, pool_id: int) -> bool:
        """Switches the active pool."""
        res = self.send_command("switchpool", str(pool_id))
        return self._is_success(res)

    def remove_pool(self, pool_id: int) -> bool:
        """Removes a pool configuration."""
        res = self.send_command("removepool", str(pool_id))
        return self._is_success(res)

    def _is_success(self, response: Optional[dict]) -> bool:
        """Helper to determine if a write command was successful."""
        if not response:
            return False
        # Typically returns: {"STATUS": [{"STATUS": "S", "Msg": "..."}]} or similar. 'S' is Success.
        status_list = response.get("STATUS", [])
        if status_list and isinstance(status_list, list):
            status_code = status_list[0].get("STATUS", "")
            return status_code in ("S", "I", "W")  # Success, Info, Warning
        return False
