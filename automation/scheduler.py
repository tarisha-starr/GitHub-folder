"""Pick today's post — sequential, each used exactly once.

POSTS_LAUNCH_DATE controls day 0 (the first post that goes out). Set as
a GitHub repository variable (or env var locally). Defaults to
DEFAULT_LAUNCH below if unset.

After the list is exhausted, todays_post() returns None and the email
script sends an "out of posts" alert instead of trying to publish.

remaining_count() returns how many unused posts are LEFT (excluding
today's). The daily email script also checks this — if it drops to
ALERT_THRESHOLD, it sends a "create more posts" warning email.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

POSTS_PATH = Path(__file__).resolve().parent.parent / "content" / "posts.json"

# Override with the repo variable POSTS_LAUNCH_DATE = "YYYY-MM-DD"
DEFAULT_LAUNCH = date(2026, 5, 3)

ALERT_THRESHOLD = 7  # warn when this many posts remain (after today)


def launch_date() -> date:
    raw = os.environ.get("POSTS_LAUNCH_DATE")
    if raw:
        try:
            return date.fromisoformat(raw.strip())
        except ValueError:
            pass
    return DEFAULT_LAUNCH


def load_posts() -> list[dict]:
    with POSTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def post_for(day: date, posts: list[dict], launch: date) -> dict | None:
    n = (day - launch).days
    if n < 0 or n >= len(posts):
        return None
    return posts[n]


def todays_post() -> dict | None:
    return post_for(date.today(), load_posts(), launch_date())


def remaining_count() -> int:
    """Unused posts left AFTER today. Returns 0 if exhausted."""
    posts = load_posts()
    n = (date.today() - launch_date()).days
    return max(0, len(posts) - n - 1)


if __name__ == "__main__":
    post = todays_post()
    if post is None:
        print(json.dumps({"error": "No post for today (out of inventory or before launch)"}, indent=2))
    else:
        print(json.dumps(post, indent=2, ensure_ascii=False))
    print(f"\nRemaining after today: {remaining_count()}")
