"""POST this week's "The Second Awakening" reel to the Zapier webhook.

One reel every Sunday (New Zealand time). Each reel recaps the three
question cards that went out that Monday, Wednesday and Friday, so the
first reel goes out on the Sunday after QUESTIONS_LAUNCH_DATE and the
14th, a single-question finale, closes the series.

The payload has the usual shape with post_type "reel" and a video_url
pointing at videos/awakening/reel-<id>.mp4. image_url is the week's first
question card, for Zaps that want a cover image.

Required env vars:
  ZAPIER_WEBHOOK_URL      same Catch Hook URL as the other pushes
  IMAGE_RAW_BASE          public raw URL base of the repo
  QUESTIONS_LAUNCH_DATE   optional, shared with the question cards
  FORCE_DATE              optional, YYYY-MM-DD, for testing
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from zapier_push_question import launch_date, today_nz

ROOT = Path(__file__).resolve().parent.parent
REELS_PATH = ROOT / "content" / "second_awakening_reels.json"


def reel_index(day: date, launch: date) -> int | None:
    """0-based reel number for `day`, or None if it is not a reel Sunday."""
    first_sunday = launch + timedelta(days=(6 - launch.weekday()) % 7)
    if day < first_sunday or day.weekday() != 6:
        return None
    return (day - first_sunday).days // 7


def build_payload(reel: dict, raw_base: str) -> dict:
    base = raw_base.rstrip("/")
    tags = reel.get("hashtags") or []
    return {
        "post_type": "reel",
        "post_id": reel["id"],
        "caption": reel["caption"],
        "question": reel["caption"].split("\n\n")[1] if "\n\n" in reel["caption"] else "",
        "hashtags": " ".join(tags),
        "hashtags_list": tags,
        "video_url": f"{base}/videos/awakening/reel-{reel['id']}.mp4",
        "image_url": f"{base}/images/questions/question-{reel['question_ids'][0]}.jpg",
        "themes": ["the second awakening"],
    }


def main() -> int:
    with REELS_PATH.open(encoding="utf-8") as f:
        reels = json.load(f)
    day = today_nz()
    n = reel_index(day, launch_date())
    if n is None:
        print(f"{day} is not a reel day. Skipping.")
        return 0
    if n >= len(reels):
        print(f"All {len(reels)} reels have been posted. Skipping.")
        return 0
    reel = reels[n]

    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    payload = build_payload(reel, raw_base or "https://example.invalid")
    if not webhook_url or not raw_base:
        print("ZAPIER_WEBHOOK_URL and IMAGE_RAW_BASE must be set. Payload would be:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Zapier webhook error {e.code}: {body}", file=sys.stderr)
        return 1

    print(f"Sent reel #{reel['id']} to Zapier ({len(reels) - n - 1} left); response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
