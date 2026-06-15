"""Fetch post images from a Dropbox shared folder, in two phases.

Phase 1 (always runs): downloads every image in the shared folder to
images/raw/<original-name>. This lets you see what's there before
deciding which image goes with which post.

Phase 2 (runs if images/mapping.json exists): reads the mapping and
creates images/image-N.jpg copies for each entry, matching the `image`
field in content/posts.json.

mapping.json format:
  {
    "Original Filename From Dropbox.jpg": 1,
    "Another File.png": 2,
    ...
  }
The value is the post id (1..20). The destination extension is forced
to .jpg so it matches posts.json. Buffer detects MIME from file bytes,
not the URL extension, so this is safe even for sources that were PNG.

Required env vars:
  DROPBOX_ACCESS_TOKEN   long-lived OAuth token with files.content.read
  DROPBOX_FOLDER_URL     shared link URL to the folder

Diagnostics: any error from the Dropbox API is also written to
images/_diagnostic.json so it can be inspected without reading workflow
logs.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.dropboxapi.com/2"
CONTENT = "https://content.dropboxapi.com/2"

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
RAW_DIR = IMAGES_DIR / "raw"
INFOGRAPHIC_DIR = IMAGES_DIR / "infographics"
VIDEOS_DIR = ROOT / "videos"
INFOGRAPHIC_VIDEO_DIR = VIDEOS_DIR / "infographics"
MAPPING_PATH = IMAGES_DIR / "mapping.json"
DIAGNOSTIC_PATH = IMAGES_DIR / "_diagnostic.json"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}
ALL_EXTS = IMAGE_EXTS | VIDEO_EXTS

INFOGRAPHIC_IMAGE_RE = re.compile(r"^infographic-(\d+)\.(jpg|jpeg|png|webp|heic)$", re.IGNORECASE)
INFOGRAPHIC_VIDEO_RE = re.compile(
    r"^infographic[-_]?(?:reel[-_]?)?(\d+)(?:[-_]reel)?\.(mp4|mov|m4v|webm)$",
    re.IGNORECASE,
)
# Back-compat alias used elsewhere in the file
INFOGRAPHIC_RE = INFOGRAPHIC_IMAGE_RE


def write_diagnostic(payload: dict) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )


def post_json(url: str, token: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_files(token: str, folder_url: str) -> list[dict]:
    body = {"path": "", "shared_link": {"url": folder_url}}
    result = post_json(f"{API}/files/list_folder", token, body)
    entries = list(result.get("entries", []))
    while result.get("has_more"):
        result = post_json(
            f"{API}/files/list_folder/continue",
            token,
            {"cursor": result["cursor"]},
        )
        entries.extend(result.get("entries", []))
    return entries


def download_file(token: str, folder_url: str, path_in_folder: str, dest: Path) -> None:
    req = urllib.request.Request(
        f"{CONTENT}/sharing/get_shared_link_file",
        headers={
            "Authorization": f"Bearer {token}",
            "Dropbox-API-Arg": json.dumps(
                {"url": folder_url, "path": path_in_folder}
            ),
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f.write(chunk)


def phase_one_download_raw(token: str, folder_url: str) -> list[str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    try:
        entries = list_files(token, folder_url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        write_diagnostic(
            {
                "phase": "list_folder",
                "status": e.code,
                "reason": e.reason,
                "body": body,
                "folder_url_set": bool(folder_url),
                "token_set": bool(token),
            }
        )
        print(f"list_folder failed: {e.code} {e.reason}\n{body}", file=sys.stderr)
        raise

    image_entries = [
        e
        for e in entries
        if e.get(".tag") == "file"
        and Path(e["name"]).suffix.lower() in ALL_EXTS
    ]
    image_entries.sort(key=lambda e: e["name"].lower())

    write_diagnostic(
        {
            "phase": "list_folder_ok",
            "total_entries": len(entries),
            "image_entries": len(image_entries),
            "names": [e["name"] for e in image_entries],
        }
    )

    if not image_entries:
        print("No image files found in shared folder", file=sys.stderr)
        return []

    print(f"Phase 1: downloading {len(image_entries)} image(s) to images/raw/")
    saved: list[str] = []
    for entry in image_entries:
        name = entry["name"]
        dest = RAW_DIR / name
        try:
            download_file(token, folder_url, "/" + name, dest)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            write_diagnostic(
                {
                    "phase": "download_file",
                    "name": name,
                    "status": e.code,
                    "reason": e.reason,
                    "body": body,
                }
            )
            print(f"download {name} failed: {e.code} {e.reason}\n{body}", file=sys.stderr)
            raise
        saved.append(name)
        print(f"  {name}  ({entry.get('size', '?')} bytes)")
    return saved


def _save_as_jpeg(src: Path, dest: Path) -> None:
    """Copy src to dest. If src isn't already JPEG, try Pillow re-encode;
    fall back to a plain copy if Pillow isn't available (Buffer/Zapier
    sniff MIME from bytes, so a PNG renamed to .jpg still works for
    most consumers, but a true JPEG is preferred)."""
    if src.suffix.lower() in {".jpg", ".jpeg"}:
        shutil.copyfile(src, dest)
        return
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        shutil.copyfile(src, dest)
        return
    with Image.open(src) as im:
        rgb = im.convert("RGB")
        out = io.BytesIO()
        rgb.save(out, format="JPEG", quality=92, optimize=True)
        dest.write_bytes(out.getvalue())


def phase_three_route_infographics(saved: list[str]) -> None:
    """Route any infographic-N.* files in raw/ to the right place.

    Images (infographic-N.{jpg,png,webp,heic}) go to images/infographics/.
    Videos / Reels (infographic-N.{mp4,mov,m4v,webm}, with optional
    "-reel" or "reel-" in the name) go to videos/infographics/.

    The user drops finished infographics and their matching Reels into
    the same Dropbox folder as daily photo posts. This phase moves them
    where the daily Zapier push expects to find them.
    """
    INFOGRAPHIC_DIR.mkdir(parents=True, exist_ok=True)
    INFOGRAPHIC_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    routed_images = 0
    routed_videos = 0
    skipped: list[str] = []

    for name in saved:
        m_img = INFOGRAPHIC_IMAGE_RE.match(name)
        if m_img:
            idx = int(m_img.group(1))
            src = RAW_DIR / name
            dest = INFOGRAPHIC_DIR / f"infographic-{idx}.jpg"
            try:
                _save_as_jpeg(src, dest)
                print(f"  {name} -> {dest.relative_to(ROOT)}")
                routed_images += 1
            except Exception as e:
                skipped.append(f"{name}: {e}")
            continue

        m_vid = INFOGRAPHIC_VIDEO_RE.match(name)
        if m_vid:
            idx = int(m_vid.group(1))
            src = RAW_DIR / name
            dest = INFOGRAPHIC_VIDEO_DIR / f"infographic-{idx}.mp4"
            try:
                shutil.copyfile(src, dest)
                print(f"  {name} -> {dest.relative_to(ROOT)}")
                routed_videos += 1
            except Exception as e:
                skipped.append(f"{name}: {e}")
            continue

    if routed_images == 0 and routed_videos == 0 and not skipped:
        print(
            "\nPhase 3: no infographic-N.* files found in raw/. "
            "Skip (this is fine if you only uploaded daily photos)."
        )
        return
    print(
        f"\nPhase 3: routed {routed_images} infographic image(s) to images/infographics/, "
        f"{routed_videos} reel(s) to videos/infographics/"
    )
    for line in skipped:
        print(f"  SKIPPED {line}", file=sys.stderr)


def phase_two_apply_mapping(saved: list[str]) -> None:
    if not MAPPING_PATH.exists():
        print(
            "\nPhase 2 skipped: images/mapping.json not present yet.\n"
            "Inspect images/raw/, then create images/mapping.json mapping each\n"
            "original filename to a post id (1..20), and re-run the workflow."
        )
        return

    with MAPPING_PATH.open(encoding="utf-8") as f:
        mapping: dict[str, int] = json.load(f)

    print(f"\nPhase 2: applying mapping for {len(mapping)} entries")
    saved_lookup = {s.lower(): s for s in saved}
    for original, post_id in mapping.items():
        match = saved_lookup.get(original.lower())
        if not match:
            print(f"  SKIP {original} -> image-{post_id}.jpg (not in raw/)")
            continue
        src = RAW_DIR / match
        dest = IMAGES_DIR / f"image-{int(post_id)}.jpg"
        shutil.copyfile(src, dest)
        print(f"  {match} -> {dest.name}")


def main() -> int:
    token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    folder_url = os.environ.get("DROPBOX_FOLDER_URL")
    if not token or not folder_url:
        write_diagnostic(
            {
                "phase": "config",
                "token_set": bool(token),
                "folder_url_set": bool(folder_url),
                "error": "DROPBOX_ACCESS_TOKEN and DROPBOX_FOLDER_URL must both be set",
            }
        )
        print(
            "DROPBOX_ACCESS_TOKEN and DROPBOX_FOLDER_URL must be set",
            file=sys.stderr,
        )
        return 1

    saved = phase_one_download_raw(token, folder_url)
    if not saved:
        return 1
    phase_two_apply_mapping(saved)
    phase_three_route_infographics(saved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
