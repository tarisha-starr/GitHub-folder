"""Schedule today's post to Buffer.

Uploads the post's image to Buffer and creates an "add to queue" update on
each configured profile. The caption is built from caption + question +
hashtags from posts.json.

Requires:
  BUFFER_ACCESS_TOKEN   - personal access token (https://buffer.com/developers/apps)
  BUFFER_PROFILE_IDS    - comma-separated profile (channel) IDs
  GITHUB_RAW_BASE       - public raw URL to the repo's main branch, e.g.
                          https://raw.githubusercontent.com/tarisha-starr/GitHub-folder/main
                          (used so Buffer can fetch the image by URL)
"""

from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request
import json

from scheduler import todays_post

BUFFER_API = "https://api.bufferapp.com/1"


def build_caption(post: dict) -> str:
    parts = [post.get("caption", post["hook"]).strip()]
    hashtags = post.get("hashtags") or []
    if hashtags:
        parts.append("")
        parts.append(" ".join(hashtags))
    return "\n".join(parts)


def post_form(path: str, token: str, fields: list[tuple[str, str]]) -> dict:
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        f"{BUFFER_API}{path}?access_token={token}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def schedule(post: dict, token: str, profile_ids: list[str], image_url: str) -> dict:
    text = build_caption(post)
    fields: list[tuple[str, str]] = [("text", text), ("media[photo]", image_url)]
    for pid in profile_ids:
        fields.append(("profile_ids[]", pid))
    return post_form("/updates/create.json", token, fields)


def main() -> int:
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    profile_ids_raw = os.environ.get("BUFFER_PROFILE_IDS", "")
    raw_base = os.environ.get("GITHUB_RAW_BASE", "").rstrip("/")
    if not token or not profile_ids_raw or not raw_base:
        print("BUFFER_ACCESS_TOKEN, BUFFER_PROFILE_IDS, and GITHUB_RAW_BASE must be set", file=sys.stderr)
        return 1

    profile_ids = [p.strip() for p in profile_ids_raw.split(",") if p.strip()]
    post = todays_post()
    image_path = post.get("image")
    if not image_path:
        print(f"Post #{post['id']} has no image path", file=sys.stderr)
        return 1

    image_url = f"{raw_base}/{image_path}"
    result = schedule(post, token, profile_ids, image_url)
    if not result.get("success"):
        print(f"Buffer error: {result}", file=sys.stderr)
        return 1
    print(f"Queued post #{post['id']} to {len(profile_ids)} Buffer profile(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
