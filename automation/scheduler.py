"""Pick today's post deterministically based on the date.

Rotates through posts.json so each post lands on a predictable day.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

POSTS_PATH = Path(__file__).resolve().parent.parent / "content" / "posts.json"


def load_posts() -> list[dict]:
    with POSTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def post_for(day: date, posts: list[dict]) -> dict:
    index = day.toordinal() % len(posts)
    return posts[index]


def todays_post() -> dict:
    return post_for(date.today(), load_posts())


if __name__ == "__main__":
    post = todays_post()
    print(json.dumps(post, indent=2, ensure_ascii=False))
