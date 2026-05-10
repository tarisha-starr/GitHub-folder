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
LOGO_W_FRAC = 0.085
LOGO_MARGIN_FRAC = 0.022

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


def _supersample_paste(canvas, cx: int, cy: int, size: int, draw_fn, color, scale: int = 4):
    """Render a small icon at scale x then downsample for smooth edges."""
    from PIL import Image, ImageDraw
    big = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    big_draw = ImageDraw.Draw(big)
    draw_fn(big_draw, size * scale, color)
    small = big.resize((size, size), Image.LANCZOS)
    canvas.paste(small, (cx - size // 2, cy - size // 2), small)


def _heart_polygon(s: int):
    """Polygon points for a smooth heart filling an s x s box."""
    import math
    pts = []
    lx_l, lx_r, ly = s * 0.30, s * 0.70, s * 0.32
    radius = s * 0.22
    # Left lobe: top arc from rightmost (centre dip) sweeping left
    for deg in range(0, 181, 8):
        rad = math.radians(180 - deg)
        pts.append((lx_l + radius * math.cos(rad), ly - radius * math.sin(rad)))
    # Left side curve down to tip via quadratic bezier
    left_top = (lx_l - radius, ly)
    p_left_ctrl = (s * 0.04, s * 0.55)
    p_tip = (s * 0.5, s * 0.96)
    for t in [i / 14 for i in range(1, 15)]:
        x = (1 - t) ** 2 * left_top[0] + 2 * (1 - t) * t * p_left_ctrl[0] + t ** 2 * p_tip[0]
        y = (1 - t) ** 2 * left_top[1] + 2 * (1 - t) * t * p_left_ctrl[1] + t ** 2 * p_tip[1]
        pts.append((x, y))
    # Right side back up to right lobe
    right_top = (lx_r + radius, ly)
    p_right_ctrl = (s * 0.96, s * 0.55)
    for t in [i / 14 for i in range(1, 15)]:
        x = (1 - t) ** 2 * p_tip[0] + 2 * (1 - t) * t * p_right_ctrl[0] + t ** 2 * right_top[0]
        y = (1 - t) ** 2 * p_tip[1] + 2 * (1 - t) * t * p_right_ctrl[1] + t ** 2 * right_top[1]
        pts.append((x, y))
    # Right lobe arc
    for deg in range(0, 181, 8):
        rad = math.radians(deg)
        pts.append((lx_r + radius * math.cos(rad), ly - radius * math.sin(rad)))
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _flame_polygon(s: int):
    """Smooth flame: pointed at top, rounded base, slight asymmetric flicker."""
    import math
    pts = []
    tip = (s * 0.5, s * 0.04)
    left_w = (s * 0.16, s * 0.62)
    right_w = (s * 0.84, s * 0.62)
    bottom_l = (s * 0.30, s * 0.94)
    bottom_r = (s * 0.70, s * 0.94)
    # Left side: tip → left_w (bezier with inward control near top, outward midway)
    ctrl_l1 = (s * 0.42, s * 0.20)
    ctrl_l2 = (s * 0.20, s * 0.42)
    for t in [i / 18 for i in range(0, 19)]:
        # cubic bezier
        x = ((1 - t) ** 3 * tip[0]
             + 3 * (1 - t) ** 2 * t * ctrl_l1[0]
             + 3 * (1 - t) * t ** 2 * ctrl_l2[0]
             + t ** 3 * left_w[0])
        y = ((1 - t) ** 3 * tip[1]
             + 3 * (1 - t) ** 2 * t * ctrl_l1[1]
             + 3 * (1 - t) * t ** 2 * ctrl_l2[1]
             + t ** 3 * left_w[1])
        pts.append((x, y))
    # Left bottom curve
    ctrl_lb = (s * 0.10, s * 0.86)
    for t in [i / 12 for i in range(1, 13)]:
        x = (1 - t) ** 2 * left_w[0] + 2 * (1 - t) * t * ctrl_lb[0] + t ** 2 * bottom_l[0]
        y = (1 - t) ** 2 * left_w[1] + 2 * (1 - t) * t * ctrl_lb[1] + t ** 2 * bottom_l[1]
        pts.append((x, y))
    # Bottom rounded arc (squashed half-ellipse)
    cx_b = (bottom_l[0] + bottom_r[0]) / 2
    cy_b = (bottom_l[1] + bottom_r[1]) / 2
    rx = (bottom_r[0] - bottom_l[0]) / 2
    ry = rx * 0.45
    for deg in range(180, 361, 10):
        rad = math.radians(deg)
        pts.append((cx_b + rx * math.cos(rad), cy_b - ry * math.sin(rad)))
    # Right bottom curve
    ctrl_rb = (s * 0.90, s * 0.86)
    for t in [i / 12 for i in range(1, 13)]:
        x = (1 - t) ** 2 * bottom_r[0] + 2 * (1 - t) * t * ctrl_rb[0] + t ** 2 * right_w[0]
        y = (1 - t) ** 2 * bottom_r[1] + 2 * (1 - t) * t * ctrl_rb[1] + t ** 2 * right_w[1]
        pts.append((x, y))
    # Right side back to tip
    ctrl_r1 = (s * 0.80, s * 0.42)
    ctrl_r2 = (s * 0.58, s * 0.20)
    for t in [i / 18 for i in range(1, 19)]:
        x = ((1 - t) ** 3 * right_w[0]
             + 3 * (1 - t) ** 2 * t * ctrl_r1[0]
             + 3 * (1 - t) * t ** 2 * ctrl_r2[0]
             + t ** 3 * tip[0])
        y = ((1 - t) ** 3 * right_w[1]
             + 3 * (1 - t) ** 2 * t * ctrl_r1[1]
             + 3 * (1 - t) * t ** 2 * ctrl_r2[1]
             + t ** 3 * tip[1])
        pts.append((x, y))
    return [(int(round(x)), int(round(y))) for x, y in pts]


def draw_heart(canvas, cx: int, cy: int, size: int, color):
    def _do(d, s, c):
        d.polygon(_heart_polygon(s), fill=c)
    _supersample_paste(canvas, cx, cy, size, _do, color)


def draw_flame(canvas, cx: int, cy: int, size: int, color):
    def _do(d, s, c):
        d.polygon(_flame_polygon(s), fill=c)
    _supersample_paste(canvas, cx, cy, size, _do, color)


def draw_flourish(draw, cx: int, cy: int, width: int, color):
    """Simple gold horizontal divider with a small diamond in the middle."""
    half = width // 2
    draw.line([(cx - half, cy), (cx - 16, cy)], fill=color, width=2)
    draw.line([(cx + 16, cy), (cx + half, cy)], fill=color, width=2)
    draw.polygon(
        [(cx - 7, cy), (cx, cy - 5), (cx + 7, cy), (cx, cy + 5)],
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

    margin = 60

    # Logo zone reserves vertical space at the top right; title sits below it
    logo_w = int(CANVAS_W * LOGO_W_FRAC)
    logo_margin = int(CANVAS_W * LOGO_MARGIN_FRAC)
    # Approximate logo height (square logo) plus its margin
    logo_zone_h = logo_w + logo_margin * 2

    title = entry.get("title", "")
    title_font = get_font(58, weight="bold")

    # Centre block: title + flourish + body. Compute positions.
    y = max(60, logo_zone_h + 12)

    title_lines = wrap_text(draw, title, title_font, CANVAS_W - 2 * margin)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (CANVAS_W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=title_font, fill=NAVY)
        y += int((bbox[3] - bbox[1]) * 1.2)

    y += 16
    draw_flourish(draw, CANVAS_W // 2, y, 260, GOLD)
    y += 26

    title_end_y = y

    structured = entry.get("structured", {})
    left = structured.get("left", {})
    right = structured.get("right", {})

    col_w = (CANVAS_W - 3 * margin) // 2
    left_x = margin
    right_x = margin + col_w + margin

    # ---- Bottom band: pre-compute & anchor above footer ----
    bb = structured.get("bottom_band", "")
    bb_font = get_font(26, weight="italic")
    bb_lines = wrap_text(draw, bb, bb_font, CANVAS_W - 2 * margin) if bb else []
    bb_line_h = int(26 * 1.4)
    bb_total_h = bb_line_h * len(bb_lines)
    bb_top_padding = 28  # space above text for the flourish
    bb_block_h = bb_total_h + bb_top_padding + 36  # bottom breathing room
    bb_block_top_y = CANVAS_H - FOOTER_H - bb_block_h

    # ---- Pre-compute body block height to vertically centre it ----
    icon_size = 80
    icon_gap_below = 18
    header_font = get_font(48, weight="bold")
    header_h_est = 54
    label_to_sub_gap = 14
    subtitle_font = get_font(26, weight="italic")
    sub_line_h = int(26 * 1.32)
    sub_to_items_gap = 40
    body_font = get_font(28)
    body_line_h = int(28 * 1.5)
    item_gap = 18

    # Estimate subtitle line counts per column for height
    def sub_count(col):
        sub = col.get("subtitle", "")
        if not sub:
            return 0
        return len(wrap_text(draw, sub, subtitle_font, col_w - 20))

    def items_height(col):
        total = 0
        for item in col.get("items", []):
            line_count = len(wrap_text(draw, item, body_font, col_w - 24))
            total += line_count * body_line_h + item_gap
        if total > 0:
            total -= item_gap  # no trailing gap
        return total

    sub_h = max(sub_count(left), sub_count(right)) * sub_line_h
    items_h = max(items_height(left), items_height(right))

    body_block_h = (
        icon_size + icon_gap_below
        + header_h_est + label_to_sub_gap
        + sub_h + sub_to_items_gap
        + items_h
    )

    # Available vertical space between title-end and bottom-band-top
    avail_top = title_end_y + 14
    avail_bot = bb_block_top_y - 14
    avail_h = avail_bot - avail_top
    body_top = avail_top + max(0, (avail_h - body_block_h) // 2)

    # ---- Icons ----
    icon_y = body_top + icon_size // 2

    def _icon_color(icon_name: str):
        # heart → burgundy; flame → teal (or BURGUNDY fallback)
        if icon_name == "flame":
            return TEAL
        return BURGUNDY

    def _draw_icon(icon_name: str, cx: int, cy: int):
        if icon_name == "heart":
            draw_heart(canvas, cx, cy, icon_size, _icon_color(icon_name))
        elif icon_name == "flame":
            draw_flame(canvas, cx, cy, icon_size, _icon_color(icon_name))

    _draw_icon(left.get("icon", ""), left_x + col_w // 2, icon_y)
    _draw_icon(right.get("icon", ""), right_x + col_w // 2, icon_y)

    # canvas was paste()'d into; refresh draw handle in case
    draw = ImageDraw.Draw(canvas)

    label_y = icon_y + icon_size // 2 + icon_gap_below

    # ---- Headers ----
    for col, x_center, color in [
        (left, left_x + col_w // 2, _icon_color(left.get("icon", ""))),
        (right, right_x + col_w // 2, _icon_color(right.get("icon", ""))),
    ]:
        label = col.get("label", "").upper()
        bbox = draw.textbbox((0, 0), label, font=header_font)
        draw.text((x_center - (bbox[2] - bbox[0]) // 2, label_y), label, font=header_font, fill=color)

    sub_y = label_y + header_h_est + label_to_sub_gap

    # ---- Subtitles ----
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
                cur_y += sub_line_h
        if sub_y_var_holder == "left":
            sub_y_left = cur_y
        else:
            sub_y_right = cur_y

    items_y = max(sub_y_left, sub_y_right) + sub_to_items_gap

    # ---- Body bullets ----
    col_end_ys: list[int] = []
    for col, x_start, bullet_color in [
        (left, left_x, _icon_color(left.get("icon", ""))),
        (right, right_x, _icon_color(right.get("icon", ""))),
    ]:
        cur_y = items_y
        items = col.get("items", [])
        for item in items:
            draw.ellipse(
                [x_start, cur_y + 12, x_start + 14, cur_y + 26],
                fill=bullet_color,
            )
            text_x = x_start + 26
            text_w = col_w - 26
            lines = wrap_text(draw, item, body_font, text_w)
            for line in lines:
                draw.text((text_x, cur_y), line, font=body_font, fill=NAVY)
                cur_y += body_line_h
            cur_y += item_gap
        col_end_ys.append(cur_y)

    bullets_end_y = max(col_end_ys)

    # ---- Vertical divider between the two columns ----
    divider_x = CANVAS_W // 2
    div_top = label_y - 6
    div_bot = bullets_end_y - item_gap
    draw.line([(divider_x, div_top), (divider_x, div_bot)], fill=GOLD, width=1)
    mid_y = (div_top + div_bot) // 2
    draw.polygon(
        [(divider_x - 6, mid_y), (divider_x, mid_y - 5), (divider_x + 6, mid_y), (divider_x, mid_y + 5)],
        fill=GOLD,
    )

    # ---- Bottom band (anchored above footer) ----
    if bb_lines:
        bb_y = bb_block_top_y + bb_top_padding
        draw_flourish(draw, CANVAS_W // 2, bb_block_top_y + 8, 200, GOLD)
        for line in bb_lines:
            bbox = draw.textbbox((0, 0), line, font=bb_font)
            draw.text(
                ((CANVAS_W - (bbox[2] - bbox[0])) // 2, bb_y),
                line, font=bb_font, fill=BURGUNDY,
            )
            bb_y += bb_line_h

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
