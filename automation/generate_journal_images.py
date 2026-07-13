"""Generate 30 journal-prompt cards via OpenAI's image API.

Reads content/journal_prompts.json, sends one image-generation request
per prompt to OpenAI (gpt-image-1) using the brand's color-card style,
and saves each result as images/journal/journal-N.jpg.

Idempotent: skips prompts whose image already exists. Set FORCE=1 in
the env to regenerate everything.

Two logo variants are supported. Place these in images/brand/:
- logo-burgundy.png — burgundy circle, white S (used on light backgrounds:
                      cream, gold, blush). Falls back to logo.png if
                      logo-burgundy.png is not present.
- logo-gold.png     — gold circle, dark S (used on dark backgrounds:
                      burgundy, navy). Falls back to the burgundy logo
                      if logo-gold.png is not present.

Required env vars:
  OPENAI_API_KEY        OpenAI API key
  OPENAI_IMAGE_MODEL    optional, defaults to gpt-image-1
  IMAGE_QUALITY         optional, defaults to "high" (text renders best)
  FORCE                 optional, set to "1" to regenerate existing
  SKIP_LOGO             optional, set to "1" to skip logo overlay
"""

from __future__ import annotations

import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_PATH = ROOT / "content" / "journal_prompts.json"
OUT_DIR = ROOT / "images" / "journal"
DIAGNOSTIC_PATH = OUT_DIR / "_diagnostic.json"
BRAND_DIR = ROOT / "images" / "brand"

DEFAULT_MODEL = "gpt-image-1"
DEFAULT_QUALITY = "high"
SIZE = "1024x1536"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025

# Brand burgundy (#74224F) sampled from logo-burgundy.png — matches the
# real wine/burgundy of the logo. Used for body text on light cards and
# as the bg colour for the burgundy card so everything matches.
BRAND_BURGUNDY = "#74224F"

BRAND_COLORS = [
    {"name": "cream", "bg": "#F4EFE6", "text": BRAND_BURGUNDY, "accent": "#C2A46D"},
    {"name": "burgundy", "bg": BRAND_BURGUNDY, "text": "#F4EFE6", "accent": "#C2A46D"},
    {"name": "gold", "bg": "#C2A46D", "text": BRAND_BURGUNDY, "accent": "#1F2A44"},
    {"name": "navy", "bg": "#1F2A44", "text": "#F4EFE6", "accent": "#C2A46D"},
    {"name": "blush", "bg": "#E8D5CE", "text": BRAND_BURGUNDY, "accent": "#C2A46D"},
]

LOGO_FOR_BG = {
    "cream": "burgundy",
    "gold": "burgundy",
    "blush": "burgundy",
    "burgundy": "gold",
    "navy": "gold",
}


def burgundy_logo_path() -> Path | None:
    """Prefer logo-burgundy.png; fall back to logo.png; None if neither."""
    primary = BRAND_DIR / "logo-burgundy.png"
    if primary.exists():
        return primary
    fallback = BRAND_DIR / "logo.png"
    if fallback.exists():
        return fallback
    return None


def gold_logo_path() -> Path | None:
    primary = BRAND_DIR / "logo-gold.png"
    if primary.exists():
        return primary
    return None


def pick_logo_path(bg_name: str) -> Path | None:
    """Return the logo file matching this bg colour, with sensible fallbacks."""
    variant = LOGO_FOR_BG.get(bg_name, "burgundy")
    if variant == "gold":
        gold = gold_logo_path()
        if gold:
            return gold
        return burgundy_logo_path()
    return burgundy_logo_path()


PROMPT_TEMPLATE = """\
A single 4:5 portrait social-media card (1024x1536), an elegant
journaling prompt card.

Style: solid {color_name} background, hex {bg}. NOT photorealistic.
NOT a photograph. Premium calm aesthetic, very subtle paper grain
optional.

Render this prompt text EXACTLY as written, including the trailing
ellipsis, with straight apostrophes:

  "{prompt}"

Text styling:
- Centered, large, easy to read on mobile.
- Elegant serif font (Lora-style or Cormorant Garamond).
- Body text color: {text}.
- Trailing three dots "..." rendered as plain body text in the same
  color as the rest of the text. Not stylized.
- The area above and below the text must be completely empty. No
  ornament, no divider, no flourish, no filigree, no curlicue, no
  scroll, no swirl, no leaf, no dot cluster, no symbol of any kind.
  Pure background only above and below the text block.
- Use straight ASCII apostrophes and straight quotes only. No curly
  or smart typography.

Branding:
- Solid footer bar at bottom in deep navy #1F2A44, full width.
- Footer text "SEXUALEMPOWERMENTFORWOMEN.COM" in serif ALL CAPS,
  cream/white #F4EFE6, centered in the bar.

IMPORTANT: Leave the TOP-RIGHT corner of the image visually clean and
empty. Do NOT draw any logo, monogram, letter, or graphic in the
top-right area. A real logo will be placed there in post-production.

DO NOT include: any photograph or person, any text other than the
prompt and footer URL, any numbers/labels/watermarks, multiple cards
in a grid, saturated colors outside the brand palette, any logo or
S monogram, any decorative flourish, filigree, ornament, curlicue,
scrollwork, swirl, leaf motif, dot cluster, star, or any symbol
whatsoever above or below the prompt text, any curly quotes or curly
apostrophes.
"""


