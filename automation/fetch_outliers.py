"""Fetch YouTube outliers in the niche and append them to content/outliers.csv.

An "outlier" is a video where view count is at least N x the median view
count of its channel's most recent ~50 uploads (default N = 10, set by
--multiplier). Recent-uploads median is sharper than the channel's all-time
mean for spotting videos that punched above their channel's normal traction.

Requires:
  YOUTUBE_API_KEY  - YouTube Data API v3 key
                     https://console.cloud.google.com/apis/library/youtube.googleapis.com

Usage:
  cd automation
  YOUTUBE_API_KEY=... python fetch_outliers.py
  YOUTUBE_API_KEY=... python fetch_outliers.py --shorts
  YOUTUBE_API_KEY=... python fetch_outliers.py --queries my_queries.json --per-query 50

The script is idempotent: rows whose URL already exists in the CSV are
skipped. When no candidate crosses the threshold, the top 10 candidates
are printed with their actual multipliers so you can re-run with a
calibrated --multiplier.

Quota cost (default config): ~20 queries x 100 units (search.list) + a
few batched channels.list / videos.list / playlistItems.list calls at 1
unit each. A typical run is ~2,200 units, well inside the 10,000/day
free quota.
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


class YouTubeAPIError(Exception):
    def __init__(self, status: int, reason: str, message: str):
        self.status = status
        self.reason = reason
        self.message = message
        super().__init__(f"HTTP {status} {reason}: {message}")


def api_get(path: str, params: dict, api_key: str) -> dict:
    params = {**params, "key": api_key}
    qs = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}?{qs}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        reason = "unknown"
        message = body[:200]
        try:
            err = json.loads(body).get("error", {})
            errors = err.get("errors") or [{}]
            reason = errors[0].get("reason", reason)
            message = err.get("message", message)
        except (ValueError, KeyError, IndexError, AttributeError):
            pass
        raise YouTubeAPIError(e.code, reason, message) from None


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
        try:
            data = api_get(
                "videos",
                {
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(chunk),
                },
                api_key,
            )
        except (urllib.error.HTTPError, YouTubeAPIError) as e:
            print(f"videos.list failed for {len(chunk)} ids: {e}", file=sys.stderr)
            continue
        out.extend(data.get("items", []))
    return out


def channel_baselines(channel_ids: list[str], api_key: str) -> dict[str, int]:
    """Return {channel_id: median_recent_views} for up to 50 IDs per call.

    Uses channels.list to get each channel's uploads playlist ID
    (1 unit per batched call), then playlistItems.list to pull the most
    recent ~50 uploads (1 unit per channel), then videos.list to get
    those videos' view counts (1 unit per 50). Median of those is the
    baseline — much sharper than the channel's all-time mean for spotting
    outliers, and still cheap on quota (~1 unit per channel vs ~100 for
    a per-channel search.list).
    """
    out: dict[str, int] = {}
    unique = list(dict.fromkeys(channel_ids))
    uploads_playlists: dict[str, str] = {}

    for i in range(0, len(unique), 50):
        chunk = unique[i : i + 50]
        try:
            data = api_get(
                "channels",
                {"part": "contentDetails", "id": ",".join(chunk)},
                api_key,
            )
        except (urllib.error.HTTPError, YouTubeAPIError) as e:
            print(f"channels.list failed for {len(chunk)} ids: {e}", file=sys.stderr)
            continue
        for item in data.get("items", []):
            playlists = item.get("contentDetails", {}).get("relatedPlaylists", {})
            uploads = playlists.get("uploads")
            if uploads:
                uploads_playlists[item["id"]] = uploads

    for channel_id, playlist_id in uploads_playlists.items():
        try:
            data = api_get(
                "playlistItems",
                {
                    "part": "contentDetails",
                    "playlistId": playlist_id,
                    "maxResults": 50,
                },
                api_key,
            )
        except (urllib.error.HTTPError, YouTubeAPIError) as e:
            print(f"playlistItems.list failed for {channel_id}: {e}", file=sys.stderr)
            continue
        recent_video_ids = [
            item["contentDetails"]["videoId"]
            for item in data.get("items", [])
            if item.get("contentDetails", {}).get("videoId")
        ]
        if not recent_video_ids:
            continue
        details = videos_details(recent_video_ids, api_key)
        view_counts = [int(v.get("statistics", {}).get("viewCount", 0)) for v in details]
        view_counts = [v for v in view_counts if v > 0]
        if view_counts:
            out[channel_id] = int(statistics.median(view_counts))
    return out


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
    rows: list[dict] = []

    # Phase 1: collect candidate videos across all queries (filtered by duration).
    candidates: list[dict] = []
    seen_video_ids: set[str] = set()
    for q in queries:
        try:
            video_ids = search_videos(q, args.per_query, api_key)
        except (urllib.error.HTTPError, YouTubeAPIError) as e:
            print(f"search failed for {q!r}: {e}", file=sys.stderr)
            continue
        new_ids = [vid for vid in video_ids if vid not in seen_video_ids]
        seen_video_ids.update(new_ids)
        videos = videos_details(new_ids, api_key)
        for v in videos:
            url = f"https://www.youtube.com/watch?v={v['id']}"
            if url in existing_urls:
                continue
            duration = parse_duration_seconds(v.get("contentDetails", {}).get("duration", ""))
            if args.shorts and duration > 70:
                continue
            if not args.shorts and duration <= 70:
                continue
            if not v.get("snippet", {}).get("channelId"):
                continue
            candidates.append(v)

    # Phase 2: pull each channel's recent-uploads median for the baseline.
    channel_ids = [v["snippet"]["channelId"] for v in candidates]
    baselines = channel_baselines(channel_ids, api_key)

    # Phase 3: filter to outliers and build rows. Also collect diagnostics so
    # we can show the top candidates even when nothing crosses the threshold.
    scored: list[tuple[float, dict, int]] = []
    for v in candidates:
        channel_id = v["snippet"]["channelId"]
        baseline = baselines.get(channel_id, 0)
        if baseline <= 0:
            continue
        views = int(v.get("statistics", {}).get("viewCount", 0))
        ratio = views / baseline
        scored.append((ratio, v, baseline))

    scored.sort(key=lambda t: -t[0])

    for ratio, v, baseline in scored:
        if ratio < args.multiplier:
            continue
        url = f"https://www.youtube.com/watch?v={v['id']}"
        rows.append(build_row(v, baseline, ratio, content_type, row_id))
        existing_urls.add(url)
        row_id += 1

    if not rows:
        print(
            f"Considered {len(candidates)} candidate videos across "
            f"{len(set(channel_ids))} channels. None reached the "
            f"{args.multiplier}x threshold."
        )
        if scored:
            print("\nTop 10 candidates by multiplier (for reference):")
            for ratio, v, baseline in scored[:10]:
                title = first_line(v.get("snippet", {}).get("title", ""), 80)
                channel = v.get("snippet", {}).get("channelTitle", "")
                views = int(v.get("statistics", {}).get("viewCount", 0))
                print(
                    f"  {ratio:5.2f}x  views={views:>10}  baseline={baseline:>9}  "
                    f"{channel} :: {title}"
                )
            print(
                f"\nTo capture these, re-run with "
                f"--multiplier {max(1.5, scored[0][0] * 0.9):.1f}"
            )
        return 0

    append_rows(args.output, rows)
    print(f"Appended {len(rows)} outlier(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
