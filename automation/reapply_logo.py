"""Re-apply the right brand logo to existing images.

For solid-bg cards (journal, infographics): clears the top-right with
sampled bg colour, then overlays the appropriate logo variant.
- Journal cards rotate through 5 brand colours (cream, burgundy, gold,
  navy, blush). Burgundy and navy backgrounds get the gold-circle logo
  (logo-gold.png). The other three get the burgundy logo
  (logo-burgundy.png, falling back to logo.png).
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
BRAND_DIR = ROOT / "images" / "brand"
JOURNAL_DIR = ROOT / "images" / "journal"
INFOGRAPHIC_DIR = ROOT / "images" / "infographics"
IMAGES_DIR = ROOT / "images"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025

JOURNAL_BG_ROTATION = ["cream", "burgundy", "gold", "navy", "blush"]
LOGO_FOR_BG = {
    "cream": "burgundy",
    "gold": "burgundy",
    "blush": "burgundy",
    "burgundy": "gold",
    "navy": "gold",
}


def burgundy_logo_path() -> Path | None:
    primary = BRAND_DIR / "logo-burgundy.png"
    if primary.exists():
        return primary
    fallback = BRAND_DIR / "logo.png"
    if fallback.exists():
        return fallback
    return None


def gold_logo_path() -> Path | None:
    primary = BRAND_DIR / "logo-gold.png"
    return primary if primary.exists() else None


def journal_logo_for(idx: int) -> Path | None:
    bg_name = JOURNAL_BG_ROTATION[(idx - 1) % len(JOURNAL_BG_ROTATION)]
    variant = LOGO_FOR_BG.get(bg_name, "burgundy")
    if variant == "gold":
        gold = gold_logo_path()
        if gold:
            return gold
    return burgundy_logo_path()


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
    burgundy = burgundy_logo_path()
    gold = gold_logo_path()
    if burgundy is None:
        print(
            f"No burgundy logo found in {BRAND_DIR.relative_to(ROOT)} "
            "(expected logo-burgundy.png or logo.png). Cannot proceed.",
            file=sys.stderr,
        )
        return 1
    if gold is None:
        print("Note: logo-gold.png not found; dark-bg journal cards will use the burgundy logo.")

    journal_targets = sorted(JOURNAL_DIR.glob("journal-*.jpg")) if JOURNAL_DIR.exists() else []
    infographic_targets = sorted(INFOGRAPHIC_DIR.glob("infographic-*.jpg")) if INFOGRAPHIC_DIR.exists() else []
    photo_targets = sorted(IMAGES_DIR.glob("image-*.jpg")) if IMAGES_DIR.exists() else []

    total = len(journal_targets) + len(infographic_targets) + len(photo_targets)
    if total == 0:
        print("No images found to re-apply logo on")
        return 0

    print(
        f"Re-applying logos: {len(journal_targets)} journal, "
        f"{len(infographic_targets)} infographics, {len(photo_targets)} photos"
    )
    print(f"  burgundy: {burgundy.name}, gold: {gold.name if gold else '(missing)'}")

    for path in journal_targets:
        idx = journal_index(path)
        logo_path = journal_logo_for(idx) if idx is not None else burgundy
        if logo_path is None:
            print(f"  {path.relative_to(ROOT)} SKIPPED: no usable logo", file=sys.stderr)
            continue
        try:
            composite_logo(path, logo_path, clear_bg=True)
            print(f"  {path.relative_to(ROOT)} ({logo_path.name}) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    for path in infographic_targets:
        try:
            composite_logo(path, burgundy, clear_bg=True)
            print(f"  {path.relative_to(ROOT)} ({burgundy.name}) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    for path in photo_targets:
        try:
            composite_logo(path, burgundy, clear_bg=False)
            print(f"  {path.relative_to(ROOT)} ({burgundy.name}) ✓")
        except Exception as e:
            print(f"  {path.relative_to(ROOT)} FAILED: {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
