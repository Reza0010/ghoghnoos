"""
FixBoard Miner Manager - Import and Verification Tests
Verifies that all written packages and PySide6 GUI components can be imported without any errors.
"""

import sys
import os

# Set project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("[TEST] Running import tests...")

    try:
        from database.db_manager import DatabaseManager
        print("✅ database/db_manager.py imported successfully")

        from utils.helpers import parse_ip_range, format_hashrate, format_uptime
        print("✅ utils/helpers.py imported successfully")

        from miners.cgminer_api import CGMinerAPI
        print("✅ miners/cgminer_api.py imported successfully")

        from miners.whatsminer_api import WhatsMinerSecureAPI
        print("✅ miners/whatsminer_api.py imported successfully")

        from miners.ssh_api import SSHFallbackAPI
        print("✅ miners/ssh_api.py imported successfully")

        from miners.http_api import HTTPFallbackAPI
        print("✅ miners/http_api.py imported successfully")

        from network.scanner import NetworkScanner
        print("✅ network/scanner.py imported successfully")

        # Test GUI widgets
        from gui.dashboard import DashboardWidget, KPICard, DynamicGraphWidget
        print("✅ gui/dashboard.py imported successfully")

        from gui.miner_table import MinerTableWidget
        print("✅ gui/miner_table.py imported successfully")

        from gui.login_dialog import LoginDialog
        print("✅ gui/login_dialog.py imported successfully")

        from gui.miner_details_dialog import MinerDetailsDialog
        print("✅ gui/miner_details_dialog.py imported successfully")

        from gui.group_actions import GroupActionsWidget
        print("✅ gui/group_actions.py imported successfully")

        from gui.main_window import MainWindow
        print("✅ gui/main_window.py imported successfully")

        print("\n🎉 ALL core and GUI components imported, compiled and validated successfully!")

    except Exception as e:
        print(f"\n❌ Import test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
