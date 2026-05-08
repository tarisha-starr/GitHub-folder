"""POST today's infographic to the Zapier webhook.

Selects today's infographic using the same date math as the image and
journal schedulers (POSTS_LAUNCH_DATE controls day 0, sequential, each
used once). Builds a payload with image_url + caption + hashtags and
sends to ZAPIER_WEBHOOK_URL.

Required env vars:
  ZAPIER_WEBHOOK_URL    same Catch Hook URL as the image push
  IMAGE_RAW_BASE        public raw URL base of the repo
  POSTS_LAUNCH_DATE     optional, YYYY-MM-DD
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from scheduler import launch_date

ROOT = Path(__file__).resolve().parent.parent
INFOGRAPHICS_PATH = ROOT / "content" / "infographics.json"

DEFAULT_HASHTAGS = [
    "#WomenOver40",
    "#MidlifeWomen",
    "#Midlife",
    "#IntimacyMatters",
    "#SacredFeminine",
    "#FeminineEnergy",
    "#SelfReclamation",
]


def load_infographics() -> list[dict]:
    with INFOGRAPHICS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def todays_infographic() -> dict | None:
    items = load_infographics()
    n = (date.today() - launch_date()).days
    if n < 0 or n >= len(items):
        return None
    return items[n]


def build_payload(entry: dict, raw_base: str) -> dict:
    base = raw_base.rstrip("/")
    image_url = f"{base}/{entry['image']}"
    hashtags = " ".join(DEFAULT_HASHTAGS)
    return {
        "post_type": "infographic",
        "post_id": entry["id"],
        "title": entry.get("title", ""),
        "caption": entry["caption"],
        "question": entry["caption"],
        "hashtags": hashtags,
        "hashtags_list": DEFAULT_HASHTAGS,
        "image_url": image_url,
        "infographic_image_url": image_url,
        "video_url": "",
        "themes": ["infographic", "education"],
    }


def main() -> int:
    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    if not webhook_url or not raw_base:
        print(
            "ZAPIER_WEBHOOK_URL and IMAGE_RAW_BASE must be set",
            file=sys.stderr,
        )
        return 1

    entry = todays_infographic()
    if entry is None:
        print(
            "No infographic for today (out of inventory or before launch). Skipping.",
            file=sys.stderr,
        )
        return 0

    payload = build_payload(entry, raw_base)
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Zapier webhook error {e.code}: {body}", file=sys.stderr)
        return 1

    print(f"Sent infographic #{entry['id']} to Zapier; response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
