"""Pick today's book OR practice post.

Looks up today's date in content/book-posts.json and content/practices.json.
Returns the matching post (if any) plus its kind ('book' or 'practice').

Unlike scheduler.py (which uses a sequential offset from launch date), this
matches by the exact `post_date` field — so posts only fire on the dates
they're scheduled for (Mon/Wed/Fri/Sat per the SERW book calendar).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK_PATH = ROOT / "content" / "book-posts.json"
PRACTICES_PATH = ROOT / "content" / "practices.json"
REELS_PATH = ROOT / "content" / "reels.json"

# NZST is UTC+12 (May–Sep). NZDT is UTC+13 (Oct–Apr).
# We use +12 since the daily cron runs at 21:00 UTC = 09:00 NZST.
# During NZDT this will fire at 10:00am NZ which is acceptable, or update
# cron to "0 20 * * *" for 09:00 NZDT.
NZ_OFFSET = timedelta(hours=12)


def nz_today() -> str:
    """Today's date in NZ — used to match post_date entries."""
    return (datetime.now(timezone.utc) + NZ_OFFSET).date().isoformat()


def _load(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def todays_entry() -> tuple[str, dict] | tuple[None, None]:
    today = nz_today()
    for post in _load(BOOK_PATH):
        if post.get("post_date") == today:
            return ("book", post)
    for post in _load(REELS_PATH):
        if post.get("post_date") == today:
            return ("reel", post)
    for post in _load(PRACTICES_PATH):
        if post.get("post_date") == today:
            return ("practice", post)
    return (None, None)


def remaining_count() -> int:
    """Future-dated posts AFTER today (NZ), across all files."""
    today = nz_today()
    n = 0
    for post in _load(BOOK_PATH) + _load(PRACTICES_PATH) + _load(REELS_PATH):
        pd = post.get("post_date")
        if pd and pd > today:
            n += 1
    return n


if __name__ == "__main__":
    print(f"NZ today: {nz_today()}")
    kind, post = todays_entry()
    if post is None:
        print(json.dumps({"info": "No book/practice post scheduled for today (NZ)"}, indent=2))
    else:
        print(json.dumps({"kind": kind, "post": post}, indent=2, ensure_ascii=False))
    print(f"\nFuture-dated posts remaining: {remaining_count()}")
