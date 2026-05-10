"""Re-apply the real brand logo to existing images.

For solid-bg cards (journal, infographics): clears the top-right with
sampled bg colour, then overlays the appropriate logo variant.
- Journal cards rotate through 5 brand colours (cream, burgundy, gold,
  navy, blush). Burgundy and navy backgrounds get the gold-circle logo
  (logo-gold.png). The other three get the burgundy logo (logo.png).
- Infographic cards have a single blush bg, always burgundy logo.

For photo posts (images/image-*.jpg), only the burgundy logo is
overlaid — no bg paint, since photo backgrounds vary.
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGO_DARK_PATH = ROOT / "images" / "brand" / "logo.png"        # burgundy circle
LOGO_LIGHT_PATH = ROOT / "images" / "brand" / "logo-gold.png"  # gold circle
JOURNAL_DIR = ROOT / "images" / "journal"
INFOGRAPHIC_DIR = ROOT / "images" / "infographics"
IMAGES_DIR = ROOT / "images"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025

# Same rotation as in generate_journal_images.py
JOURNAL_BG_ROTATION = ["cream", "burgundy", "gold", "navy", "blush"]
LOGO_FOR_BG = {
    "cream": "dark",
    "gold": "dark",
    "blush": "dark",
    "burgundy": "light",
    "navy": "light",
}


def journal_logo_for(idx: int) -> Path:
    bg_name = JOURNAL_BG_ROTATION[(idx - 1) % len(JOURNAL_BG_ROTATION)]
    variant = LOGO_FOR_BG.get(bg_name, "dark")
    if variant == "light" and LOGO_LIGHT_PATH.exists():
        return LOGO_LIGHT_PATH
    return LOGO_DARK_PATH


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


def journal_index(path: Path) -> int | None:
    m = re.match(r"^journal-(\d+)\.jpg$", path.name, re.IGNORECASE)
    return int(m.group(1)) if m else None


def main() -> int:
    if not LOGO_DARK_PATH.exists():
        print(f"Logo not found at {LOGO_DARK_PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if not LOGO_LIGHT_PATH.exists():
        print(
            f"Note: logo-gold.png not found; dark-bg journal cards will fall "
            f"back to the burgundy logo."
        )

    journal_targets: list[Path] = sorted(JOURNAL_DIR.glob("journal-*.jpg")) if JOURNAL_DIR.exists() else []
    infographic_targets: list[Path] = sorted(INFOGRAPHIC_DIR.glob("infographic-*.jpg")) if INFOGRAPHIC_DIR.exists() else []
    photo_targets: list[Path] = sorted(IMAGES_DIR.glob("image-*.jpg")) if IMAGES_DIR.exists() else []

    total = len(journal_targets) + len(infographic_targets) + len(photo_targets)
    if total == 0:
        print("No images found to re-apply logo on")
        return 0

    print(
        f"Re-applying logos: {len(journal_targets)} journal, "
        f"{len(infographic_targets)} infographics, {len(photo_targets)} photos"
    )

    for path in journal_targets:
        idx = journal_index(path)
        logo_path = journal_logo_for(idx) if idx is not None else LOGO_DARK_PATH
        try:
            composite_logo(path, logo_path, clear_bg=True)
            print(f"  {path.relative_to(ROOT)} ({logo_path.name}) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    for path in infographic_targets:
        try:
            composite_logo(path, LOGO_DARK_PATH, clear_bg=True)
            print(f"  {path.relative_to(ROOT)} (logo.png) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    for path in photo_targets:
        try:
            composite_logo(path, LOGO_DARK_PATH, clear_bg=False)
            print(f"  {path.relative_to(ROOT)} (logo.png) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
