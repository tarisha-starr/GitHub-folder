"""Generate new hook + caption + question + hashtag sets in your brand voice.

Reads content/posts.json as style examples, then calls the OpenAI API to
generate N new posts that match the SHORT-PUNCHY pain-hook + emotional-
truth formula without repeating any hook already in the file.

Outputs to content/draft_hooks.json AND emails the list (along with the
ChatGPT image prompt) so you can generate images and add to rotation.

Required env vars:
  OPENAI_API_KEY                 OpenAI API key
  SMTP_*, EMAIL_FROM, EMAIL_TO   for the email digest
  HOOKS_TO_GENERATE              optional, defaults to 30
  OPENAI_MODEL                   optional, defaults to gpt-4o-mini
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
import urllib.request
from datetime import date
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_PATH = ROOT / "content" / "posts.json"
DRAFT_PATH = ROOT / "content" / "draft_hooks.json"
PROMPT_PATH = ROOT / "content" / "image_prompt.md"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_COUNT = 30


SYSTEM_PROMPT = """\
You write social-media hooks and captions for Tarisha Starr, a coach
for women over 40. Themes: desire, intimacy, sex after 40, long-term
relationships, midlife identity, body acceptance, perimenopause,
embodiment, burnout, emotional labour, sensuality, reclaiming.

VOICE RULES (NEVER BREAK)

1. NEVER use em-dashes (—) or en-dashes (–). Use commas, periods,
   ellipses (...), or split into separate sentences instead.
2. ALWAYS use contractions: don't, can't, won't, isn't, hasn't,
   you've, she's, it's, I'm.
3. British / NZ spelling: realise (not realize), colour (not color),
   favourite (not favorite), apologise (not apologize).

HOOK RULES (text burned into image)
- Short and punchy. Maximum 8 words. Aim for 3-6.
- Pain hook + emotional truth. No qualifiers. No softening.
- Examples that work:
  - "You're not done."
  - "You're not broken."
  - "Desire isn't dead. It's hiding."
  - "She came home to her body."
  - "I miss feeling wanted."

CAPTION RULES (the post body, in HER voice)
- Open with first-person observation from her work:
  "I see this every day in my work,"
  "I had a client say...",
  "I hear this every week,"
  "Women tell me...",
  "Many couples come into my office..."
- Conversational, raw, warm. Run-ons and sentence fragments are fine.
- Personify the body as "she": "she's been calling you home,"
  "ask her how she's doing, darling."
- Pet names welcome: "darling," "my love."
- Multiple short questions in a row are GOOD when they build rhythm:
  "Are you ready? Are you willing to take the first step?"
- Use ALL CAPS sparingly for emotional emphasis on one word:
  "Loving someone is NOT the same as being met by them."
- Use ellipses (...) for pause / weight:
  "It feels like betrayal... until you understand it's a signal."
- End with a direct question or comment-CTA:
  "Can you relate?", "Want to know how? Comment 'connection'",
  "Reach out if you feel lonely. We can shift it."

NEVER USE
- Em-dashes or en-dashes
- Therapist-speak ("Research shows," "Studies suggest")
- Coaching cliches ("Queen energy," "boss babe," "self-care")
- Performative empathy ("I see you," "I feel you, sister")
- Furthermore / However / Moreover
- Long polished paragraphs

HASHTAG RULES
- 6-8 hashtags per post from this established pool only:
#WomenOver40 #MidlifeWomen #Midlife #DesireAfter40 #SexAfter40
#LowDesire #LongTermLove #MarriageAfter40 #CouplesGoals
#RelationshipGoals #EmotionalIntimacy #IntimacyMatters
#Perimenopause #Menopause #SelfReclamation #ComeBackToYourself
#SacredFeminine #FeminineEnergy #Sensuality #BodyAcceptance
#BodyWisdom #SomaticHealing #Embodiment #SelfLove
#InvisibleLoad #EmotionalLabor #BurnoutRecovery #Loneliness
"""

USER_PROMPT_TEMPLATE = """\
Generate {n} new posts as a JSON object with key "posts" containing
an array. Each entry: hook, caption, question, hashtags (array of
6-8 tags), themes (array of 1-3 short tags).

CRITICAL: hook must be 3-8 words. NO LONG HOOKS.

Do NOT repeat any of these existing hooks (case-insensitive):
{existing_hooks}

Existing posts as style examples:
{examples}
"""


IMAGE_PROMPT_TEMPLATE = """\
Create a single photorealistic 4:5 portrait social media image
(1024x1280) for the brand "Sexual Empowerment for Women".

