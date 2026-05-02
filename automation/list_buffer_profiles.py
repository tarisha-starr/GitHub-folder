"""List Buffer profile IDs for the configured access token.

Hits Buffer's /profiles endpoint and writes the result to
automation/buffer_profiles.json so the user (and Claude) can read the
IDs directly from the repo, no log inspection needed.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent / "buffer_profiles.json"


def fetch_profiles(token: str) -> list[dict]:
    url = f"https://api.bufferapp.com/1/profiles.json?access_token={token}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if not token:
        print("BUFFER_ACCESS_TOKEN must be set", file=sys.stderr)
        return 1

    try:
        profiles = fetch_profiles(token)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        OUT_PATH.write_text(
            json.dumps(
                {"error": str(e), "status": e.code, "body": body},
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Buffer API error {e.code}: {body}", file=sys.stderr)
        return 1

    summary = []
    for p in profiles or []:
        summary.append(
            {
                "id": p.get("id"),
                "service": p.get("service"),
                "username": p.get("formatted_username")
                or p.get("service_username"),
            }
        )

    OUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {len(summary)} profile(s) to {OUT_PATH.relative_to(OUT_PATH.parents[1])}")
    for entry in summary:
        print(f"  {entry['service']:<12} {entry['username'] or '?':<30} {entry['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
