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
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

API = "https://api.dropboxapi.com/2"
CONTENT = "https://content.dropboxapi.com/2"

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
RAW_DIR = IMAGES_DIR / "raw"
MAPPING_PATH = IMAGES_DIR / "mapping.json"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


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
    entries = list_files(token, folder_url)
    image_entries = [
        e
        for e in entries
        if e.get(".tag") == "file"
        and Path(e["name"]).suffix.lower() in IMAGE_EXTS
    ]
    image_entries.sort(key=lambda e: e["name"].lower())

    if not image_entries:
        print("No image files found in shared folder", file=sys.stderr)
        return []

    print(f"Phase 1: downloading {len(image_entries)} image(s) to images/raw/")
    saved: list[str] = []
    for entry in image_entries:
        name = entry["name"]
        dest = RAW_DIR / name
        download_file(token, folder_url, "/" + name, dest)
        saved.append(name)
        print(f"  {name}  ({entry.get('size', '?')} bytes)")
    return saved


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
        print(
            "DROPBOX_ACCESS_TOKEN and DROPBOX_FOLDER_URL must be set",
            file=sys.stderr,
        )
        return 1

    saved = phase_one_download_raw(token, folder_url)
    if not saved:
        return 1
    phase_two_apply_mapping(saved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
