"""Render branded text-only post cards with Pillow. NO AI, NO humans.

Each card carries the hook and nothing else, plus the website footer and the
logo. The caption stays out of the image and goes in the post body, so the
hook is never duplicated between image and caption.

Deliberately Pillow rather than an image model:
  - the text is exact, models misspell overlay text constantly
  - no OpenAI billing, which has blocked regeneration before
  - re-running gives byte-identical output, so cards can be regenerated
    after a copy edit without the look drifting

Usage:
    python3 render_post_cards.py                     # all pending drafts
    python3 render_post_cards.py --only 3            # one card
    python3 render_post_cards.py --text "A hook"     # ad-hoc single card
    python3 render_post_cards.py --out images/cards  # different destination
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "content" / "drafts" / "image_post_drafts.json"
LOGO = ROOT / "images" / "brand" / "logo-burgundy.png"
LOGO_GOLD = ROOT / "images" / "brand" / "logo-gold.png"
OUT_DIR = ROOT / "images" / "cards"

CANVAS_W, CANVAS_H = 1024, 1280          # 4:5, matches the rest of the pipeline
WEBSITE = "sexualempowermentforwomen.com"

# Brand palette, lifted from render_infographics.py so the series matches.
BLUSH = (244, 217, 214)
NAVY = (31, 42, 68)
BURGUNDY = (116, 34, 79)
GOLD = (194, 164, 109)
TEAL = (140, 174, 167)
CREAM = (244, 239, 230)

# Rotating schemes give the grid variety without leaving the brand.
# (background, headline colour, accent rule, footer bar, footer text, logo)
SCHEMES = [
    (BLUSH,    BURGUNDY, GOLD,     NAVY,     CREAM, "burgundy"),
    (NAVY,     CREAM,    GOLD,     BURGUNDY, CREAM, "gold"),
    (BURGUNDY, CREAM,    GOLD,     NAVY,     CREAM, "gold"),
    (CREAM,    NAVY,     BURGUNDY, NAVY,     CREAM, "burgundy"),
    (TEAL,     NAVY,     CREAM,    NAVY,     CREAM, "burgundy"),
]

# Lora is the brand face, per content/image_prompt.md. It's a variable font
# (weight 400-700), vendored in automation/fonts/ with its OFL licence so the
# cards render identically in CI without a system font install.
LORA = ROOT / "automation" / "fonts" / "Lora.ttf"

FONT_SERIF_BOLD = [
    str(LORA),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
FONT_SERIF = [
    str(LORA),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]


def get_font(paths: list[str], size: int, variation: str | None = None):
    """Load the first available face. `variation` names a weight on Lora."""
    from PIL import ImageFont
    for p in paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, size)
            if variation:
                try:
                    font.set_variation_by_name(variation)
                except Exception:
                    pass  # static fallback face, nothing to set
            return font
    return ImageFont.load_default()


def straighten(text: str) -> str:
    """Curly quotes render badly and break the brand rule. Force straight."""
    return (text.replace("’", "'").replace("‘", "'")
                .replace("“", '"').replace("”", '"')
                .replace("—", ",").replace("–", ","))


def wrap(draw, text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text: str, max_w: int, max_h: int):
    """Shrink until the hook fits the text box. Long hooks must not overflow."""
    for size in range(86, 33, -2):
        font = get_font(FONT_SERIF_BOLD, size, "SemiBold")
        lines = wrap(draw, text, font, max_w)
        leading = int(size * 1.30)
        if len(lines) * leading <= max_h and len(lines) <= 7:
            return font, lines, leading
    font = get_font(FONT_SERIF_BOLD, 34, "SemiBold")
    return font, wrap(draw, text, font, max_w), int(34 * 1.30)


def render_card(hook: str, dest: Path, scheme_idx: int) -> Path:
    from PIL import Image, ImageDraw

    bg, ink, accent, bar, bar_ink, logo_kind = SCHEMES[scheme_idx % len(SCHEMES)]
    hook = straighten(hook).strip()

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), bg)
    draw = ImageDraw.Draw(canvas)

    footer_h = int(CANVAS_H * 0.075)
    side = int(CANVAS_W * 0.11)
    max_w = CANVAS_W - side * 2

    # Logo, top right, clear of the headline box.
    logo_path = LOGO_GOLD if logo_kind == "gold" else LOGO
    logo_bottom = int(CANVAS_H * 0.055)
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        target_w = int(CANVAS_W * 0.10)
        target_h = int(logo.height * (target_w / logo.width))
        logo = logo.resize((target_w, target_h), Image.LANCZOS)
        margin = int(CANVAS_W * 0.05)
        canvas.paste(logo, (CANVAS_W - target_w - margin, margin), logo)
        logo_bottom = margin + target_h

    # Headline, vertically centred between logo and footer.
    top = logo_bottom + int(CANVAS_H * 0.05)
    bottom = CANVAS_H - footer_h - int(CANVAS_H * 0.06)
    font, lines, leading = fit_headline(draw, hook, max_w, bottom - top)

    block_h = len(lines) * leading
    y = top + max(0, (bottom - top - block_h) // 2)

    # Short accent rule above the headline. No flourishes, they were stripped
    # from the journal cards for being fussy.
    rule_w, rule_h = int(CANVAS_W * 0.10), 3
    draw.rectangle(
        [side, y - int(CANVAS_H * 0.035), side + rule_w, y - int(CANVAS_H * 0.035) + rule_h],
        fill=accent,
    )

    for line in lines:
        draw.text((side, y), line, font=font, fill=ink)
        y += leading

    # Footer bar with the website, centred.
    draw.rectangle([0, CANVAS_H - footer_h, CANVAS_W, CANVAS_H], fill=bar)
    fsize = int(footer_h * 0.34)
    ffont = get_font(FONT_SERIF, fsize, "Medium")
    label = WEBSITE.upper()
    tw = draw.textlength(label, font=ffont)
    bbox = draw.textbbox((0, 0), label, font=ffont)
    draw.text(
        ((CANVAS_W - tw) / 2, CANVAS_H - footer_h + (footer_h - (bbox[3] - bbox[1])) / 2 - bbox[1]),
        label, font=ffont, fill=bar_ink,
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "JPEG", quality=92)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="Render text-only branded post cards")
    ap.add_argument("--only", type=int, help="render a single draft by 1-based index")
    ap.add_argument("--text", help="render one ad-hoc card from this text")
    ap.add_argument("--out", default=str(OUT_DIR), help="output directory")
    ap.add_argument("--start", type=int, default=24,
                    help="first draft index to render (default 24, the 16 July batch)")
    args = ap.parse_args()

    out_dir = Path(args.out)

    if args.text:
        dest = render_card(args.text, out_dir / "card-adhoc.jpg", 0)
        print(f"wrote {dest}")
        return 0

    drafts = json.loads(DRAFTS.read_text(encoding="utf-8"))[args.start:]
    if not drafts:
        print("No drafts to render.")
        return 1

    targets = [(args.only, drafts[args.only - 1])] if args.only else list(enumerate(drafts, 1))

    for i, post in targets:
        dest = render_card(post["hook"], out_dir / f"card-{i:02d}.jpg", i - 1)
        print(f"  {dest.name}  {post['hook'][:58]}")

    print(f"\nRendered {len(targets)} card(s) into {out_dir}")
    print("The hook is on the image, so keep it out of the caption when posting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