STYLE
- Photorealistic, cinematic, natural skin tones (NOT over-processed)
- Warm soft lighting (golden hour or soft indoor lamp)
- Lived-in, real, intimate — not stock-photo, not posed
- Premium calm aesthetic; soft depth of field; uncluttered background

SUBJECT
- Woman aged 45-60
- Vary across the series: ethnicities (Latina, Black, white, Asian,
  Indigenous, mixed), body sizes (include curvy and plus-size),
  hair (gray, brown, blonde; short, long)
- Natural beauty: minimal makeup, real skin, real hair
- Match her expression and posture to the emotional weight of the
  hook below

SCENE
- Everyday intimate spaces: kitchen window, bedroom edge, couch,
  bathroom mirror, doorway, garden, yoga mat, walking outdoors
- Natural posture: sitting, leaning, standing, walking

TEXT OVERLAY (CRITICAL — render exactly)
- Render the hook text EXACTLY as written. Use straight apostrophes (').
- Font: elegant serif, Lora-style or Cormorant Garamond
- Large, left-aligned, easy to read on mobile
- Color rule:
  * On LIGHT/warm scenes: deep burgundy (#6E1A2E) body, warm gold
    (#C2A46D) on emotionally-weighted words
  * On DARK scenes: cream/white (#F4EFE6) body, warm gold (#C2A46D)
    accent words
- Include small gold ornamental flourishes (filigree dividers)
  between text blocks

HOOK TEXT
"<HOOK GOES HERE>"

BRANDING
- Solid footer bar at bottom: deep navy (#1F2A44), full width
- Footer text: SEXUALEMPOWERMENTFORWOMEN.COM
- Footer font: serif, ALL CAPS, large, cream/white or warm gold
- Center the footer text inside the bar

LOGO
- Circular monogram in TOP RIGHT corner.
- Circle background: deep burgundy / wine #6E1A2E (NOT gold).
- Inside the circle: a stylised letter "S" in white #F4EFE6,
  hand-painted brush-stroke calligraphy style (NOT a typed letter).
  The S has organic flowing curves, like a single ink stroke.
- Subtle thin black outline around the outer edge of the circle.
- ~80px diameter on a 1280px-tall image.

DO NOT
- Combine multiple images, include numbers/labels/watermarks
  (other than the brand footer), distort skin tones, use bright
  saturated colors, add any text other than the hook and footer
"""


def load_posts() -> list[dict]:
    with POSTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def call_openai(api_key: str, model: str, system: str, user: str) -> str:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.95,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def parse_drafts(raw: str) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, dict):
        for key in ("posts", "drafts", "hooks", "items", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
        if all(isinstance(v, dict) for v in data.values()):
            return list(data.values())
    if isinstance(data, list):
        return data
    raise ValueError("Could not find a list of drafts in the model response")


def render_email_text(drafts: list[dict]) -> str:
    lines = [
        "*** IMAGES REQUIRED ***",
        "",
        f"You have {len(drafts)} new draft hooks below.",
        "Each one needs an image generated in ChatGPT.",
        "Then upload the images to your Dropbox folder.",
        "The fetch workflow will pull them in next time it runs.",
        "",
        "=" * 60,
        "STEP 1 — Use this ChatGPT prompt for each image",
        "(swap the HOOK GOES HERE line per post)",
        "=" * 60,
        "",
        IMAGE_PROMPT_TEMPLATE,
        "",
        "=" * 60,
        f"STEP 2 — Generate one image per hook below ({len(drafts)} total)",
        "=" * 60,
        "",
    ]
    for i, d in enumerate(drafts, start=1):
        hashtags = " ".join(d.get("hashtags", []))
        lines.append(f"#{i}")
        lines.append(f"Hook:     {d.get('hook', '').strip()}")
        lines.append(f"Caption:  {d.get('caption', '').strip()}")
        lines.append(f"Question: {d.get('question', '').strip()}")
        lines.append(f"Tags:     {hashtags}")
        lines.append("")
    lines.append("=" * 60)
    lines.append("STEP 3 — When images are ready")
    lines.append("=" * 60)
    lines.append("")
    lines.append("1. Upload images to Dropbox (any filename works)")
    lines.append("2. Run the 'Fetch Dropbox images' workflow")
    lines.append("3. Look at images/raw/ and update images/mapping.json")
    lines.append("   to map each new file to its post id")
    lines.append("4. Append these draft entries to content/posts.json")
    lines.append("")
    return "\n".join(lines)


def render_email_html(drafts: list[dict]) -> str:
    parts = [
        '<div style="font-family: Georgia, serif; max-width: 640px; margin: 0 auto; color: #222;">',
        '<div style="background:#6E1A2E; color:#fff; padding:16px; text-align:center; font-size:18px; letter-spacing:2px;">IMAGES REQUIRED</div>',
        f'<p style="font-size:15px;">You have <b>{len(drafts)} new draft hooks</b> below. Each one needs an image generated in ChatGPT, then uploaded to your Dropbox folder.</p>',
        '<h3 style="border-bottom:2px solid #C2A46D; padding-bottom:8px;">Step 1 &mdash; ChatGPT image prompt</h3>',
        '<p style="font-size:13px; color:#666;">Paste this into ChatGPT once per image, swapping the hook line.</p>',
        f'<pre style="background:#f6f3ee; padding:12px; font-size:12px; white-space:pre-wrap; border-left:3px solid #C2A46D;">{IMAGE_PROMPT_TEMPLATE}</pre>',
        f'<h3 style="border-bottom:2px solid #C2A46D; padding-bottom:8px;">Step 2 &mdash; Generate {len(drafts)} images</h3>',
    ]
    for i, d in enumerate(drafts, start=1):
        hashtags = " ".join(d.get("hashtags", []))
        parts.append(
            f'<div style="margin:20px 0; padding:16px; background:#fafafa; border-left:3px solid #6E1A2E;">'
            f'<p style="color:#888; font-size:12px; margin:0;">#{i}</p>'
            f'<p style="font-size:18px; font-weight:bold; margin:6px 0;">{d.get("hook", "")}</p>'
            f'<p style="font-size:14px; color:#555; margin:6px 0;"><b>Caption:</b> {d.get("caption", "").replace(chr(10), "<br>")}</p>'
            f'<p style="font-size:14px; color:#555; margin:6px 0;"><b>Question:</b> {d.get("question", "")}</p>'
            f'<p style="font-size:12px; color:#3a6ea5; margin:6px 0;">{hashtags}</p>'
            f"</div>"
        )
    parts.append('<h3 style="border-bottom:2px solid #C2A46D; padding-bottom:8px;">Step 3 &mdash; When images are ready</h3>')
    parts.append('<ol style="font-size:14px; line-height:1.6;">')
    parts.append("<li>Upload images to your Dropbox folder (any filename works)</li>")
    parts.append("<li>Run the <b>Fetch Dropbox images</b> workflow</li>")
    parts.append("<li>Update <code>images/mapping.json</code> to map each new file to its post id</li>")
    parts.append("<li>Append these draft entries to <code>content/posts.json</code></li>")
    parts.append("</ol>")
    parts.append("</div>")
    return "\n".join(parts)


def email_drafts(drafts: list[dict]) -> None:
    sender = os.environ.get("EMAIL_FROM")
    recipients_raw = os.environ.get("EMAIL_TO", "")
    if not sender or not recipients_raw:
        print("EMAIL_FROM and EMAIL_TO not set; skipping email", file=sys.stderr)
        return
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    msg = EmailMessage()
    msg["Subject"] = f"[ACTION] {len(drafts)} new hooks ready - images required ({date.today().isoformat()})"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_email_text(drafts))
    msg.add_alternative(render_email_html(drafts), subtype="html")

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls(context=context)
            smtp.login(user, password)
            smtp.send_message(msg)


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY must be set", file=sys.stderr)
        return 1

    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    count = int(os.environ.get("HOOKS_TO_GENERATE", str(DEFAULT_COUNT)))

    posts = load_posts()
    existing_hooks = "\n".join(f"- {p['hook']}" for p in posts)
    examples = json.dumps(
        [
            {
                "hook": p["hook"],
                "caption": p.get("caption", ""),
                "question": p.get("question", ""),
                "hashtags": p.get("hashtags", []),
                "themes": p.get("themes", []),
            }
            for p in posts[:6]
        ],
        indent=2,
        ensure_ascii=False,
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        n=count, existing_hooks=existing_hooks, examples=examples
    )

    print(f"Calling {model} for {count} new short punchy hooks…")
    raw = call_openai(api_key, model, SYSTEM_PROMPT, user_prompt)
    drafts = parse_drafts(raw)
    print(f"Parsed {len(drafts)} drafts")

    DRAFT_PATH.write_text(
        json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {DRAFT_PATH.relative_to(ROOT)}")

    PROMPT_PATH.write_text(IMAGE_PROMPT_TEMPLATE, encoding="utf-8")

    try:
        email_drafts(drafts)
        print("Emailed drafts to recipients")
    except Exception as e:
        print(f"Email failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
