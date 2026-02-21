#!/usr/bin/env python3
"""ComfyUI multi-server load balancer.

Usage:
    python scripts/comfyui_server.py status   # show all server statuses
    python scripts/comfyui_server.py best     # print the least-loaded server URL
"""

import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVERS = [
    "http://wright.gazelle-galaxy.ts.net:8188",
    "http://wright.gazelle-galaxy.ts.net:8199",
    "http://neumann.gazelle-galaxy.ts.net:8188",
    "http://neumann.gazelle-galaxy.ts.net:8199",
]

TIMEOUT = 3  # seconds


def check_server(url):
    """Check a single server's queue status via /queue API."""
    try:
        req = urllib.request.Request(f"{url}/queue")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        running = len(data.get("queue_running", []))
        pending = len(data.get("queue_pending", []))
        return {
            "url": url,
            "online": True,
            "running": running,
            "pending": pending,
            "load": running + pending,
        }
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return {"url": url, "online": False, "running": 0, "pending": 0, "load": float("inf")}


def check_all_servers():
    """Check all servers in parallel, return list sorted by load."""
    results = []
    with ThreadPoolExecutor(max_workers=len(SERVERS)) as pool:
        futures = {pool.submit(check_server, url): url for url in SERVERS}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda s: (not s["online"], s["load"]))
    return results


def get_best_server():
    """Return the URL of the least-loaded online server, or None."""
    for server in check_all_servers():
        if server["online"]:
            return server["url"]
    return None


def submit_prompt(workflow):
    """Submit a workflow to the best available server. Returns (url, response_data) or raises."""
    url = get_best_server()
    if url is None:
        raise RuntimeError("No ComfyUI servers available")
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{url}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return url, json.loads(resp.read())


def print_status():
    """Print a formatted status table of all servers."""
    servers = check_all_servers()
    print(f"{'Server':<50} {'Status':<10} {'Running':<10} {'Pending':<10} {'Load':<6}")
    print("-" * 86)
    for s in servers:
        status = "online" if s["online"] else "OFFLINE"
        load = str(s["load"]) if s["online"] else "-"
        running = str(s["running"]) if s["online"] else "-"
        pending = str(s["pending"]) if s["online"] else "-"
        print(f"{s['url']:<50} {status:<10} {running:<10} {pending:<10} {load:<6}")


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "status":
        print_status()
    elif cmd == "best":
        url = get_best_server()
        if url:
            print(url)
        else:
            print("No servers available", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
