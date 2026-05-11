"""POST today's testimonial to the Zapier webhook.

The 1pm slot alternates between testimonial (even days from REPURPOSE
launch) and a regular image post from posts.json (odd days). This
script handles the testimonial days only — it picks the right
testimonial by day-index and no-ops on image-post days.

Required env vars:
  ZAPIER_WEBHOOK_URL    same Catch Hook URL as the image push
  IMAGE_RAW_BASE        public raw URL base of the repo
  REPURPOSE_LAUNCH_DATE optional override, YYYY-MM-DD
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from scheduler import repurposed_1pm_entry


def build_payload(entry: dict, raw_base: str) -> dict:
    base = raw_base.rstrip("/")
    image_url = f"{base}/{entry['image']}"
    text = entry["text"]
    attribution = entry.get("attribution", "").strip()
    hashtags_list = entry.get("hashtags", [])
    hashtags = " ".join(hashtags_list)

    caption_parts = [f"“{text}”"]
    if attribution:
        caption_parts.append("")
        caption_parts.append(f"— {attribution}")
    if hashtags:
        caption_parts.append("")
        caption_parts.append(hashtags)
    caption = "\n".join(caption_parts)

    return {
        "post_type": "testimonial",
        "post_id": entry["id"],
        "caption": caption,
        "text": text,
        "attribution": attribution,
        "hashtags": hashtags,
        "hashtags_list": hashtags_list,
        "image_url": image_url,
        "testimonial_image_url": image_url,
        "video_url": "",
        "themes": ["testimonial", "workshop"],
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

    slot = repurposed_1pm_entry()
    if slot is None:
        print(
            "1pm slot is empty (before repurpose launch or inventory exhausted). Skipping.",
            file=sys.stderr,
        )
        return 0
    if slot["kind"] != "testimonial":
        print(
            f"Today's 1pm slot is a regular post (id={slot['data']['id']}). "
            "Testimonial push skipped — zapier_push.py will handle it.",
        )
        return 0

    payload = build_payload(slot["data"], raw_base)
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

    print(f"Sent testimonial #{slot['data']['id']} to Zapier; response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
