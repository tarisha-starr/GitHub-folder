"""Generate 30 infographic cards via OpenAI's image API.

Reads content/infographics.json. For each entry:
1. Sends a generation request to OpenAI (gpt-image-1) with a brand-styled
   prompt that uses the entry's title and layout description.
2. Pillow draws the brand footer bar with the website URL at the bottom
   of the result (guaranteed correct, no AI text errors).
3. Pillow overlays the real burgundy logo on the top-right.
4. Saves to images/infographics/infographic-N.jpg.

Idempotent: skips entries whose image already exists. Set FORCE=1 to
regenerate everything.

Required env vars:
  OPENAI_API_KEY        OpenAI API key
  OPENAI_IMAGE_MODEL    optional, defaults to gpt-image-1
  IMAGE_QUALITY         optional, defaults to "high"
  FORCE                 optional, "1" to regenerate existing
  SKIP_LOGO             optional, "1" to skip logo overlay
  ONLY_ID               optional, integer 1..30. If set, only that one
                        infographic is generated. Useful for testing
                        a single card cheaply (~$0.17).
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
INFOGRAPHICS_PATH = ROOT / "content" / "infographics.json"
OUT_DIR = ROOT / "images" / "infographics"
DIAGNOSTIC_PATH = OUT_DIR / "_diagnostic.json"
BRAND_DIR = ROOT / "images" / "brand"

DEFAULT_MODEL = "gpt-image-1"
DEFAULT_QUALITY = "high"
SIZE = "1024x1536"

WEBSITE = "sexualempowermentforwomen.com"
BRAND_BURGUNDY = "#74224F"

LOGO_WIDTH_FRACTION = 0.10
LOGO_MARGIN_FRACTION = 0.025

FOOTER_HEIGHT_FRACTION = 0.06
FOOTER_BG = (31, 42, 68)
FOOTER_TEXT = (244, 239, 230)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/System/Library/Fonts/Times.ttc",
]


PROMPT_TEMPLATE = """\
A single 4:5 portrait infographic image (1024x1536), in the style of
elegant educational graphics for a women's wellness brand.

STYLE
- Solid soft pink/blush background, hex #F4D9D6.
- Premium calm aesthetic, NOT photorealistic, NOT a photograph.
- Hand-drawn illustration accents allowed (small simple figures, hearts, shields).
- Strict palette only:
  * Deep navy #1F2A44 for headings and main body text.
  * Brand burgundy {brand_burgundy} for section labels and accent words
    (this is the wine/burgundy of the brand logo).
  * Warm gold #C2A46D for highlights, dividers, key phrases.
  * Soft teal/green for shield icons.
- Elegant serif font (Lora-style or Cormorant Garamond).
- Small heart icon (in brand burgundy {brand_burgundy}) for sections about her.
- Small shield icon (teal) for sections about him.
- Gold ornamental flourishes (filigree dividers) between sections.

TITLE at the top, large, navy serif:
"{title}"

BODY layout:
{layout}

CRITICAL CONSTRAINTS
- Leave the bottom 10% of the canvas COMPLETELY EMPTY. Do not draw any
  band, footer, watermark, or text in the bottom 10%. A footer bar will
  be drawn there in post-production.
- Leave the top-right corner clean and empty. Do not draw any logo,
  monogram, or letter there. A logo will be added in post-production.

