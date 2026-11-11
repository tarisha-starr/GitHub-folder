"""POST this week's reels to the Zapier webhook, one per brand.

One reel per brand every Sunday (New Zealand time). Each reel recaps the
three question cards that brand posted that Monday, Wednesday and Friday,
so the first reels go out on the Sunday after QUESTIONS_LAUNCH_DATE and
the 14th, a single-question finale, closes each series.

  serw     The Second Awakening              videos/awakening/reel-<id>.mp4
  couples  Three questions to ask each other videos/couples/reel-<id>.mp4

Each reel is its own webhook call with post_type "reel", a "brand" field
for Zap routing, and video_url. image_url is the week's first question
card, for Zaps that want a cover image.

Required env vars:
  ZAPIER_WEBHOOK_URL      same Catch Hook URL as the other pushes
  IMAGE_RAW_BASE          public raw URL base of the repo
  QUESTIONS_LAUNCH_DATE   optional, shared with the question cards
  QUESTION_BRANDS         optional, comma list; default "serw,couples"
  FORCE_DATE              optional, YYYY-MM-DD, for testing
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from zapier_push_question import enabled_brands, launch_date, send, today_nz

ROOT = Path(__file__).resolve().parent.parent

SERIES = {
    # brand: (reels file, video folder, question card folder, theme tag)
    "serw": ("second_awakening_reels.json", "awakening", "serw", "the second awakening"),
    "couples": ("couples_reels.json", "couples", "couples", "questions to ask each other"),
}


def reel_index(day: date, launch: date) -> int | None:
    """0-based reel number for `day`, or None if it is not a reel Sunday."""
    first_sunday = launch + timedelta(days=(6 - launch.weekday()) % 7)
    if day < first_sunday or day.weekday() != 6:
        return None
    return (day - first_sunday).days // 7


def build_payload(brand: str, reel: dict, raw_base: str) -> dict:
    reels_file, video_dir, card_dir, theme = SERIES[brand]
    base = raw_base.rstrip("/")
    tags = reel.get("hashtags") or []
    return {
        "post_type": "reel",
        "brand": brand,
        "post_id": reel["id"],
        "caption": reel["caption"],
        "question": reel["caption"].split("\n\n")[0],
        "hashtags": " ".join(tags),
        "hashtags_list": tags,
        "video_url": f"{base}/videos/{video_dir}/reel-{reel['id']}.mp4",
        "image_url": f"{base}/images/questions/{card_dir}/question-{reel['question_ids'][0]}.jpg",
        "themes": [theme],
    }


def main() -> int:
    day = today_nz()
    n = reel_index(day, launch_date())
    if n is None:
        print(f"{day} is not a reel day. Skipping.")
        return 0

    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    ok = True
    for brand in enabled_brands():
        with (ROOT / "content" / SERIES[brand][0]).open(encoding="utf-8") as f:
            reels = json.load(f)
        if n >= len(reels):
            print(f"All {len(reels)} {brand} reels have been posted. Skipping.")
            continue
        payload = build_payload(brand, reels[n], raw_base or "https://example.invalid")
        if not webhook_url or not raw_base:
            print("ZAPIER_WEBHOOK_URL and IMAGE_RAW_BASE must be set. Payload would be:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            ok = False
            continue
        ok = send(webhook_url, payload) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