def write_diagnostic(payload: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )


def load_prompts() -> list[dict]:
    with PROMPTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def call_openai_image(api_key: str, model: str, quality: str, prompt: str) -> bytes:
    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": SIZE,
        "quality": quality,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    b64 = result["data"][0]["b64_json"]
    return base64.b64decode(b64)


def composite_logo(img_bytes: bytes, logo_path: Path) -> bytes:
    """Wipe top-right with sampled bg colour, then overlay the logo cleanly."""
    from PIL import Image, ImageDraw  # type: ignore

    base = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    target_w = int(base.width * LOGO_WIDTH_FRACTION)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)

    margin = int(base.width * LOGO_MARGIN_FRACTION)
    pos = (base.width - target_w - margin, margin)

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
    return out.getvalue()


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY must be set", file=sys.stderr)
        write_diagnostic({"error": "OPENAI_API_KEY not set"})
        return 1

    model = os.environ.get("OPENAI_IMAGE_MODEL") or DEFAULT_MODEL
    quality = os.environ.get("IMAGE_QUALITY") or DEFAULT_QUALITY
    force = os.environ.get("FORCE") == "1"
    skip_logo = os.environ.get("SKIP_LOGO") == "1"

    burgundy = burgundy_logo_path()
    gold = gold_logo_path()
    use_logo = (burgundy is not None) and not skip_logo

    if not use_logo and not skip_logo:
        print(f"No burgundy logo found in {BRAND_DIR.relative_to(ROOT)}; skipping overlay")
    if gold is None:
        print("Note: logo-gold.png not found; dark-bg cards will use the burgundy logo.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts()

    built: list[int] = []
    skipped: list[int] = []
    failed: list[dict] = []

    for entry in prompts:
        idx = int(entry["id"])
        dest = OUT_DIR / f"journal-{idx}.jpg"
        if dest.exists() and dest.stat().st_size > 0 and not force:
            skipped.append(idx)
            continue

        color = BRAND_COLORS[(idx - 1) % len(BRAND_COLORS)]
        prompt_text = (
            entry["prompt"]
            .replace("’", "'")
            .replace("‘", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("—", ",")
            .replace("–", ",")
            .replace("…", "...")
        )
        full_prompt = PROMPT_TEMPLATE.format(
            color_name=color["name"],
            bg=color["bg"],
            text=color["text"],
            accent=color["accent"],
            prompt=prompt_text,
        )

        print(f"Generating journal-{idx}.jpg ({color['name']})...")
        try:
            img_bytes = call_openai_image(api_key, model, quality, full_prompt)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            failed.append({"id": idx, "status": e.code, "body": body[:500]})
            print(f"FAILED journal-{idx}: {e.code} {body[:200]}", file=sys.stderr)
            continue
        except Exception as e:
            failed.append({"id": idx, "error": str(e)})
            print(f"FAILED journal-{idx}: {e}", file=sys.stderr)
            continue

        if use_logo:
            logo_path = pick_logo_path(color["name"])
            if logo_path:
                try:
                    img_bytes = composite_logo(img_bytes, logo_path)
                except Exception as e:
                    print(f"Logo overlay failed for journal-{idx}: {e}", file=sys.stderr)

        dest.write_bytes(img_bytes)
        built.append(idx)

    write_diagnostic(
        {
            "model": model,
            "quality": quality,
            "size": SIZE,
            "burgundy_hex": BRAND_BURGUNDY,
            "burgundy_logo": str(burgundy.name) if burgundy else None,
            "gold_logo": str(gold.name) if gold else None,
            "built": built,
            "skipped": skipped,
            "failed": failed,
        }
    )
    print(f"Built {len(built)}; skipped {len(skipped)}; failed {len(failed)}")
    if failed and not built and not skipped:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
