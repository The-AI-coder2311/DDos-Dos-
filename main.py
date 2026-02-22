# Safe Minecraft Proxy Latency Monitor (with Direct Fallback)
# Requires: pip install mcstatus PySocks

import random
import time
import logging
import socks
import socket
from mcstatus import JavaServer
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, stdev
from colorama import Fore

print(Fore.RED+" _____ __     __ ___  _          ____   ____    ___   ____  ")
print(Fore.RED+"|  ___|\ \   / /|_ _|| |        |  _ \ |  _ \  / _ \ / ___| ")
print(Fore.RED+"| |__   \ \ / /  | | | |        | | | || | | || | | |\___ \ ")
print(Fore.RED+"|  __|   \ V /   | | | |___     | |_| || |_| || |_| | ___) |")
print(Fore.RED+"| |___    \_/   |___||_____|    |____/ |____/  \___/ |____/ ")
print(Fore.RED+"|_____|         ")
print(Fore.RED+""+Fore.RESET)
print("/n")
print("/n")
print(Fore.GREEN+"@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
print(Fore.GREEN+"@@@@@@@@@@@@@@@@@@@%@@@@@@@%%%%%#####%%%%%%%%%@%@@@@@%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@")
print(Fore.GREEN+"@@@@@%@@%@@@@@@@@@@@@@@@@%%%+=-::------==*%%%%%@%%%%%#*+====++#%%%%@@@@@@@@@@@@@@@@")
print(Fore.GREEN+"@@@%@@@@@@@@@@@@@@%@@@%%%*-:----=========---+%%%%*=----======---+%%%%@@@@@@@@@@@@%@")
print(Fore.GREEN+"@@@@@%%@%@%@@@@@@@@@%%%*-----===============--==--==============--*%%@@@@@@@@@@@%@@")
print(Fore.GREEN+"@@@@@@@@@@@@@@@@@%@%%%=:---===================-:-=================:#%%@@@@@@@@@@@@@")
print(Fore.GREEN+"@@@@@@%@@@@@@@@@@@%%#:----======-----------=====:-=================:%%@@@@@@@@@@@@%")
print(Fore.GREEN+"@%@@@@@@%@@%@@@@@%%*:---=====-----========-----=-:======------=====-+%%%@@@@@@@@%@@")
print(Fore.GREEN+"@@@@@@@@@@@@@@@@@%*:---====---================---:------------------:+#%%%@@%@@@@@@")
print(Fore.GREEN+"@@%@@@@@@@@@@@%%%*:---===========================---==================--=+%%%@@@@@@")
print(Fore.GREEN+"@@@@@@@@@@@@%%%%#:----================-------------:--======---------------#%%%@@%@")
print(Fore.GREEN+"@@@@@@%@@%%%%+-:...::-============------------------------------------------=*%%%%@")
print(Fore.GREEN+"@@@@@@@@@%%*. ..:::.. .:-======-------:-===+++++=---------------=----==-----:.-==#%")
print(Fore.GREEN+"@@@@@%@@@%%+.:-:-----:...:-=----=--:=+*=-=.  :*#**=-..........-=.-.  .-=-:...... =%")
print(Fore.GREEN+"@@@@@%@@%%+:---:---====-:. .::::.:.-=-:..:............. .-- ..............       -%")
print(Fore.GREEN+"@@@@@@@%%=-----:---======-... ...............           =%+ ...                  -%")
print(Fore.GREEN+"@@@@@@%%=---------========---...                       :%%%.                    .#%")
print(Fore.GREEN+"@@@@@%%*:--------============:                        .-*#%#:                  :*%%")
print(Fore.GREEN+"@@@@@%%:---------============-.                      :-:-----:.              :+%%%%")
print(Fore.GREEN+"@@@@%%+:--------==============-:.                  .:--=======--::.........=*%%%%%@")
print(Fore.GREEN+"@@@@%%---------=================--::............:::-================------#%%%%%@@@")
print(Fore.GREEN+"@@@@%%:--------======================----------:--=======-----===----:-=#%%%%@@@@@%")
print(Fore.GREEN+"@@@@%*:-------===========================------============--:::-------=#%%@@@@@@@@")
print(Fore.GREEN+"@@@%%=--------==========================---===================--=======--+%%@%@@@@@")
print(Fore.GREEN+"@@@%%---------==============---==========================================-+%%%@@@@@")
print(Fore.GREEN+"@@%%%--------=============-::::::-========================================:#%%@@@@@")
print(Fore.GREEN+"@@%%-.:------============-:------::--=====================================-=%%@@@%@")
print(Fore.GREEN+"@%%#.....----============:---::-----::--==================================-:#%%@@@@")
print(Fore.GREEN+"@@%#......:--============-:---::::-----::::----=======================--:::-:#%%@@@")
print(Fore.GREEN+"@@%*........:-============-:-----:::::-------::::::::::::::::-:::::::::-----:%%%@@@")
print(Fore.GREEN+"@@%=..........:-============:::------:::::::::---------------------------::=%%%@@@@")
print(Fore.GREEN+"@%%:.............::-==========-::::---------::::::::::::::::::::::::::::::%%%%@@@@@")
print(Fore.GREEN+"@%#..................::--========----:::::-------------------------------:#%%%@@@@@")
print(Fore.GREEN+"%%=.......................::--==========-----::::::::::---------------::=#%%@@@@@@@")
print(Fore.GREEN+"%%:.............................::--===============---------------::+*#%%%%%@@@@%@@")
print(Fore.GREEN+"%%....................................::---=====================-:.-*#%%%%%%%@@@@@@")
print(Fore.GREEN+"%%..........................................:===============--:.......:-+#%%%%@@@@%")
print(Fore.GREEN+"%%..........................................:==========--::................-+#%%@@@")
print(Fore.GREEN+"%%:........................................:=-----:::::......................=%%%@@")
print(Fore.GREEN+"%%*........................................::::::----:....................-*%%%%%@@")
print(Fore.GREEN+"%%%=......................................---------:.....................*%%%%%%@@@")
print(Fore.GREEN+"@%%%+..................................................................:%%%%%%%%@@@")
print(Fore.GREEN+"@@%%%%*-..............................................................:%%%%%%%%%%@@")
print(Fore.GREEN+"@@@%%%%%#+-..........................................................-%%%%@%%%%%@@@")
print(Fore.GREEN+"@@@@@%%%%%%%*=:..............................................:=+===+*%%%%@%@@@@@@@@")
print(Fore.GREEN+"@@@@@@@@%%%%%%%#+=:.....................................:-=*#%%%%%%%%%%@@@@@@@@@@@@")
print(Fore.GREEN+"@@@@@@@@@@@%%%%%%%%#*=-...............:::::::---===++*#%%%%%%%%%%%%%%%%@@@@@@@%@%@%")
print(Fore.GREEN+"@@@@@@%@@@@@@@@%%%%%%%%%#*+==-::.....=%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@%@@@@%@@@@")
print(Fore.GREEN+"@@@@@@@@@@@%@@@@%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@")
print(Fore.GREEN+"@%@@@@%@@@@@@@@@@@@@@@@@@@@%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@%@@@@@@@%@@@@%@@@@@@%@%@@@")
print(Fore.GREEN+"")

print(Fore.RED + "Code By Someone -2026/2/21")
print("Version 1.2 \n")



# ---------------- USER CONFIG ----------------
TARGET_SERVER = input("Minecraft server (e.g., play.example.com): ").strip() or "example.com"
MAX_WORKERS   = int(input("Threads (suggested 5–100): ") or 20)
NUM_PROXIES   = int(input("Proxies per round (default 20 max is 50): ") or 20)
PING_ATTEMPTS = int(input("Pings per proxy (default 5): ") or 5)
PING_RATE     = float(input("Delay between pings [s] (default 2): ") or 2.0)
ROUND_DELAY   = float(input("Delay between rounds [s] (default 10): ") or 10.0)
TIMEOUT       = 5  # seconds for proxy connection timeout
SAVE_FILE     = "working_proxies.txt"
# ------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# --- 50 proxies from your list ---
PROXIES = [
    "31.42.6.125:5678", "31.43.33.55:4153", "31.43.63.70:4145", "34.101.184.164:3128",
    "35.206.88.200:8888", "36.92.81.181:4145", "37.59.98.31:9050", "38.127.172.18:11537",
    "43.130.6.42:80", "45.136.25.23:8085", "46.4.75.218:20000", "47.243.207.3:33967",
    "49.12.20.48:40000", "51.38.191.230:80", "64.227.108.25:31908", "68.183.207.140:80",
    "72.195.101.99:4145", "76.223.21.152:8080", "79.141.160.2:48462", "81.12.157.98:5678",
    "84.252.75.135:1111", "85.214.204.79:80", "87.121.77.130:4145", "88.213.214.254:4145",
    "89.116.191.51:80", "91.107.148.58:53967", "91.121.63.160:40831", "91.150.189.122:60647",
    "91.192.25.158:4145", "91.217.76.97:1080", "91.218.244.153:8989", "91.229.23.180:12273",
    "91.245.224.37:8443", "91.247.163.124:8085", "92.119.74.249:5678", "93.177.94.82:8085",
    "94.130.171.189:10004", "94.130.184.102:10015", "95.140.124.173:1080", "95.161.188.246:61537",
    "97.213.76.123:80", "98.162.25.4:31654", "98.162.25.7:31653", "98.170.57.231:4145",
    "98.170.57.249:4145", "98.175.31.222:4145", "98.178.72.21:10919", "98.181.137.83:4145",
    "98.188.47.150:4145", "99.86.63.31:443", "108.181.33.135:443"
]

def pick_random_proxies(n):
    return random.sample(PROXIES, min(n, len(PROXIES)))

def ping_direct():
    """Ping Minecraft server directly (no proxy)."""
    try:
        socket.socket = socket._socketobject if hasattr(socket, "_socketobject") else socket.socket
        server = JavaServer.lookup(TARGET_SERVER)
        latency = server.ping()
        return latency
    except Exception:
        return None

def test_proxy(proxy_id, ip, port):
    """Ping through proxy; if it fails, automatically switch to local direct ping."""
    results = []
    success = False
    try:
        socks.setdefaultproxy(socks.SOCKS5, ip, int(port))
        socket.socket = socks.socksocket
        socket.setdefaulttimeout(TIMEOUT)
        server = JavaServer.lookup(TARGET_SERVER)

        for attempt in range(1, PING_ATTEMPTS + 1):
            try:
                latency = server.ping()
                results.append(latency)
                success = True
                logging.info(f"[Proxy {proxy_id}] {ip}:{port} → Ping {attempt}/{PING_ATTEMPTS}: {round(latency,1)} ms")
            except Exception as e:
                logging.warning(f"[Proxy {proxy_id}] {ip}:{port} failed → {e}")
                break
            time.sleep(PING_RATE)

        # if proxy worked
        if success:
            avg = mean(results)
            spread = stdev(results) if len(results) > 1 else 0
            logging.info(f"[Proxy {proxy_id}] {ip}:{port} avg {round(avg,1)} ms ± {round(spread,1)} ms")
            return (ip, port, round(avg, 1))

    except Exception as e:
        logging.warning(f"[Proxy {proxy_id}] {ip}:{port} setup failed → {e}")

    # --- fallback to direct ping automatically ---
    direct_latency = ping_direct()
    if direct_latency:
        logging.info(f"[Proxy {proxy_id}] Proxy failed — direct ping used: {round(direct_latency,1)} ms")
        return ("LOCAL", 0, round(direct_latency,1))
    else:
        logging.warning(f"[Proxy {proxy_id}] Both proxy and direct ping failed.")
        return None

def save_working_proxies(results):
    if not results:
        return
    with open(SAVE_FILE, "a", encoding="utf8") as f:
        for ip, port, latency in results:
            f.write(f"{ip}:{port} → {latency} ms\n")
    logging.info(f"Saved {len(results)} working proxies to {SAVE_FILE}")

def run_round(round_num):
    selected = pick_random_proxies(NUM_PROXIES)
    logging.info(f"--- Round {round_num}: Testing {len(selected)} proxies ---")

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(test_proxy, i + 1, ip, port)
            for i, (ip, port) in enumerate(p.split(":") for p in selected)
        ]
        for f in as_completed(futures):
            r = f.result()
            if r:
                results.append(r)

    if results:
        results.sort(key=lambda x: x[2])
        logging.info("Working proxies this round:")
        for ip, port, latency in results[:10]:
            logging.info(f"  {ip}:{port} → {latency} ms")
        save_working_proxies(results)
    else:
        logging.info("No working proxies found this round.")

def main():
    round_num = 1
    try:
        while True:
            run_round(round_num)
            round_num += 1
            logging.info(f"Waiting {ROUND_DELAY}s before next round...\n")
            time.sleep(ROUND_DELAY)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected — exiting safely.")

if __name__ == "__main__":
    main()
