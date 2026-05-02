"""Print Buffer profile IDs for the configured access token.

Hits Buffer's /profiles endpoint and prints one line per profile so you
can copy the ones you want into the BUFFER_PROFILE_IDS secret.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if not token:
        print("BUFFER_ACCESS_TOKEN must be set", file=sys.stderr)
        return 1

    url = f"https://api.bufferapp.com/1/profiles.json?access_token={token}"
    with urllib.request.urlopen(url) as resp:
        profiles = json.loads(resp.read().decode("utf-8"))

    if not isinstance(profiles, list) or not profiles:
        print("No profiles returned. Check token scope and Buffer plan.", file=sys.stderr)
        return 1

    print(f"Found {len(profiles)} Buffer profile(s):\n")
    print(f"{'service':<12} {'username':<30} id")
    print("-" * 70)
    for p in profiles:
        service = p.get("service", "?")
        username = p.get("formatted_username") or p.get("service_username") or "?"
        pid = p.get("id", "?")
        print(f"{service:<12} {username:<30} {pid}")

    print("\nCopy the ids you want, comma-separated, into the BUFFER_PROFILE_IDS secret.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
