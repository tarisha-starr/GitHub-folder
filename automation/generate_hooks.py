"""Generate new hook + caption + question + hashtag sets in your brand voice.

Reads content/posts.json as style examples, then calls the OpenAI API to
generate N new posts that match the existing pain-hook + emotional-truth
formula without repeating any hook already in the file.

Outputs to content/draft_hooks.json AND emails the list so you can pick
which ones to make images for in Canva.

Required env vars:
  OPENAI_API_KEY                 OpenAI API key
  SMTP_*, EMAIL_FROM, EMAIL_TO   for the email digest
  HOOKS_TO_GENERATE              optional, defaults to 28
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

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_COUNT = 28


SYSTEM_PROMPT = """\
You write short, emotionally honest social-media hooks for women over 40.

Themes: desire, intimacy, sex after 40, long-term relationships, midlife
identity, body acceptance, perimenopause, embodiment, burnout, emotional
labour, sensuality.

Voice rules:
- Sound like something she would whisper to herself at 11pm.
- Never advice voice ("you should", "try"). Never clinical voice
  ("research shows"). Never performative empathy ("I see you, queen").
- Use the formula: pain hook + emotional truth. Two short sentences.
  No qualifiers. No softening. The truth lands harder than comfort.
- Examples of voice that works:
  - "You're not broken. You're exhausted."
  - "You don't hate sex. You hate pressure."
  - "You can love him and still feel lonely."
  - "The spark didn't die. It got buried under years of being useful."

Caption rules:
- The caption is what appears under the post on Instagram. The image
  already shows the hook. So the caption is JUST a short engagement
  question or two. 1-3 short lines maximum.
- Examples: "Is this you?", "Do you relate?", "Is this true?",
  "When did you last feel wanted?", "What helped you come back?",
  "Tell me below."

Hashtag rules:
- 6-8 hashtags per post. Mix big tags (#WomenOver40, #Midlife) with
  niche (#DesireAfter40, #ComeBackToYourself). Use only tags from
  the established pool below; do not invent new ones unless required.

Established hashtag pool:
#WomenOver40 #MidlifeWomen #Midlife #DesireAfter40 #SexAfter40
#LowDesire #LongTermLove #MarriageAfter40 #CouplesGoals
#RelationshipGoals #EmotionalIntimacy #IntimacyMatters
#Perimenopause #Menopause #SelfReclamation #ComeBackToYourself
#SacredFeminine #FeminineEnergy #Sensuality #BodyAcceptance
#BodyWisdom #SomaticHealing #Embodiment #SelfLove
#InvisibleLoad #EmotionalLabor #BurnoutRecovery #Loneliness
"""

USER_PROMPT_TEMPLATE = """\
Generate {n} new posts in this exact JSON structure. Return ONLY a JSON
array, no prose. Each entry needs: hook, caption, question, hashtags
(array of 6-8 tags), themes (array of 1-3 short tags).

The hook is what will be burned into the image. The caption is the
short engagement prompt under the post. The question is the single
strongest engagement prompt (often the same as the last line of caption).

Do NOT repeat any of these existing hooks (case-insensitive):
{existing_hooks}

Existing posts as style examples:
{examples}
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
        "temperature": 0.9,
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


def render_email(drafts: list[dict]) -> str:
    lines = [
        f"You have {len(drafts)} new draft hooks ready for review.",
        "",
        "Pick the ones you want, make images in Canva, upload to Dropbox.",
        "Then update content/posts.json + images/mapping.json with the new entries.",
        "",
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
    return "\n".join(lines)


def email_drafts(drafts: list[dict]) -> None:
    sender = os.environ.get("EMAIL_FROM")
    recipients_raw = os.environ.get("EMAIL_TO", "")
    if not sender or not recipients_raw:
        print("EMAIL_FROM and EMAIL_TO not set; skipping email", file=sys.stderr)
        return
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    msg = EmailMessage()
    msg["Subject"] = f"{len(drafts)} new draft hooks ready ({date.today().isoformat()})"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_email(drafts))

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

    print(f"Calling {model} for {count} new hooks…")
    raw = call_openai(api_key, model, SYSTEM_PROMPT, user_prompt)
    drafts = parse_drafts(raw)
    print(f"Parsed {len(drafts)} drafts")

    DRAFT_PATH.write_text(
        json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {DRAFT_PATH.relative_to(ROOT)}")

    try:
        email_drafts(drafts)
        print("Emailed drafts to recipients")
    except Exception as e:
        print(f"Email failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
