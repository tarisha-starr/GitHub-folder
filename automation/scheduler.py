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

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
POSTS_PATH = CONTENT_DIR / "posts.json"
TESTIMONIALS_PATH = CONTENT_DIR / "testimonials.json"

# Override with the repo variable POSTS_LAUNCH_DATE = "YYYY-MM-DD"
DEFAULT_LAUNCH = date(2026, 5, 3)

# Day 0 of the testimonial + image-post alternation at the 1pm slot.
# Even days from this launch fire a testimonial; odd days fire the next
# unused image post from posts.json (skipping SKIP_POSTS already used).
DEFAULT_REPURPOSE_LAUNCH = date(2026, 5, 12)
SKIP_POSTS = 8  # posts.json indices 0..7 already published before repurpose

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


def repurpose_launch_date() -> date:
    raw = os.environ.get("REPURPOSE_LAUNCH_DATE")
    if raw:
        try:
            return date.fromisoformat(raw.strip())
        except ValueError:
            pass
    return DEFAULT_REPURPOSE_LAUNCH


def load_testimonials() -> list[dict]:
    with TESTIMONIALS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def repurposed_1pm_entry() -> dict | None:
    """Pick today's 1pm content under the repurposed rotation.

    Returns a dict {'kind': 'testimonial'|'post', 'data': {...}} or None
    if today is before REPURPOSE_LAUNCH or both inventories are exhausted.
    """
    today = date.today()
    n = (today - repurpose_launch_date()).days
    if n < 0:
        return None
    if n % 2 == 0:
        idx = n // 2
        testimonials = load_testimonials()
        if idx >= len(testimonials):
            return None
        return {"kind": "testimonial", "data": testimonials[idx]}
    idx = SKIP_POSTS + (n - 1) // 2
    posts = load_posts()
    if idx >= len(posts):
        return None
    return {"kind": "post", "data": posts[idx]}


def repurposed_1pm_remaining() -> int:
    """Total 1pm slots left AFTER today across both inventories."""
    today = date.today()
    n = (today - repurpose_launch_date()).days
    if n < 0:
        n = -1
    used_testimonials = (n + 2) // 2 if n >= 0 else 0  # includes today if even
    used_post_pairs = (n + 1) // 2 if n >= 0 else 0   # includes today if odd
    total_t = len(load_testimonials())
    total_p = max(0, len(load_posts()) - SKIP_POSTS)
    remaining_t = max(0, total_t - used_testimonials)
    remaining_p = max(0, total_p - used_post_pairs)
    return remaining_t + remaining_p


if __name__ == "__main__":
    slot = repurposed_1pm_entry()
    if slot is None:
        print(json.dumps({"error": "No 1pm post today (before repurpose launch or exhausted)"}, indent=2))
    else:
        print(json.dumps(slot, indent=2, ensure_ascii=False))
    print(f"\n1pm slots remaining after today: {repurposed_1pm_remaining()}")
