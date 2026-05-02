"""POST today's video to a separate Zapier webhook for Reels/TikTok.

Same scheduler logic as zapier_push.py, but sends a video_url pointing
to the matching videos/video-N.mp4 file. Use a second Zapier Zap whose
trigger is this webhook and whose action is Buffer "Add to Queue" (or
"Add Reel") on your Reels/TikTok channels.

Required env vars:
  ZAPIER_REEL_WEBHOOK_URL    second Zap's catch-hook URL
  IMAGE_RAW_BASE             public raw URL base, e.g.
                             https://raw.githubusercontent.com/<owner>/<repo>/main
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

from scheduler import todays_post


def derive_video_url(image_path: str, raw_base: str) -> str:
    base = raw_base.rstrip("/")
    name = image_path.split("/")[-1]
    m = re.match(r"image-(\d+)\.jpg$", name, re.IGNORECASE)
    if not m:
        return ""
    return f"{base}/videos/video-{m.group(1)}.mp4"


def build_payload(post: dict, raw_base: str) -> dict:
    image_path = post.get("image", "")
    image_url = f"{raw_base.rstrip('/')}/{image_path}" if image_path else ""
    video_url = derive_video_url(image_path, raw_base)
    return {
        "post_id": post["id"],
        "hook": post["hook"],
        "caption": post.get("caption", post["hook"]),
        "question": post.get("question", ""),
        "hashtags": " ".join(post.get("hashtags", [])),
        "hashtags_list": post.get("hashtags", []),
        "image_url": image_url,
        "video_url": video_url,
        "themes": post.get("themes", []),
    }


def main() -> int:
    webhook_url = os.environ.get("ZAPIER_REEL_WEBHOOK_URL")
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    if not webhook_url or not raw_base:
        print(
            "ZAPIER_REEL_WEBHOOK_URL and IMAGE_RAW_BASE must be set",
            file=sys.stderr,
        )
        return 1

    post = todays_post()
    if post is None:
        print("No post for today; skipping Reel push.", file=sys.stderr)
        return 0
    payload = build_payload(post, raw_base)
    if not payload["video_url"]:
        print(f"Post #{post['id']} has no derivable video URL", file=sys.stderr)
        return 1

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

    print(f"Sent Reel for post #{post['id']} to Zapier; response: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
