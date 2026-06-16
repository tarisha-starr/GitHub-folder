"""POST today's book or practice post to the SERW book Zapier webhook.

Mirrors the structure of zapier_push.py but reads from book-posts.json /
practices.json via book_scheduler.

Required env vars:
  ZAPIER_WEBHOOK_URL   the Catch Hook URL Zapier gives you for book content
  IMAGE_RAW_BASE            e.g. https://raw.githubusercontent.com/tarisha-starr/GitHub-folder/main
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from book_scheduler import todays_entry, remaining_count

ALERT_THRESHOLD = 7


def build_caption(post: dict) -> str:
    parts = [post.get("caption", post.get("hook", "")).strip()]
    hashtags = post.get("hashtags") or []
    if hashtags:
        parts.append("")
        parts.append(" ".join(hashtags))
    return "\n".join(parts)


def main() -> int:
    webhook = os.environ.get("ZAPIER_WEBHOOK_URL", "").strip()
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").strip().rstrip("/")
    if not webhook:
        print("ZAPIER_WEBHOOK_URL is not set", file=sys.stderr)
        return 1
    if not raw_base:
        print("IMAGE_RAW_BASE is not set", file=sys.stderr)
        return 1

    kind, post = todays_entry()
    if post is None:
        print("No book/practice post scheduled for today — skipping.")
        return 0

    image_path = post.get("image", "").lstrip("/")
    image_url = f"{raw_base}/{image_path}" if image_path else ""

    payload = {
        "kind": kind,
        "post_date": post.get("post_date"),
        "post_id": post.get("id"),
        "theme": post.get("theme"),
        "book_chapter": post.get("book_chapter"),
        "hook": post.get("hook"),
        "caption": build_caption(post),
        "question": post.get("question"),
        "hashtags": post.get("hashtags") or [],
        "image_url": image_url,
        "notion_url": post.get("notion_url", ""),
        "remaining_after_today": remaining_count(),
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = r.read().decode("utf-8", errors="replace")
        print(f"Posted to Zapier ({kind}/{post.get('post_date')}/{post.get('id')}). Response: {resp[:200]}")
    except urllib.error.HTTPError as e:
        print(f"Zapier webhook returned HTTP {e.code}: {e.read().decode()[:400]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to POST to Zapier: {e}", file=sys.stderr)
        return 1

    if remaining_count() <= ALERT_THRESHOLD:
        print(f"WARNING: only {remaining_count()} future-dated posts remain — generate next batch.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
