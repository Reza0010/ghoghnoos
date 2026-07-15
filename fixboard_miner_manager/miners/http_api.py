"""
FixBoard Miner Manager - HTTP / CGI API Fallback Client
Handles HTTP/CGI requests to miner web dashboard endpoints with Basic Authentication.
"""

import urllib.request
import urllib.parse
import json
import base64
from typing import Optional, Tuple, Dict

class HTTPFallbackAPI:
    def __init__(self, ip: str, username: str = "root", password: str = "root", use_https: bool = False, timeout: float = 5.0):
        self.ip = ip
        self.username = username
        self.password = password
        self.scheme = "https" if use_https else "http"
        self.base_url = f"{self.scheme}://{self.ip}"
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        """Generates headers including basic authorization and standard browser user-agent."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        if self.username and self.password:
            auth_str = f"{self.username}:{self.password}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {auth_b64}"
        return headers

    def send_request(self, endpoint: str, data: Optional[dict] = None, method: str = "GET") -> Tuple[bool, str]:
        """
        Sends an HTTP/HTTPS request to the miner's CGI/Web control panel.
        Returns a tuple (success, response_body_text)
        """
        url = f"{self.base_url}{endpoint}"
        req_data = None

        if data is not None:
            # Send as JSON by default or form-urlencoded
            req_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=req_data, method=method)

        # Apply standard authorization and agent headers
        for k, v in self._get_headers().items():
            req.add_header(k, v)

        if data is not None:
            req.add_header("Content-Type", "application/json")

        try:
            # We bypass SSL verification for local self-signed miner certificates
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                body = response.read().decode("utf-8", errors="ignore")
                return True, body
        except Exception as e:
            return False, f"HTTP Request failed: {str(e)}"

    def get_cgi_status(self) -> Optional[dict]:
        """Fetches status data from common CGI endpoints like /cgi-bin/get_status.cgi."""
        success, body = self.send_request("/cgi-bin/get_status.cgi")
        if success:
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                pass
        return None

    def reboot(self) -> bool:
        """Sends reboot post request to Web endpoint."""
        success, _ = self.send_request("/cgi-bin/reboot.cgi", method="POST")
        if not success:
            # Antminer Luci reboot endpoint
            success, _ = self.send_request("/cgi-bin/luci/admin/system/reboot", method="POST")
        return success
