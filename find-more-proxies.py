#!/usr/bin/env python3
"""
Fetch public SOCKS5 proxies from multiple sources and print them.
Optional --check mode verifies proxies by requesting https://httpbin.org/ip
"""

import argparse
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROXY_SOURCES = [
    "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&country=all",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}
TIMEOUT = 10
RETRIES = 2
MAX_WORKERS = 20
TEST_URL = "https://httpbin.org/ip"  # harmless test endpoint

def fetch_source(url):
    for attempt in range(1, RETRIES + 2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            lines = [ln.strip() for ln in r.text.splitlines() if ln.strip()]
            return lines
        except Exception as e:
            if attempt <= RETRIES:
                time.sleep(1 + attempt)
                continue
            print(f"[!] Failed to fetch {url}: {e}")
            return []

def fetch_all():
    all_lines = []
    for src in PROXY_SOURCES:
        print(f"Fetching: {src}")
        lines = fetch_source(src)
        print(f"  -> {len(lines)} entries")
        all_lines.extend(lines)
    unique = sorted(set(all_lines))
    print(f"\nTotal unique proxies fetched: {len(unique)}\n")
    return unique

def check_proxy(proxy):
    """
    proxy: "ip:port"
    returns (proxy, ok_bool, info)
    """
    proxies = {"http": f"socks5://{proxy}", "https": f"socks5://{proxy}"}
    try:
        r = requests.get(TEST_URL, proxies=proxies, timeout=8)
        if r.status_code == 200:
            # httpbin returns {"origin": "x.x.x.x"}
            origin = r.json().get("origin", "")
            return (proxy, True, origin)
        return (proxy, False, f"HTTP {r.status_code}")
    except Exception as e:
        return (proxy, False, str(e))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Verify proxies by requesting httpbin and print remote IP")
    ap.add_argument("--max-workers", type=int, default=MAX_WORKERS)
    args = ap.parse_args()

    proxies = fetch_all()
    if not proxies:
        print("No proxies found. Try running again or check your network/timeout.")
        return

    # print raw list
    print("Proxies (ip:port):")
    for p in proxies:
        print(p)

    if args.check:
        print("\nVerifying proxies (this may take a while)...\n")
        with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
            futures = {ex.submit(check_proxy, p): p for p in proxies}
            for fut in as_completed(futures):
                p = futures[fut]
                try:
                    proxy, ok, info = fut.result()
                    if ok:
                        print(f"[OK] {proxy} -> remote IP: {info}")
                    else:
                        print(f"[FAIL] {proxy} -> {info}")
                except Exception as e:
                    print(f"[ERR] {p} -> {e}")

if __name__ == "__main__":
    main()
