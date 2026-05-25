"""Generate one ChatGPT image prompt per infographic.

Reads content/infographics.json and writes content/chatgpt_infographic_prompts.md.

Each entry produces a self-contained prompt block the user can paste
directly into ChatGPT / Sora / any image model. The prompt locks in the
brand's "Quick recipes for social posts" palette:

- Background: Cream #F5EFE3
- Headlines: Marcellus, Near-Black #15110D
- Body / italic / accents: Lora, Near-Black #15110D
- Eyebrow / small caps: Lora bold small caps, Rust #9E4A2A
- Accent dividers / dots / underlines: Copper #C75D3D
- Italic body / quote: Near-Black at 80% opacity, Lora italic

Footer is always Navy #1F2A44 with cream type. Top-right corner is
reserved for post-production logo placement (NEVER draw a logo).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFOGRAPHICS_PATH = ROOT / "content" / "infographics.json"
OUT_PATH = ROOT / "content" / "chatgpt_infographic_prompts.md"


STYLE_BLOCK = """\
STYLE
- Canvas: 4:5 portrait, 1024x1536 px. NOT photorealistic. NOT a photograph.
- Solid background: Cream #F5EFE3. Optional very subtle paper grain.
- Headlines: serif in the style of Marcellus, colour Near-Black #15110D.
- Body text and italic quotes: serif in the style of Lora, colour Near-Black #15110D (italic body at 80 percent opacity).
- Eyebrow text and labels in SMALL CAPS: Lora bold small caps, colour Rust #9E4A2A.
- Accent dividers, dots, underlines, small ornaments: Copper #C75D3D.
- Generous whitespace. Premium, calm, editorial.
- Aesthetic reference: high-end women's wellness editorial, NOT corporate clip-art."""


FOOTER_BLOCK = """\
FOOTER (always include, last 6 percent of canvas)
- Solid Navy #1F2A44 bar, full width.
- Centred text: SEXUALEMPOWERMENTFORWOMEN.COM in Marcellus ALL CAPS, colour Cream #F5EFE3.
- No other text in the footer."""


LOGO_BLOCK = """\
LOGO ZONE (always reserve)
- LEAVE the top-right corner empty for about 130x130 px. Do NOT draw any logo, monogram, letter S, brand mark, watermark, or graphic in the top-right area. A real logo will be added in post-production."""


DONTS_BLOCK = """\
DO NOT INCLUDE
- Any photograph, person, body part, or illustrated figure.
- Any text other than what is specified above.
- Watermarks, page numbers, scale references, labels not requested.
- Saturated colours outside the palette (no bright pinks, no neon, no rainbow).
- Em-dashes. Use commas or full stops. Use straight apostrophes only.
- Any logo, S monogram, or SEW lettering anywhere on the card.
- Misspellings, dropped letters, doubled words, or invented words. Render every word EXACTLY as written."""


HEADER = """\
# ChatGPT prompts for the 30 brand infographics

Paste a single prompt below into ChatGPT (use a model with image
generation, e.g. ChatGPT Image / Sora). Each one is self-contained.

After ChatGPT returns the image, save it as
`images/infographics/infographic-{id}.jpg` and the existing
`reapply-logo` workflow will stamp the burgundy logo on top-right.

Brand palette (locked):

| Role | Hex |
| --- | --- |
| Background | `#F5EFE3` Cream (or `#FBF7EE` Ivory) |
| Headlines | `#15110D` Near-Black |
| Eyebrow / small caps | `#9E4A2A` Rust |
| Accent dot / divider | `#C75D3D` Copper |
| Italic body / quote | `#15110D` at 80% |
| Footer bar | `#1F2A44` Navy |
| Footer text | `#F5EFE3` Cream |

Fonts (locked): **Marcellus** for headlines, **Lora** for body, italic, and accents. Nothing else.

---
"""


def prompt_for(entry: dict) -> str:
    """Build the full ChatGPT prompt for a single infographic."""
    idx = entry["id"]
    title = entry["title"]
    caption = entry.get("caption", "")
    layout_desc = entry.get("layout", "")

    intent = ""
    if caption:
        intent = f"\nINTENT (do not render this as text on the card)\nThis card is paired with the caption: \"{caption}\". It must read as a calm, premium reflection prompt for women over 40.\n"

    return f"""\
LAYOUT BRIEF for infographic #{idx} — "{title}"

Render exactly the text shown below in the layout described. Treat
every quoted string as VERBATIM copy. Do not paraphrase, do not add
words. Use straight apostrophes.

TITLE (top of card, large Marcellus serif, Near-Black, centred, allowed to wrap to 2 lines):
"{title}"

DESIGN BRIEF (compose using these elements only):
{layout_desc}

Where the brief above says "heart", draw a small Copper #C75D3D heart-shaped accent (clean editorial silhouette, NOT a cartoon, NOT an emoji, NOT 3D). Where it says "shield" or "flame", draw a small editorial flame/teardrop in Copper #C75D3D. Treat them as small accent marks (about 28 to 56 px), not the focal point. If the brief mentions burgundy or teal column accents, replace those with the brand palette: use Rust #9E4A2A for the left/primary column accents and Copper #C75D3D for the right/secondary column accents. The body of each column remains Near-Black on Cream.

{STYLE_BLOCK}

{LOGO_BLOCK}

{FOOTER_BLOCK}

{DONTS_BLOCK}
{intent}"""


def main() -> int:
    with INFOGRAPHICS_PATH.open(encoding="utf-8") as f:
        entries = json.load(f)

    parts: list[str] = [HEADER]
    for entry in entries:
        idx = entry["id"]
        title = entry["title"]
        parts.append(f"\n## {idx}. {title}\n")
        if entry.get("caption"):
            parts.append(f"*Caption it will pair with: {entry['caption']}*\n")
        parts.append("\n````")
        parts.append(prompt_for(entry))
        parts.append("````\n")
        parts.append("\n---\n")

    OUT_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)} with {len(entries)} prompts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
