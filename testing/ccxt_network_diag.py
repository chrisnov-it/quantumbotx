#!/usr/bin/env python3
"""Network diagnostics for Binance Spot/Futures demo endpoints.

Usage:
  .venv/bin/python testing/ccxt_network_diag.py
"""

from __future__ import annotations

import argparse
import shutil
import socket
import ssl
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from datetime import datetime, timezone


DOMAINS = [
    "demo-fapi.binance.com",
    "testnet.binance.vision",
    "api.binance.com",
]

URLS = [
    "https://demo-fapi.binance.com/fapi/v1/ping",
    "https://demo-fapi.binance.com/fapi/v1/time",
    "https://testnet.binance.vision/api/v3/ping",
    "https://testnet.binance.vision/api/v3/time",
    "https://api.binance.com/api/v3/ping",
]

PUBLIC_DNS = ["1.1.1.1", "8.8.8.8"]
SUSPICIOUS_KEYWORDS = ["internetpositif.id", "nxdomain", "blocked", "forbidden"]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def run_cmd(cmd: list[str], timeout: int = 8) -> tuple[int, str, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return res.returncode, (res.stdout or "").strip(), (res.stderr or "").strip()
    except Exception as exc:
        return 99, "", str(exc)


def system_dns_lookup(domain: str) -> list[str]:
    ips = set()
    try:
        infos = socket.getaddrinfo(domain, 443, type=socket.SOCK_STREAM)
        for info in infos:
            ips.add(info[4][0])
    except Exception:
        return []
    return sorted(ips)


def nslookup(domain: str, resolver: str | None = None) -> str:
    if not shutil.which("nslookup"):
        return "nslookup not available"
    cmd = ["nslookup", domain] + ([resolver] if resolver else [])
    _, out, err = run_cmd(cmd)
    if out:
        return out
    return err or "no output"


def tcp_check(host: str, port: int = 443, timeout: int = 5) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "OK"
    except Exception as exc:
        return f"FAIL: {exc}"


def tls_check(host: str, port: int = 443, timeout: int = 5) -> str:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                subject = cert.get("subject", ())
                cn = "?"
                for field in subject:
                    for key, val in field:
                        if key == "commonName":
                            cn = val
                return f"OK (CN={cn}, TLS={tls.version()})"
    except Exception as exc:
        return f"FAIL: {exc}"


def http_check(url: str, timeout: int = 8) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ccxt-network-diag/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(200).decode("utf-8", errors="replace").strip()
            return f"HTTP {resp.status} body={body}"
    except urllib.error.HTTPError as exc:
        body = exc.read(200).decode("utf-8", errors="replace").strip()
        return f"HTTP {exc.code} body={body}"
    except Exception as exc:
        return f"FAIL: {exc}"


def suspicious(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in SUSPICIOUS_KEYWORDS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Binance demo endpoint connectivity/DNS issues")
    parser.add_argument("--timeout", type=int, default=8, help="HTTP command timeout in seconds")
    args = parser.parse_args()

    print("CCXT Network Diagnostics")
    print(f"Timestamp : {now_utc()}")
    print(f"Python    : {sys.version.split()[0]}")
    print(f"Timeout   : {args.timeout}s")

    print_header("DNS Resolution")
    for domain in DOMAINS:
        print(f"\n- Domain: {domain}")
        ips = system_dns_lookup(domain)
        print(f"  socket.getaddrinfo: {ips if ips else 'FAILED'}")

        out_default = nslookup(domain)
        flag_default = " [SUSPICIOUS]" if suspicious(out_default) else ""
        print("  nslookup(default):")
        print(textwrap.indent(out_default, "    ") + flag_default)

        for resolver in PUBLIC_DNS:
            out = nslookup(domain, resolver=resolver)
            flag = " [SUSPICIOUS]" if suspicious(out) else ""
            print(f"  nslookup({resolver}):")
            print(textwrap.indent(out, "    ") + flag)

    print_header("TCP/TLS")
    for domain in DOMAINS:
        print(f"- {domain}:443")
        print(f"  TCP: {tcp_check(domain, 443)}")
        print(f"  TLS: {tls_check(domain, 443)}")

    print_header("HTTP API Checks")
    for url in URLS:
        result = http_check(url, timeout=args.timeout)
        flag = " [SUSPICIOUS]" if suspicious(result) else ""
        print(f"- {url}")
        print(f"  {result}{flag}")

    print_header("Interpretation Tips")
    print(
        textwrap.dedent(
            """
            - Jika DNS mengarah ke domain lain (mis. internetpositif.id), ini DNS interception/filtering.
            - Jika TCP/TLS fail tapi DNS normal, kemungkinan blokir jaringan/firewall.
            - Jalankan ulang script ini setelah VPN aktif untuk membandingkan hasil.
            """
        ).strip()
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
