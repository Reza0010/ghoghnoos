"""
FixBoard Miner Manager - General Utility Helpers
Contains networking utilities, unit formatters, and range parsers.
"""

import re
import ipaddress
from typing import List

def validate_ip(ip_str: str) -> bool:
    """Validates if the provided string is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ip_str.strip())
        return True
    except ValueError:
        return False

def parse_ip_range(ip_range_str: str) -> List[str]:
    """
    Parses various IP input formats into a list of individual IP addresses.
    Supported formats:
      - Single IP: "192.168.1.10"
      - Dash-range: "192.168.1.1-254" or "192.168.1.50-100"
      - CIDR Block: "192.168.1.0/24"
      - Comma-separated combination of the above: "192.168.1.5, 192.168.1.10-15"
    """
    ips = []
    # Split by comma
    parts = [p.strip() for p in ip_range_str.split(",") if p.strip()]

    for part in parts:
        # Check for CIDR
        if "/" in part:
            try:
                network = ipaddress.IPv4Network(part, strict=False)
                # Skip network address and broadcast address for standard scanning
                hosts = list(network.hosts())
                if hosts:
                    for host in hosts:
                        ips.append(str(host))
                else:
                    ips.append(str(network.network_address))
            except ValueError:
                pass

        # Check for dash-range
        elif "-" in part:
            dash_match = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})-(\d{1,3})$", part)
            if dash_match:
                prefix = dash_match.group(1)
                start = int(dash_match.group(2))
                end = int(dash_match.group(3))
                if start <= end and start >= 0 and end <= 255:
                    for i in range(start, end + 1):
                        ips.append(f"{prefix}{i}")
            else:
                # Try generic dash range where the second part might be a full IP
                full_dash_match = re.match(r"^([\d\.]+)-([\d\.]+)$", part)
                if full_dash_match:
                    try:
                        start_ip = ipaddress.IPv4Address(full_dash_match.group(1))
                        end_ip = ipaddress.IPv4Address(full_dash_match.group(2))
                        if int(start_ip) <= int(end_ip):
                            curr = int(start_ip)
                            last = int(end_ip)
                            while curr <= last:
                                ips.append(str(ipaddress.IPv4Address(curr)))
                                curr += 1
                    except ValueError:
                        pass
        # Single IP
        else:
            if validate_ip(part):
                ips.append(part)

    # Deduplicate while preserving order
    seen = set()
    return [x for x in ips if not (x in seen or seen.add(x))]

def format_hashrate(hashrate_val: float, unit_from: str = "GH") -> str:
    """
    Formats raw hashrate to human-readable units.
    Miners often return hashrate in GH/s or MH/s or TH/s.
    """
    try:
        val = float(hashrate_val)
    except (ValueError, TypeError):
        return "دریافت نشد"

    # Normalize to GH/s first
    u = unit_from.upper()
    if u == "H":
        gh_val = val / 1_000_000_000.0
    elif u == "KH":
        gh_val = val / 1_000_000.0
    elif u == "MH":
        gh_val = val / 1000.0
    elif u == "TH":
        gh_val = val * 1000.0
    elif u == "PH":
        gh_val = val * 1_000_000.0
    else:  # Default is GH
        gh_val = val

    if gh_val >= 1_000_000.0:
        return f"{gh_val / 1_000_000.0:.2f} PH/s"
    elif gh_val >= 1000.0:
        return f"{gh_val / 1000.0:.2f} TH/s"
    elif gh_val >= 1.0:
        return f"{gh_val:.2f} GH/s"
    else:
        return f"{gh_val * 1000.0:.2f} MH/s"

def format_uptime(seconds_val) -> str:
    """Formats uptime in seconds into a localized Persian representation of D days, H:M:S."""
    try:
        total_seconds = int(float(seconds_val))
    except (ValueError, TypeError):
        return "دریافت نشد"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days} روز و {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
