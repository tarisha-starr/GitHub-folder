"""Re-apply the real brand logo to existing images.

Walks images/journal/journal-*.jpg and images/image-*.jpg. For each
file, opens it, overlays images/brand/logo.png on the top-right
corner, and writes the result back. Idempotent on the file format
but each run re-composites — so don't run repeatedly without intent.

Use this once after uploading a new logo to catch existing AI-generated
images that have an outdated or wrong logo.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / "brand" / "logo.png"
JOURNAL_DIR = ROOT / "images" / "journal"
IMAGES_DIR = ROOT / "images"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025


def composite_logo(image_path: Path, logo_path: Path) -> None:
    from PIL import Image  # type: ignore

    base = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    target_w = int(base.width * LOGO_WIDTH_FRACTION)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)

    margin = int(base.width * LOGO_MARGIN_FRACTION)
    pos = (base.width - target_w - margin, margin)

    base.paste(logo_resized, pos, logo_resized)

    out = io.BytesIO()
    base.convert("RGB").save(out, format="JPEG", quality=92, optimize=True)
    image_path.write_bytes(out.getvalue())


def main() -> int:
    if not LOGO_PATH.exists():
        print(f"Logo not found at {LOGO_PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1

    targets: list[Path] = []
    if JOURNAL_DIR.exists():
        targets.extend(sorted(JOURNAL_DIR.glob("journal-*.jpg")))
    if IMAGES_DIR.exists():
        targets.extend(sorted(IMAGES_DIR.glob("image-*.jpg")))

    if not targets:
        print("No images found to re-apply logo on")
        return 0

    print(f"Re-applying logo to {len(targets)} image(s)…")
    for path in targets:
        try:
            composite_logo(path, LOGO_PATH)
            print(f"  {path.relative_to(ROOT)} ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