DO NOT
- Use photographs of real people.
- Use bright saturated colours outside the palette.
- Add any logo, monogram, or letter S.
- Add any URL, website, or footer text.
- Include numbers/labels other than as part of the content above.
"""


def write_diagnostic(payload: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )


def load_entries() -> list[dict]:
    with INFOGRAPHICS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def burgundy_logo_path() -> Path | None:
    primary = BRAND_DIR / "logo-burgundy.png"
    if primary.exists():
        return primary
    fallback = BRAND_DIR / "logo.png"
    if fallback.exists():
        return fallback
    return None


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
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return base64.b64decode(result["data"][0]["b64_json"])


def find_font(size: int):
    from PIL import ImageFont  # type: ignore

    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_footer(img):
    from PIL import ImageDraw  # type: ignore

    width, height = img.size
    bar_h = int(height * FOOTER_HEIGHT_FRACTION)
    bar_top = height - bar_h

    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, bar_top), (width, height)], fill=FOOTER_BG)

    font_size = int(bar_h * 0.40)
    font = find_font(font_size)

    bbox = draw.textbbox((0, 0), WEBSITE, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = bar_top + (bar_h - text_h) // 2 - bbox[1]
    draw.text((x, y), WEBSITE, font=font, fill=FOOTER_TEXT)

    return img


def overlay_logo(img, logo_path: Path):
    from PIL import Image, ImageDraw  # type: ignore

    logo = Image.open(logo_path).convert("RGBA")
    target_w = int(img.width * LOGO_WIDTH_FRACTION)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)

    margin = int(img.width * LOGO_MARGIN_FRACTION)
    pos = (img.width - target_w - margin, margin)

    sample_box = (10, 10, 60, 60)
    sample = img.crop(sample_box).resize((1, 1), Image.LANCZOS)
    bg = sample.getpixel((0, 0))
    if isinstance(bg, tuple) and len(bg) == 4:
        bg = bg[:3]

    cover_pad = max(20, int(target_w * 0.30))
    cover_box = [
        max(0, pos[0] - cover_pad),
        max(0, pos[1] - cover_pad),
        min(img.width, pos[0] + target_w + cover_pad),
        min(img.height, pos[1] + target_h + cover_pad),
    ]
    draw = ImageDraw.Draw(img)
    draw.rectangle(cover_box, fill=bg)

    img.paste(logo_resized, pos, logo_resized)
    return img


def post_process(raw_bytes: bytes, logo_path: Path | None) -> bytes:
    from PIL import Image  # type: ignore

    base = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
    base = draw_footer(base)
    if logo_path is not None and logo_path.exists():
        base = overlay_logo(base, logo_path)

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
    logo_path = None if skip_logo else burgundy_logo_path()

    only_id_raw = os.environ.get("ONLY_ID", "").strip()
    only_id: int | None = None
    if only_id_raw and only_id_raw not in ("0", "all"):
        try:
            only_id = int(only_id_raw)
        except ValueError:
            print(f"Ignoring invalid ONLY_ID: {only_id_raw}", file=sys.stderr)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    entries = load_entries()
    if only_id is not None:
        entries = [e for e in entries if int(e["id"]) == only_id]
        if not entries:
            print(f"No infographic with id={only_id}", file=sys.stderr)
            write_diagnostic({"error": f"No entry with id={only_id}"})
            return 1
        print(f"ONLY_ID={only_id} set; generating just this one card.")

    built: list[int] = []
    skipped: list[int] = []
    failed: list[dict] = []

    for entry in entries:
        idx = int(entry["id"])
        dest = OUT_DIR / f"infographic-{idx}.jpg"
        if dest.exists() and dest.stat().st_size > 0 and not force:
            skipped.append(idx)
            continue

        full_prompt = PROMPT_TEMPLATE.format(
            title=entry.get("title", ""),
            layout=entry.get("layout", ""),
            brand_burgundy=BRAND_BURGUNDY,
        )

        print(f"Generating infographic-{idx}.jpg ({entry.get('title', '')})…")
        try:
            raw = call_openai_image(api_key, model, quality, full_prompt)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            failed.append({"id": idx, "status": e.code, "body": body[:500]})
            print(f"FAILED infographic-{idx}: {e.code} {body[:200]}", file=sys.stderr)
            continue
        except Exception as e:
            failed.append({"id": idx, "error": str(e)})
            print(f"FAILED infographic-{idx}: {e}", file=sys.stderr)
            continue

        try:
            final = post_process(raw, logo_path)
        except Exception as e:
            failed.append({"id": idx, "error": f"post-process: {e}"})
            print(f"Post-process failed for infographic-{idx}: {e}", file=sys.stderr)
            continue

        dest.write_bytes(final)
        built.append(idx)

    write_diagnostic(
        {
            "model": model,
            "quality": quality,
            "size": SIZE,
            "burgundy_hex": BRAND_BURGUNDY,
            "logo_applied": logo_path.name if logo_path else None,
            "footer_url": WEBSITE,
            "only_id": only_id,
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
