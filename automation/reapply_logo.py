"""Re-apply the real brand logo to existing images.

For each image, opens it, optionally clears the top-right area with
sampled background colour (only for solid-bg cards: journal,
infographics), then overlays images/brand/logo.png on top-right.

For photo posts (images/image-*.jpg), only the logo overlay runs —
no background paint, since photo backgrounds vary.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "images" / "brand" / "logo.png"
JOURNAL_DIR = ROOT / "images" / "journal"
INFOGRAPHIC_DIR = ROOT / "images" / "infographics"
IMAGES_DIR = ROOT / "images"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025


def composite_logo(image_path: Path, logo_path: Path, clear_bg: bool) -> None:
    from PIL import Image, ImageDraw  # type: ignore

    base = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    target_w = int(base.width * LOGO_WIDTH_FRACTION)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)

    margin = int(base.width * LOGO_MARGIN_FRACTION)
    pos = (base.width - target_w - margin, margin)

    if clear_bg:
        sample_box = (10, 10, 60, 60)
        sample = base.crop(sample_box).resize((1, 1), Image.LANCZOS)
        bg = sample.getpixel((0, 0))
        if isinstance(bg, tuple) and len(bg) == 4:
            bg = bg[:3]

        cover_pad = max(20, int(target_w * 0.30))
        cover_box = [
            max(0, pos[0] - cover_pad),
            max(0, pos[1] - cover_pad),
            min(base.width, pos[0] + target_w + cover_pad),
            min(base.height, pos[1] + target_h + cover_pad),
        ]
        draw = ImageDraw.Draw(base)
        draw.rectangle(cover_box, fill=bg)

    base.paste(logo_resized, pos, logo_resized)

    out = io.BytesIO()
    base.convert("RGB").save(out, format="JPEG", quality=92, optimize=True)
    image_path.write_bytes(out.getvalue())


def main() -> int:
    if not LOGO_PATH.exists():
        print(f"Logo not found at {LOGO_PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1

    solid_bg_targets: list[Path] = []
    photo_targets: list[Path] = []

    if JOURNAL_DIR.exists():
        solid_bg_targets.extend(sorted(JOURNAL_DIR.glob("journal-*.jpg")))
    if INFOGRAPHIC_DIR.exists():
        solid_bg_targets.extend(sorted(INFOGRAPHIC_DIR.glob("infographic-*.jpg")))
    if IMAGES_DIR.exists():
        photo_targets.extend(sorted(IMAGES_DIR.glob("image-*.jpg")))

    total = len(solid_bg_targets) + len(photo_targets)
    if total == 0:
        print("No images found to re-apply logo on")
        return 0

    print(
        f"Re-applying logo: {len(solid_bg_targets)} solid-bg "
        f"(paint+overlay), {len(photo_targets)} photos (overlay only)"
    )

    for path in solid_bg_targets:
        try:
            composite_logo(path, LOGO_PATH, clear_bg=True)
            print(f"  {path.relative_to(ROOT)} ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    for path in photo_targets:
        try:
            composite_logo(path, LOGO_PATH, clear_bg=False)
            print(f"  {path.relative_to(ROOT)} ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
