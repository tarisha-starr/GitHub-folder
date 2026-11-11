"""POST today's brave-question card to the Zapier webhook.

Posts three times a week, Monday, Wednesday and Friday (New Zealand
time), working through content/brave_questions.json in order, each card
used once. QUESTIONS_LAUNCH_DATE is the first posting day (a Monday,
Wednesday or Friday). On any other weekday, or once all 40 cards have
gone out, the script exits quietly without posting.

Two versions go out each posting day, one per brand, each as its own
webhook call with a "brand" field so the Zap can send it to the right
account:
  serw     content/brave_questions.json    images/questions/serw/
  couples  content/couples_questions.json  images/questions/couples/
The payload otherwise has the same shape as the journal push, with
post_type "question" (image_url plus caption).

Required env vars:
  ZAPIER_WEBHOOK_URL      same Catch Hook URL as the other pushes
  IMAGE_RAW_BASE          public raw URL base of the repo
  QUESTIONS_LAUNCH_DATE   optional, YYYY-MM-DD; defaults to DEFAULT_LAUNCH
  QUESTION_BRANDS         optional, comma list; default "serw,couples"
  FORCE_DATE              optional, YYYY-MM-DD; pretend today is this date
                          (for testing)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent

NZ = ZoneInfo("Pacific/Auckland")
POST_DAYS = {0, 2, 4}  # Monday, Wednesday, Friday
DEFAULT_LAUNCH = date(2026, 11, 16)  # Monday


def env_date(name: str) -> date | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def today_nz() -> date:
    return env_date("FORCE_DATE") or datetime.now(NZ).date()


def launch_date() -> date:
    return env_date("QUESTIONS_LAUNCH_DATE") or DEFAULT_LAUNCH


def post_index(day: date, launch: date) -> int | None:
    """How many posting days came before `day`, counting from launch.
    None when `day` is not a posting day or is before launch."""
    if day < launch or day.weekday() not in POST_DAYS:
        return None
    n = 0
    d = launch
    while d < day:
        if d.weekday() in POST_DAYS:
            n += 1
        d += timedelta(days=1)
    return n


BRANDS = {
    # brand key: (questions file, image folder)
    "serw": ("brave_questions.json", "serw"),
    "couples": ("couples_questions.json", "couples"),
}


def enabled_brands() -> list[str]:
    raw = os.environ.get("QUESTION_BRANDS") or "serw,couples"
    return [b.strip() for b in raw.split(",") if b.strip() in BRANDS]


def load_questions(brand: str) -> list[dict]:
    with (ROOT / "content" / BRANDS[brand][0]).open(encoding="utf-8") as f:
        return json.load(f)


def build_payload(brand: str, entry: dict, raw_base: str) -> dict:
    base = raw_base.rstrip("/")
    image_url = f"{base}/images/questions/{BRANDS[brand][1]}/question-{entry['id']}.jpg"
    caption = f"{entry['question']}\n\n{entry['caption_tail']}"
    tags = entry.get("hashtags") or []
    return {
        "post_type": "question",
        "brand": brand,
        "post_id": entry["id"],
        "prompt": entry["question"],
        "caption": caption,
        "question": entry["question"],
        "hashtags": " ".join(tags),
        "hashtags_list": tags,
        "image_url": image_url,
        "video_url": "",
        "themes": [entry["theme"]],
    }


def send(webhook_url: str, payload: dict) -> bool:
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
        return False
    print(f"Sent {payload['brand']} {payload['post_type']} #{payload['post_id']} to Zapier; response: {result}")
    return True


def main() -> int:
    day = today_nz()
    n = post_index(day, launch_date())
    if n is None:
        print(f"{day} is not a question day. Skipping.")
        return 0

    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    ok = True
    for brand in enabled_brands():
        questions = load_questions(brand)
        if n >= len(questions):
            print(f"All {len(questions)} {brand} question cards have been posted. Skipping.")
            continue
        payload = build_payload(brand, questions[n], raw_base or "https://example.invalid")
        if not webhook_url or not raw_base:
            print("ZAPIER_WEBHOOK_URL and IMAGE_RAW_BASE must be set. Payload would be:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            ok = False
            continue
        ok = send(webhook_url, payload) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
