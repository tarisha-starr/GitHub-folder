"""Generate 30 journal-prompt cards via OpenAI's image API.

Reads content/journal_prompts.json, sends one image-generation request
per prompt to OpenAI (gpt-image-1) using the brand's color-card style,
and saves each result as images/journal/journal-N.jpg.

Idempotent: skips prompts whose image already exists. Set FORCE=1 in
the env to regenerate everything.

Required env vars:
  OPENAI_API_KEY        OpenAI API key
  OPENAI_IMAGE_MODEL    optional, defaults to gpt-image-1
  IMAGE_QUALITY         optional, defaults to "high" (text renders best)
  FORCE                 optional, set to "1" to regenerate existing
"""

from __future__ import annotations

import base64
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

DEFAULT_MODEL = "gpt-image-1"
DEFAULT_QUALITY = "high"
SIZE = "1024x1536"  # 4:5-ish portrait; gpt-image-1 supports this preset

# Rotated brand colors so cards aren't all the same shade across the set.
BRAND_COLORS = [
    {"name": "cream", "bg": "#F4EFE6", "text": "#6E1A2E", "accent": "#C2A46D"},
    {"name": "burgundy", "bg": "#6E1A2E", "text": "#F4EFE6", "accent": "#C2A46D"},
    {"name": "gold", "bg": "#C2A46D", "text": "#6E1A2E", "accent": "#1F2A44"},
    {"name": "navy", "bg": "#1F2A44", "text": "#F4EFE6", "accent": "#C2A46D"},
    {"name": "blush", "bg": "#E8D5CE", "text": "#6E1A2E", "accent": "#C2A46D"},
]


PROMPT_TEMPLATE = """\
A single 4:5 portrait social-media card (1024x1536) for the brand
"Sexual Empowerment for Women" — a journaling prompt card.

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
- Trailing "..." in accent color: {accent}.
- Small gold ornamental flourish (filigree divider, curlicue motif)
  above and below the text, color {accent}.

Branding:
- Solid footer bar at bottom in deep navy #1F2A44, full width.
- Footer text "SEXUALEMPOWERMENTFORWOMEN.COM" in serif ALL CAPS,
  cream/white #F4EFE6, centered in the bar.
- Circular monogram in TOP RIGHT corner.
- Circle background: deep burgundy / wine #6E1A2E (NOT gold).
- Inside: stylised letter "S" in white #F4EFE6, hand-painted
  brush-stroke calligraphy style (NOT a typed letter), organic
  flowing curves like a single ink stroke.
- Subtle thin black outline around the outer edge of the circle.
- ~80px diameter on a 1536px-tall image.

DO NOT include: any photograph or person, any text other than the
prompt and footer URL, any numbers/labels/watermarks, multiple cards
in a grid, saturated colors outside the brand palette.
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


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY must be set", file=sys.stderr)
        write_diagnostic({"error": "OPENAI_API_KEY not set"})
        return 1

    model = os.environ.get("OPENAI_IMAGE_MODEL") or DEFAULT_MODEL
    quality = os.environ.get("IMAGE_QUALITY") or DEFAULT_QUALITY
    force = os.environ.get("FORCE") == "1"

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
        full_prompt = PROMPT_TEMPLATE.format(
            color_name=color["name"],
            bg=color["bg"],
            text=color["text"],
            accent=color["accent"],
            prompt=entry["prompt"],
        )

        print(f"Generating journal-{idx}.jpg ({color['name']})…")
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

        dest.write_bytes(img_bytes)
        built.append(idx)

    write_diagnostic(
        {
            "model": model,
            "quality": quality,
            "size": SIZE,
            "built": built,
            "skipped": skipped,
            "failed": failed,
        }
    )
    print(f"Built {len(built)}; skipped {len(skipped)}; failed {len(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
