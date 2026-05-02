"""Convert each images/image-N.jpg into videos/video-N.mp4.

Uses ffmpeg to build a 7-second 1080x1920 (9:16) Reels/TikTok clip with:
- The original image scaled to fit (no cropping or distortion)
- A blurred copy of the same image filling the 9:16 background bars
- A slow Ken Burns zoom-in effect
- A silent stereo audio track (TikTok requires audio)

Idempotent: skips images whose video already exists. On any ffmpeg
failure, writes videos/_diagnostic.json with the error so it can be
read directly from the repo without log inspection.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
VIDEOS_DIR = ROOT / "videos"
DIAGNOSTIC_PATH = VIDEOS_DIR / "_diagnostic.json"

DURATION_SEC = 7
FPS = 30
WIDTH = 1080
HEIGHT = 1920
ZOOM_END = 1.18  # final zoom factor; 1.0 = no zoom


def write_diagnostic(payload: dict) -> None:
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )


def build_video(image_path: Path, video_path: Path) -> tuple[bool, str]:
    """Render a 9:16 zoom-in MP4. Returns (ok, stderr_tail)."""
    frames = DURATION_SEC * FPS
    zoom_step = (ZOOM_END - 1.0) / frames

    filter_complex = (
        # Split the input so we can use it twice
        "[0:v]split=2[bg][fg];"
        # Background: scale to FILL 9:16 (cropping if needed) then blur
        f"[bg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},boxblur=24:3[blurred];"
        # Foreground: scale to FIT inside 9:16 without cropping
        f"[fg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease[scaled];"
        # Composite scaled image onto blurred background
        f"[blurred][scaled]overlay=(W-w)/2:(H-h)/2,"
        # Slow zoom-in over the whole duration
        f"zoompan=z='min(zoom+{zoom_step:.6f},{ZOOM_END})':"
        f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        "format=yuv420p"
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
        "-filter_complex",
        filter_complex,
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
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr[-2000:] if proc.stderr else "(no stderr)"
    return True, ""


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
        write_diagnostic({"error": "images/ directory not found"})
        return 1
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    images = discover_images()
    if not images:
        msg = "No image-N.jpg files found in images/"
        print(msg, file=sys.stderr)
        write_diagnostic({"error": msg})
        return 1

    built = 0
    skipped = 0
    failures: list[dict] = []
    for n, src in images:
        dest = VIDEOS_DIR / f"video-{n}.mp4"
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        print(f"Building {dest.name} from {src.name}…")
        ok, stderr_tail = build_video(src, dest)
        if not ok:
            failures.append({"image": src.name, "stderr": stderr_tail})
            print(f"FAILED {src.name}: {stderr_tail[:300]}", file=sys.stderr)
            # Remove any half-written file
            if dest.exists():
                dest.unlink()
            continue
        built += 1

    write_diagnostic(
        {
            "built": built,
            "skipped": skipped,
            "failed": len(failures),
            "failures": failures,
            "ffmpeg_filter_summary": (
                f"split → blur+crop {WIDTH}x{HEIGHT} bg, "
                f"fit-scale fg, overlay, zoompan to {ZOOM_END}x"
            ),
        }
    )
    print(f"Built {built}; skipped {skipped}; failed {len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
