"""Convert each images/image-N.jpg into videos/video-N.mp4.

Uses ffmpeg to create a 7-second 1080x1920 (9:16) clip with a slow
center-crop zoom-in (Ken Burns effect) and a silent stereo audio track.
The vertical 9:16 aspect ratio is what Reels and TikTok expect.

The script is idempotent — videos that already exist are skipped, so
you can run it after each new batch of images is downloaded.

Requires: ffmpeg in PATH (ubuntu-latest runners have it pre-installed).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
VIDEOS_DIR = ROOT / "videos"

DURATION_SEC = 7
FPS = 30
WIDTH = 1080
HEIGHT = 1920
ZOOM_END = 1.18  # final zoom factor; 1.0 = no zoom


def build_video(image_path: Path, video_path: Path) -> None:
    """Render a 9:16 zoom-in MP4 from a still image with a silent track."""
    frames = DURATION_SEC * FPS
    zoom_step = (ZOOM_END - 1.0) / frames

    # Pre-scale the image to a large canvas so the zoompan crop is sharp,
    # then center-crop and zoom into the requested 9:16 frame.
    vf = (
        f"scale=2160:-1:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,"
        f"zoompan=z='min(zoom+{zoom_step:.6f},{ZOOM_END})':"
        f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-t",
        str(DURATION_SEC),
        "-shortest",
        "-movflags",
        "+faststart",
        str(video_path),
    ]
    subprocess.run(cmd, check=True)


def discover_images() -> list[tuple[int, Path]]:
    pattern = re.compile(r"^image-(\d+)\.jpg$", re.IGNORECASE)
    found: list[tuple[int, Path]] = []
    for p in sorted(IMAGES_DIR.glob("image-*.jpg")):
        m = pattern.match(p.name)
        if m:
            found.append((int(m.group(1)), p))
    return found


def main() -> int:
    if not IMAGES_DIR.exists():
        print("images/ directory not found", file=sys.stderr)
        return 1
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    images = discover_images()
    if not images:
        print("No image-N.jpg files found in images/", file=sys.stderr)
        return 1

    built = 0
    skipped = 0
    for n, src in images:
        dest = VIDEOS_DIR / f"video-{n}.mp4"
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        print(f"Building {dest.name} from {src.name}…")
        try:
            build_video(src, dest)
            built += 1
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg failed for {src.name}: {e}", file=sys.stderr)
            return 1

    print(f"Built {built} video(s); skipped {skipped} existing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
