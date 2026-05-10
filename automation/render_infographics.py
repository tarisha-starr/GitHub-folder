"""Pillow-based infographic renderer (NO AI).

For each entry in content/infographics.json that has a layout_type and
structured data, render the infographic precisely using Pillow. No
OpenAI calls, no text errors, no surprises.

Currently supported layout_type values:
- "compare"  : two-column comparison (LEFT vs RIGHT, each with icon,
                label, subtitle, bullet items, plus a centred bottom band).

Entries without layout_type are skipped (the AI generator handles those).

Required env vars:
  ONLY_ID   optional, integer 1..30. Render only that one entry.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFOGRAPHICS_PATH = ROOT / "content" / "infographics.json"
OUT_DIR = ROOT / "images" / "infographics"
LOGO_BURGUNDY = ROOT / "images" / "brand" / "logo-burgundy.png"

CANVAS_W = 1024
CANVAS_H = 1280

# Brand palette (RGB)
BG_BLUSH = (244, 217, 214)
NAVY = (31, 42, 68)
BURGUNDY = (116, 34, 79)
GOLD = (194, 164, 109)
TEAL = (140, 174, 167)
CREAM = (244, 239, 230)

FOOTER_H = int(CANVAS_H * 0.06)
WEBSITE = "sexualempowermentforwomen.com"
LOGO_W_FRAC = 0.10
LOGO_MARGIN_FRAC = 0.025

FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
FONT_ITALIC = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
]


def get_font(size: int, weight: str = "regular"):
    from PIL import ImageFont
    candidates = {
        "bold": FONT_BOLD,
        "italic": FONT_ITALIC,
        "regular": FONT_REG,
    }[weight]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_heart(draw, cx: int, cy: int, size: int, color):
    r = size // 2
    draw.ellipse([cx - r, cy - r // 2, cx, cy + r // 2], fill=color)
    draw.ellipse([cx, cy - r // 2, cx + r, cy + r // 2], fill=color)
    draw.polygon(
        [(cx - r + 2, cy + r // 2 - 2), (cx + r - 2, cy + r // 2 - 2), (cx, cy + r + r // 2)],
        fill=color,
    )


def draw_shield(draw, cx: int, cy: int, size: int, color):
    r = size // 2
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=color)
    draw.polygon([(cx - r, cy), (cx + r, cy), (cx, cy + r + r // 2)], fill=color)


def draw_flourish(draw, cx: int, cy: int, width: int, color):
    """Simple gold horizontal divider with a small diamond in the middle."""
    half = width // 2
    draw.line([(cx - half, cy), (cx - 18, cy)], fill=color, width=2)
    draw.line([(cx + 18, cy), (cx + half, cy)], fill=color, width=2)
    draw.polygon(
        [(cx - 8, cy), (cx, cy - 6), (cx + 8, cy), (cx, cy + 6)],
        fill=color,
    )


def overlay_logo(canvas):
    if not LOGO_BURGUNDY.exists():
        return canvas
    from PIL import Image
    logo = Image.open(LOGO_BURGUNDY).convert("RGBA")
    target_w = int(CANVAS_W * LOGO_W_FRAC)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
    margin = int(CANVAS_W * LOGO_MARGIN_FRAC)
    rgba = canvas.convert("RGBA")
    rgba.paste(logo_resized, (CANVAS_W - target_w - margin, margin), logo_resized)
    return rgba.convert("RGB")


def draw_footer(canvas):
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, CANVAS_H - FOOTER_H), (CANVAS_W, CANVAS_H)], fill=NAVY)
    font = get_font(int(FOOTER_H * 0.40), weight="bold")
    bbox = draw.textbbox((0, 0), WEBSITE, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (CANVAS_W - text_w) // 2
    y = CANVAS_H - FOOTER_H + (FOOTER_H - text_h) // 2 - bbox[1]
    draw.text((x, y), WEBSITE, font=font, fill=CREAM)


def render_compare(entry: dict, dest: Path) -> None:
    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_BLUSH)
    draw = ImageDraw.Draw(canvas)

    margin = 50
    y = 70

    # Title
    title = entry.get("title", "")
    title_font = get_font(50, weight="bold")
    title_lines = wrap_text(draw, title, title_font, CANVAS_W - 2 * margin)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (CANVAS_W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=title_font, fill=NAVY)
        y += int((bbox[3] - bbox[1]) * 1.15)

    y += 18
    draw_flourish(draw, CANVAS_W // 2, y, 240, GOLD)
    y += 30

    structured = entry.get("structured", {})
    left = structured.get("left", {})
    right = structured.get("right", {})

    col_w = (CANVAS_W - 3 * margin) // 2
    left_x = margin
    right_x = margin + col_w + margin

    # Icons
    icon_size = 50
    icon_y = y + icon_size // 2 + 10
    if left.get("icon") == "heart":
        draw_heart(draw, left_x + col_w // 2, icon_y, icon_size, BURGUNDY)
    elif left.get("icon") == "shield":
        draw_shield(draw, left_x + col_w // 2, icon_y, icon_size, TEAL)
    if right.get("icon") == "shield":
        draw_shield(draw, right_x + col_w // 2, icon_y, icon_size, TEAL)
    elif right.get("icon") == "heart":
        draw_heart(draw, right_x + col_w // 2, icon_y, icon_size, BURGUNDY)

    label_y = icon_y + icon_size + 10

    # Headers
    header_font = get_font(38, weight="bold")
    for col, x_center, color in [
        (left, left_x + col_w // 2, BURGUNDY),
        (right, right_x + col_w // 2, TEAL if right.get("icon") == "shield" else BURGUNDY),
    ]:
        label = col.get("label", "").upper()
        bbox = draw.textbbox((0, 0), label, font=header_font)
        draw.text((x_center - (bbox[2] - bbox[0]) // 2, label_y), label, font=header_font, fill=color)

    sub_y = label_y + 50

    # Subtitles (italic)
    subtitle_font = get_font(22, weight="italic")
    sub_y_left = sub_y_right = sub_y
    for col, x_center, sub_y_var_holder in [
        (left, left_x + col_w // 2, "left"),
        (right, right_x + col_w // 2, "right"),
    ]:
        sub = col.get("subtitle", "")
        cur_y = sub_y
        if sub:
            sub_lines = wrap_text(draw, sub, subtitle_font, col_w - 20)
            for line in sub_lines:
                bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                draw.text((x_center - (bbox[2] - bbox[0]) // 2, cur_y), line, font=subtitle_font, fill=NAVY)
                cur_y += int(22 * 1.3)
        if sub_y_var_holder == "left":
            sub_y_left = cur_y
        else:
            sub_y_right = cur_y

    items_y = max(sub_y_left, sub_y_right) + 30

    # Body bullets
    body_font = get_font(22)
    for col, x_start, bullet_color in [
        (left, left_x, BURGUNDY),
        (right, right_x, TEAL if right.get("icon") == "shield" else BURGUNDY),
    ]:
        cur_y = items_y
        items = col.get("items", [])
        for item in items:
            # bullet circle
            draw.ellipse(
                [x_start, cur_y + 9, x_start + 12, cur_y + 21],
                fill=bullet_color,
            )
            text_x = x_start + 22
            text_w = col_w - 22
            lines = wrap_text(draw, item, body_font, text_w)
            for line in lines:
                draw.text((text_x, cur_y), line, font=body_font, fill=NAVY)
                cur_y += int(22 * 1.35)
            cur_y += 6

    # Bottom band
    bb = structured.get("bottom_band", "")
    if bb:
        bb_font = get_font(22, weight="italic")
        bb_lines = wrap_text(draw, bb, bb_font, CANVAS_W - 2 * margin)
        bb_total_h = sum(int(22 * 1.4) for _ in bb_lines) + 30
        bb_y = CANVAS_H - FOOTER_H - bb_total_h
        draw_flourish(draw, CANVAS_W // 2, bb_y - 14, 200, GOLD)
        for line in bb_lines:
            bbox = draw.textbbox((0, 0), line, font=bb_font)
            draw.text(
                ((CANVAS_W - (bbox[2] - bbox[0])) // 2, bb_y),
                line, font=bb_font, fill=BURGUNDY,
            )
            bb_y += int(22 * 1.4)

    draw_footer(canvas)
    canvas = overlay_logo(canvas)
    canvas.save(dest, format="JPEG", quality=92, optimize=True)


RENDERERS = {
    "compare": render_compare,
}


def main() -> int:
    only_id_raw = os.environ.get("ONLY_ID", "").strip()
    only_id = None
    if only_id_raw and only_id_raw not in ("0", "all"):
        try:
            only_id = int(only_id_raw)
        except ValueError:
            pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with INFOGRAPHICS_PATH.open(encoding="utf-8") as f:
        entries = json.load(f)
    if only_id is not None:
        entries = [e for e in entries if int(e["id"]) == only_id]

    rendered: list[int] = []
    unsupported: list[int] = []

    for entry in entries:
        layout_type = entry.get("layout_type")
        if not layout_type or layout_type not in RENDERERS:
            unsupported.append(int(entry["id"]))
            continue
        idx = int(entry["id"])
        dest = OUT_DIR / f"infographic-{idx}.jpg"
        print(f"Rendering infographic-{idx} ({entry.get('title', '')}) [{layout_type}]")
        try:
            RENDERERS[layout_type](entry, dest)
            rendered.append(idx)
        except Exception as e:
            print(f"FAILED infographic-{idx}: {e}", file=sys.stderr)

    print(f"Rendered: {rendered}")
    if unsupported:
        print(
            f"Skipped (no layout_type or unsupported): {unsupported}\n"
            f"Currently supported: {list(RENDERERS.keys())}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
