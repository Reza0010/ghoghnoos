"""
FixBoard Miner Manager - SQLite Database Management Layer
Provides robust and thread-safe data persistence for miner credentials, settings, scan results, and audit trails.
"""

import sqlite3
import os
import threading
from typing import List, Dict, Tuple, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "miner_manager.db")

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.db_path = DB_FILE
        self._local = threading.local()
        self.init_db()
        self._initialized = True

    def _get_conn(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def init_db(self):
        """Initializes database schema and ensures all required tables exist."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Table to store individual miners
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS miners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT UNIQUE NOT NULL,
                mac TEXT,
                name TEXT,
                model TEXT,
                brand TEXT,
                username TEXT,
                password TEXT,
                is_online INTEGER DEFAULT 0,
                last_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table to store general settings as key-value pairs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Table to store audit trails of management operations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                target_ip TEXT,
                status TEXT NOT NULL,
                message TEXT
            )
        """)

        conn.commit()

    def add_or_update_miner(self, ip: str, mac: Optional[str] = None, name: Optional[str] = None,
                           model: Optional[str] = None, brand: Optional[str] = None,
                           is_online: int = 0) -> bool:
        """Inserts a discovered miner or updates its online status and last scan timestamp."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO miners (ip, mac, name, model, brand, is_online, last_scan)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(ip) DO UPDATE SET
                    mac = COALESCE(?, miners.mac),
                    name = COALESCE(?, miners.name),
                    model = COALESCE(?, miners.model),
                    brand = COALESCE(?, miners.brand),
                    is_online = ?,
                    last_scan = CURRENT_TIMESTAMP
            """, (ip, mac, name, model, brand, is_online, mac, name, model, brand, is_online))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] add_or_update_miner failed: {e}")
            return False

    def update_miner_credentials(self, ip: str, username: str, password: str) -> bool:
        """Updates Username and Password credentials for a specific miner."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE miners
                SET username = ?, password = ?
                WHERE ip = ?
            """, (username, password, ip))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] update_miner_credentials failed: {e}")
            return False

    def get_miner_credentials(self, ip: str) -> Tuple[Optional[str], Optional[str]]:
        """Returns the username and password for a given miner."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM miners WHERE ip = ?", (ip,))
        row = cursor.fetchone()
        if row:
            return row["username"], row["password"]
        return None, None

    def get_miner_by_ip(self, ip: str) -> Optional[dict]:
        """Returns a single miner detailed dictionary by IP."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM miners WHERE ip = ?", (ip,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_miners(self) -> List[dict]:
        """Returns list of all miners stored in the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM miners ORDER BY ip")
        return [dict(row) for row in cursor.fetchall()]

    def delete_miner(self, ip: str) -> bool:
        """Deletes a miner record from the database by IP."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM miners WHERE ip = ?", (ip,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] delete_miner failed: {e}")
            return False

    def set_setting(self, key: str, value: str) -> bool:
        """Saves a configuration setting as key-value pair."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            """, (key, value, value))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] set_setting failed: {e}")
            return False

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a configuration setting."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    def log_action(self, action_type: str, target_ip: Optional[str], status: str, message: Optional[str] = None) -> bool:
        """Logs a critical administrative or system event."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO audit_logs (action_type, target_ip, status, message)
                VALUES (?, ?, ?, ?)
            """, (action_type, target_ip, status, message))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] log_action failed: {e}")
            return False

    def get_audit_logs(self, limit: int = 100) -> List[dict]:
        """Returns the most recent action logs from the database."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
