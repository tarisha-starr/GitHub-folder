"""Fetch post images from a Dropbox shared folder.

Lists the shared folder, sorts files by name, takes the first 20 image
files, and saves them as images/post-01.jpg .. images/post-20.jpg.

The destination extension is forced to .jpg so the filenames match the
`image` field in content/posts.json. Buffer detects the actual MIME from
the file bytes, not the URL extension, so this is safe.

Required env vars:
  DROPBOX_ACCESS_TOKEN   long-lived OAuth token with files.content.read
  DROPBOX_FOLDER_URL     shared link URL to the folder
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

API = "https://api.dropboxapi.com/2"
CONTENT = "https://content.dropboxapi.com/2"

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
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


def main() -> int:
    token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    folder_url = os.environ.get("DROPBOX_FOLDER_URL")
    if not token or not folder_url:
        print(
            "DROPBOX_ACCESS_TOKEN and DROPBOX_FOLDER_URL must be set",
            file=sys.stderr,
        )
        return 1

    IMAGES_DIR.mkdir(exist_ok=True)

    entries = list_files(token, folder_url)
    files = [
        e
        for e in entries
        if e.get(".tag") == "file"
        and Path(e["name"]).suffix.lower() in IMAGE_EXTS
    ]
    files.sort(key=lambda e: e["name"].lower())

    if not files:
        print("No image files found in shared folder", file=sys.stderr)
        return 1

    print(f"Found {len(files)} image file(s) in Dropbox folder")
    if len(files) < 20:
        print(
            f"Warning: only {len(files)} of 20 expected images present",
            file=sys.stderr,
        )

    for i, entry in enumerate(files[:20], start=1):
        dest = IMAGES_DIR / f"post-{i:02d}.jpg"
        path_in_folder = "/" + entry["name"]
        download_file(token, folder_url, path_in_folder, dest)
        print(f"  {entry['name']} -> {dest.name}")

    if len(files) > 20:
        print(f"Skipped {len(files) - 20} extra file(s) beyond post 20")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
