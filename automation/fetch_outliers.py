"""Fetch YouTube outliers in the niche and append them to content/outliers.csv.

An "outlier" is a video where view count is at least N x the channel's median
view count over the channel's most recent ~20 uploads (default N = 10, set by
--multiplier).

Requires:
  YOUTUBE_API_KEY  - YouTube Data API v3 key
                     https://console.cloud.google.com/apis/library/youtube.googleapis.com

Usage:
  cd automation
  YOUTUBE_API_KEY=... python fetch_outliers.py
  YOUTUBE_API_KEY=... python fetch_outliers.py --shorts
  YOUTUBE_API_KEY=... python fetch_outliers.py --queries my_queries.json --per-query 50

The script is idempotent: rows whose URL already exists in the CSV are skipped.

Quota note: each query costs 100 units (search.list), each unique channel
costs 100 more (search.list for recent uploads), and each batch of up to 50
videos costs 1 (videos.list). The default daily quota is 10,000 units, which
is roughly 50 queries + 50 channel medians.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://www.googleapis.com/youtube/v3"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES = Path(__file__).resolve().parent / "outlier_queries.json"
DEFAULT_CSV = REPO_ROOT / "content" / "outliers.csv"

CSV_COLUMNS = [
    "id",
    "platform",
    "content_type",
    "url",
    "creator",
    "creator_avg_views",
    "views",
    "multiplier",
    "hook",
    "topic",
    "format",
    "length",
    "cta",
    "why_it_worked",
    "verified",
]

ISO8601_DURATION = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def api_get(path: str, params: dict, api_key: str) -> dict:
    params = {**params, "key": api_key}
    qs = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}?{qs}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_videos(query: str, max_results: int, api_key: str) -> list[str]:
    """Return up to max_results video IDs for the query, ordered by view count."""
    items: list[str] = []
    page_token = None
    while len(items) < max_results:
        params = {
            "part": "id",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": min(50, max_results - len(items)),
            "relevanceLanguage": "en",
        }
        if page_token:
            params["pageToken"] = page_token
        data = api_get("search", params, api_key)
        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid:
                items.append(vid)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return items[:max_results]


def videos_details(video_ids: list[str], api_key: str) -> list[dict]:
    """Hydrate up to 50 video IDs with snippet + statistics + contentDetails."""
    out: list[dict] = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        data = api_get(
            "videos",
            {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(chunk),
            },
            api_key,
        )
        out.extend(data.get("items", []))
    return out


def channel_recent_view_counts(channel_id: str, api_key: str, sample: int = 20) -> list[int]:
    """Return view counts for the channel's most recent uploads (best effort)."""
    data = api_get(
        "search",
        {
            "part": "id",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": sample,
        },
        api_key,
    )
    ids = [item["id"]["videoId"] for item in data.get("items", []) if item.get("id", {}).get("videoId")]
    if not ids:
        return []
    details = videos_details(ids, api_key)
    return [int(v["statistics"].get("viewCount", 0)) for v in details]


def parse_duration_seconds(iso: str) -> int:
    m = ISO8601_DURATION.fullmatch(iso or "")
    if not m:
        return 0
    h, mi, s = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mi * 60 + s


def first_line(text: str, max_chars: int = 140) -> str:
    line = (text or "").strip().splitlines()[0] if text else ""
    return line[:max_chars]


def load_existing_urls(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["url"] for row in reader if row.get("url")}


def next_id(csv_path: Path) -> int:
    if not csv_path.exists():
        return 1
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ids = [int(r["id"]) for r in reader if (r.get("id") or "").isdigit()]
    return (max(ids) + 1) if ids else 1


def append_rows(csv_path: Path, rows: list[dict]) -> None:
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})


def build_row(video: dict, median: int, multiplier: float, content_type: str, row_id: int) -> dict:
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    duration = parse_duration_seconds(video.get("contentDetails", {}).get("duration", ""))
    return {
        "id": row_id,
        "platform": "youtube",
        "content_type": content_type,
        "url": f"https://www.youtube.com/watch?v={video['id']}",
        "creator": snippet.get("channelTitle", ""),
        "creator_avg_views": median,
        "views": int(stats.get("viewCount", 0)),
        "multiplier": round(multiplier, 2),
        "hook": first_line(snippet.get("title", "")),
        "topic": first_line(snippet.get("description", "")),
        "format": "talking-head" if duration > 600 else "short-video",
        "length": duration,
        "cta": "",
        "why_it_worked": "",
        "verified": "true",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    p.add_argument("--output", type=Path, default=DEFAULT_CSV)
    p.add_argument("--per-query", type=int, default=25)
    p.add_argument("--multiplier", type=float, default=10.0)
    p.add_argument("--shorts", action="store_true", help="keep videos under 70s and tag content_type=youtube_shorts")
    p.add_argument("--content-type", default="youtube_long_form")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY env var is required", file=sys.stderr)
        return 1

    queries = json.loads(args.queries.read_text(encoding="utf-8"))
    if not isinstance(queries, list) or not queries:
        print(f"{args.queries} must contain a non-empty JSON list of strings", file=sys.stderr)
        return 1

    content_type = "youtube_shorts" if args.shorts else args.content_type
    existing_urls = load_existing_urls(args.output)
    row_id = next_id(args.output)
    median_cache: dict[str, int] = {}
    rows: list[dict] = []

    for q in queries:
        try:
            video_ids = search_videos(q, args.per_query, api_key)
        except urllib.error.HTTPError as e:
            print(f"search failed for {q!r}: {e}", file=sys.stderr)
            continue
        videos = videos_details(video_ids, api_key)
        for v in videos:
            url = f"https://www.youtube.com/watch?v={v['id']}"
            if url in existing_urls:
                continue
            duration = parse_duration_seconds(v.get("contentDetails", {}).get("duration", ""))
            if args.shorts and duration > 70:
                continue
            if not args.shorts and duration <= 70:
                continue
            views = int(v.get("statistics", {}).get("viewCount", 0))
            channel_id = v.get("snippet", {}).get("channelId", "")
            if not channel_id:
                continue
            if channel_id not in median_cache:
                try:
                    counts = channel_recent_view_counts(channel_id, api_key)
                except urllib.error.HTTPError as e:
                    print(f"channel fetch failed for {channel_id}: {e}", file=sys.stderr)
                    counts = []
                median_cache[channel_id] = int(statistics.median(counts)) if counts else 0
            median = median_cache[channel_id]
            if median <= 0:
                continue
            ratio = views / median
            if ratio < args.multiplier:
                continue
            rows.append(build_row(v, median, ratio, content_type, row_id))
            existing_urls.add(url)
            row_id += 1

    if not rows:
        print("No outliers found above the multiplier threshold.")
        return 0

    append_rows(args.output, rows)
    print(f"Appended {len(rows)} outlier(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
