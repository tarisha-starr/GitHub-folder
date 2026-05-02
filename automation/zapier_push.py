"""POST today's post to a Zapier webhook.

Zapier handles the Buffer OAuth dance — this script just sends a JSON
payload (caption, question, hashtags, image_url) to the webhook URL.
The Zap then has a Buffer "Add to Queue" action that consumes the
fields.

Required env vars:
  ZAPIER_WEBHOOK_URL    the Catch Hook URL Zapier gives you
  IMAGE_RAW_BASE       e.g. https://raw.githubusercontent.com/<owner>/<repo>/main
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from scheduler import todays_post


def build_payload(post: dict, raw_base: str) -> dict:
    image_path = post.get("image", "")
    image_url = f"{raw_base.rstrip('/')}/{image_path}" if image_path else ""
    return {
        "post_id": post["id"],
        "hook": post["hook"],
        "caption": post.get("caption", post["hook"]),
        "question": post.get("question", ""),
        "hashtags": " ".join(post.get("hashtags", [])),
        "hashtags_list": post.get("hashtags", []),
        "image_url": image_url,
        "visual_prompt": post.get("visual", ""),
        "themes": post.get("themes", []),
    }


def post_to_zapier(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    webhook_url = os.environ.get("ZAPIER_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    if not webhook_url or not raw_base:
        print(
            "ZAPIER_WEBHOOK_URL and IMAGE_RAW_BASE must be set",
            file=sys.stderr,
        )
        return 1

    post = todays_post()
    if post is None:
        print("No post for today (out of inventory or before launch). Skipping Zapier.", file=sys.stderr)
        return 0
    payload = build_payload(post, raw_base)
    try:
        result = post_to_zapier(webhook_url, payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Zapier webhook error {e.code}: {body}", file=sys.stderr)
        return 1

    print(f"Sent post #{post['id']} to Zapier; response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
