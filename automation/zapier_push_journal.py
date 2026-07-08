"""POST today's journal prompt to the Zapier webhook.

Selects the journal prompt for today using the same date math as the
image scheduler (POSTS_LAUNCH_DATE controls day 0, sequential, each
used once). Builds a payload with `journal_image_url` and a caption
formatted as: prompt + blank line + tail.

Uses the same ZAPIER_WEBHOOK_URL as the image push so a single Zap
handles both the 1pm image post and the 6pm journal post — the Zap
just sees a different payload at each fire and routes accordingly
(filter on `post_type` or presence of `video_url`).

Required env vars:
  ZAPIER_WEBHOOK_URL    same Catch Hook URL as the image push
  IMAGE_RAW_BASE        public raw URL base of the repo
  POSTS_LAUNCH_DATE     optional, YYYY-MM-DD (defaults to scheduler default)
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
PROMPTS_PATH = ROOT / "content" / "journal_prompts.json"

DEFAULT_HASHTAGS = [
    "#midlifewoman",
    "#womenover40",
    "#journaling",
    "#innerwork",
    "#selfreflection",
]


def load_prompts() -> list[dict]:
    with PROMPTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def todays_journal_prompt() -> dict | None:
    prompts = load_prompts()
    n = (date.today() - launch_date()).days
    if n < 0 or n >= len(prompts):
        return None
    return prompts[n]


def build_payload(entry: dict, raw_base: str) -> dict:
    base = raw_base.rstrip("/")
    journal_image_url = f"{base}/images/journal/journal-{entry['id']}.jpg"
    caption = f"{entry['prompt']}\n\n{entry['caption_tail']}"
    tags_list = entry.get("hashtags") or DEFAULT_HASHTAGS
    hashtags = " ".join(tags_list)
    return {
        "post_type": "journal",
        "post_id": entry["id"],
        "prompt": entry["prompt"],
        "caption": caption,
        "question": entry["caption_tail"],
        "hashtags": hashtags,
        "hashtags_list": tags_list,
        "image_url": journal_image_url,
        "journal_image_url": journal_image_url,
        "video_url": "",
        "themes": ["journaling", "reflection"],
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

    entry = todays_journal_prompt()
    if entry is None:
        print(
            "No journal prompt for today (out of inventory or before launch). Skipping.",
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

    print(f"Sent journal prompt #{entry['id']} to Zapier; response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
