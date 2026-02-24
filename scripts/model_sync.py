#!/usr/bin/env python3
"""ComfyUI model sync — keep servers in sync with models.yaml manifest.

Usage:
    python scripts/model_sync.py status   # Show installed models per server
    python scripts/model_sync.py diff     # Show missing models per server
    python scripts/model_sync.py sync     # Download missing models via SSH+wget
    python scripts/model_sync.py orphans  # Show models not in manifest
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

# ─── Configuration ──────────────────────────────────────────────────────────

SERVERS = {
    "wright-a": "wright.gazelle-galaxy.ts.net:8188",
    "wright-b": "wright.gazelle-galaxy.ts.net:8189",
    "neumann-a": "neumann.gazelle-galaxy.ts.net:8188",
    "neumann-b": "neumann.gazelle-galaxy.ts.net:8189",
}

# SSH host → ComfyUI models root (a/b share the same filesystem)
SSH_HOSTS = {
    "wright": "wright.gazelle-galaxy.ts.net",
    "neumann": "neumann.gazelle-galaxy.ts.net",
}
COMFYUI_ROOT = "~/codegit/ComfyUI/models"

# Manifest category → ComfyUI subdirectory
CATEGORY_DIRS = {
    "diffusion_models": "diffusion_models",
    "checkpoints": "checkpoints",
    "text_encoders": "text_encoders",
    "vae": "vae",
    "clip_vision": "clip_vision",
    "loras": "loras",
    "controlnet": "controlnet",
    "upscale_models": "upscale_models",
}

MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.yaml")


# ─── Helpers ────────────────────────────────────────────────────────────────


def load_manifest():
    """Load models.yaml and return {category: [model_entries]}.

    Parses a simple subset of YAML: top-level keys mapping to lists of dicts
    with scalar string/number values. No external dependency needed.
    """
    manifest = {}
    current_category = None
    current_item = None

    with open(MANIFEST_PATH) as f:
        for line in f:
            stripped = line.rstrip()

            # Skip empty lines and comments
            if not stripped or stripped.lstrip().startswith("#"):
                continue

            # Top-level category (no leading whitespace, ends with colon)
            if not line[0].isspace() and stripped.endswith(":"):
                current_category = stripped[:-1]
                manifest[current_category] = []
                current_item = None
                continue

            # List item start: "  - key: value"
            m = re.match(r"^\s+-\s+(\w+):\s+(.+)$", stripped)
            if m:
                current_item = {m.group(1): _parse_value(m.group(2))}
                if current_category:
                    manifest[current_category].append(current_item)
                continue

            # Continuation key: "    key: value"
            m = re.match(r"^\s+(\w+):\s+(.+)$", stripped)
            if m and current_item is not None:
                current_item[m.group(1)] = _parse_value(m.group(2))

    return manifest


def _parse_value(s):
    """Parse a YAML scalar value (string or number)."""
    # Try number
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def get_server_models(server_url):
    """Query ComfyUI /object_info to get available model filenames per category."""
    # Use the simpler /models endpoint per category
    installed = {}
    for category, subdir in CATEGORY_DIRS.items():
        try:
            url = f"http://{server_url}/models/{subdir}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                files = json.loads(resp.read())
            installed[category] = set(files) if isinstance(files, list) else set()
        except Exception:
            installed[category] = set()
    return installed


def get_ssh_host(server_name):
    """Map server name (wright-a, neumann-b) to SSH host key."""
    return server_name.split("-")[0]


def ssh_list_models(ssh_host, subdir):
    """List model files on a server via SSH."""
    host = SSH_HOSTS[ssh_host]
    cmd = f"ls {COMFYUI_ROOT}/{subdir}/ 2>/dev/null"
    try:
        result = subprocess.run(
            ["ssh", host, cmd],
            capture_output=True, text=True, timeout=10,
        )
        return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except Exception:
        return set()


def ssh_download(ssh_host, subdir, filename, url):
    """Download a model to server via SSH + wget."""
    host = SSH_HOSTS[ssh_host]
    target = f"{COMFYUI_ROOT}/{subdir}/{filename}"
    tmp = f"{target}.tmp"
    cmd = f"wget -q '{url}' -O '{tmp}' && mv '{tmp}' '{target}'"
    print(f"    Downloading {filename} to {ssh_host}...")
    result = subprocess.run(
        ["ssh", host, cmd],
        capture_output=True, text=True, timeout=7200,
    )
    if result.returncode != 0:
        print(f"    FAILED: {result.stderr.strip()}")
        return False
    print(f"    Done: {filename}")
    return True


# ─── Commands ───────────────────────────────────────────────────────────────


def cmd_status():
    """Show installed models per server."""
    # Deduplicate: a/b share filesystem, just check one per host
    for host_key in SSH_HOSTS:
        server_name = f"{host_key}-a"
        server_url = SERVERS[server_name]
        print(f"\n{'='*60}")
        print(f"  {host_key} ({server_url})")
        print(f"{'='*60}")

        installed = get_server_models(server_url)
        for category in CATEGORY_DIRS:
            files = sorted(installed.get(category, set()))
            if files:
                print(f"\n  {category}/")
                for f in files:
                    print(f"    {f}")
            else:
                print(f"\n  {category}/  (empty or unreachable)")


def cmd_diff():
    """Show models in manifest but missing from servers."""
    manifest = load_manifest()
    any_missing = False

    for host_key in SSH_HOSTS:
        server_name = f"{host_key}-a"
        server_url = SERVERS[server_name]
        print(f"\n{'='*60}")
        print(f"  {host_key} — missing models")
        print(f"{'='*60}")

        installed = get_server_models(server_url)
        host_missing = False

        for category, models in manifest.items():
            if category not in CATEGORY_DIRS or not models:
                continue
            server_files = installed.get(category, set())
            for model in models:
                if model["name"] not in server_files:
                    print(f"  [-] {category}/{model['name']}  ({model.get('size_gb', '?')} GB)")
                    host_missing = True
                    any_missing = True

        if not host_missing:
            print("  All models present.")

    if not any_missing:
        print("\nAll servers in sync with manifest.")


def cmd_sync():
    """Download missing models to servers via SSH."""
    manifest = load_manifest()

    for host_key in SSH_HOSTS:
        server_name = f"{host_key}-a"
        server_url = SERVERS[server_name]
        print(f"\n{'='*60}")
        print(f"  Syncing {host_key}")
        print(f"{'='*60}")

        installed = get_server_models(server_url)
        to_download = []

        for category, models in manifest.items():
            if category not in CATEGORY_DIRS or not models:
                continue
            subdir = CATEGORY_DIRS[category]
            server_files = installed.get(category, set())
            for model in models:
                if model["name"] not in server_files:
                    to_download.append((subdir, model["name"], model["url"], model.get("size_gb", 0)))

        if not to_download:
            print("  Already in sync.")
            continue

        total_gb = sum(m[3] for m in to_download)
        print(f"  {len(to_download)} models to download ({total_gb:.1f} GB total)")
        for subdir, name, url, size_gb in to_download:
            print(f"  [+] {subdir}/{name}  ({size_gb} GB)")

        confirm = input(f"\n  Proceed with download to {host_key}? [y/N] ").strip().lower()
        if confirm != "y":
            print("  Skipped.")
            continue

        for subdir, name, url, _ in to_download:
            ssh_download(host_key, subdir, name, url)


def cmd_orphans():
    """Show models on servers that are not in manifest."""
    manifest = load_manifest()

    # Build set of expected filenames per category
    expected = {}
    for category, models in manifest.items():
        if category not in CATEGORY_DIRS or not models:
            continue
        expected[category] = {m["name"] for m in models}

    for host_key in SSH_HOSTS:
        server_name = f"{host_key}-a"
        server_url = SERVERS[server_name]
        print(f"\n{'='*60}")
        print(f"  {host_key} — orphan models (not in manifest)")
        print(f"{'='*60}")

        installed = get_server_models(server_url)
        host_orphans = False

        for category in CATEGORY_DIRS:
            server_files = installed.get(category, set())
            manifest_files = expected.get(category, set())
            orphans = sorted(server_files - manifest_files)
            for f in orphans:
                print(f"  [?] {category}/{f}")
                host_orphans = True

        if not host_orphans:
            print("  No orphans.")


# ─── Main ───────────────────────────────────────────────────────────────────

COMMANDS = {
    "status": cmd_status,
    "diff": cmd_diff,
    "sync": cmd_sync,
    "orphans": cmd_orphans,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python scripts/model_sync.py <command>")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
