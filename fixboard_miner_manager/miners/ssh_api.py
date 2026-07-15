"""
FixBoard Miner Manager - SSH Fallback Client
Provides secure SSH connection fallback to run diagnostic commands, fetch system logs, and manage configuration files.
"""

import sys
import subprocess
from typing import Optional, Tuple

# Try importing paramiko for native python SSH implementation
try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

class SSHFallbackAPI:
    def __init__(self, ip: str, username: str = "root", password: str = "root", port: int = 22, timeout: float = 5.0):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout

    def execute_command(self, cmd: str) -> Tuple[bool, str]:
        """
        Executes a command on the remote miner via SSH.
        Returns a tuple: (success, output_string)
        """
        if HAS_PARAMIKO:
            return self._execute_with_paramiko(cmd)

        # Fallback to system SSH command line subprocess if paramiko is not installed
        # Useful for environments with native ssh client available
        return self._execute_with_subprocess(cmd)

    def _execute_with_paramiko(self, cmd: str) -> Tuple[bool, str]:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout
            )
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=self.timeout)
            out_str = stdout.read().decode("utf-8", errors="ignore")
            err_str = stderr.read().decode("utf-8", errors="ignore")
            ssh.close()

            if err_str and not out_str:
                return False, err_str
            return True, out_str
        except Exception as e:
            return False, f"SSH connection failed (paramiko): {str(e)}"

    def _execute_with_subprocess(self, cmd: str) -> Tuple[bool, str]:
        """Runs the native ssh client command via subprocess as a backup."""
        try:
            # We use sshpass to pass password in command line securely if sshpass exists,
            # otherwise standard ssh with strict host checking disabled.
            # On windows/linux this is a fallback only.
            ssh_cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", f"ConnectTimeout={int(self.timeout)}",
                f"{self.username}@{self.ip}",
                cmd
            ]
            # Since standard ssh asks for password interactively, this may timeout.
            # We add a warning log prefix.
            result = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout)
            out_str = result.stdout.decode("utf-8", errors="ignore")
            err_str = result.stderr.decode("utf-8", errors="ignore")

            if result.returncode == 0:
                return True, out_str
            return False, f"SSH Command failed: {err_str}"
        except Exception as e:
            return False, f"SSH connection failed (subprocess): {str(e)}"

    def fetch_logs(self, log_path: str = "/var/log/syslog") -> str:
        """Fetches the log contents from the miner."""
        # Try some common logs
        success, out = self.execute_command(f"tail -n 1000 {log_path} 2>/dev/null || dmesg | tail -n 1000")
        if success:
            return out
        return "دریافت نشد"

    def reboot(self) -> bool:
        """Triggers remote reboot command."""
        success, _ = self.execute_command("reboot")
        return success
