"""Daily inventory alert + auto-draft + Notion review.

For each of the 3 content streams (image hooks, journal prompts,
infographics):
1. Counts remaining posts based on POSTS_LAUNCH_DATE.
2. If remaining <= ALERT_THRESHOLD (default 7), calls OpenAI to draft
   30 fresh entries in Tarisha's voice (no em-dashes, contractions,
   British/NZ spelling, no duplicates).
3. Saves drafts to content/drafts/{stream}_drafts.json.
4. If NOTION_TOKEN is set, posts the drafts as a new sub-page in Notion
   under NOTION_DRAFTS_PARENT_PAGE_ID. Tarisha reviews and edits there.
5. Emails Tarisha a digest with the Notion link (if any) plus the full
   draft text inline.

HARD RULE: drafts must be reviewed in Notion BEFORE running any image
generator. The image generators are workflow_dispatch only, so they
cannot fire automatically — Tarisha controls when, after Notion review.

Required env:
  OPENAI_API_KEY, SMTP_HOST/PORT/USER/PASS, EMAIL_FROM, EMAIL_TO

Optional env:
  POSTS_LAUNCH_DATE              YYYY-MM-DD
  ALERT_THRESHOLD                int, default 7
  ALWAYS_EMAIL                   "1" to email even when nothing low
  NOTION_TOKEN                   Notion internal integration token
  NOTION_DRAFTS_PARENT_PAGE_ID   Notion page ID under which to post drafts
  OPENAI_MODEL                   default "gpt-4o-mini"
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "content" / "drafts"

DEFAULT_LAUNCH = date(2026, 5, 3)
DEFAULT_THRESHOLD = 7
DEFAULT_MODEL = "gpt-4o-mini"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


STREAMS = [
    {
        "name": "image_posts",
        "label": "Image posts (1pm NZ)",
        "data_path": ROOT / "content" / "posts.json",
        "draft_filename": "image_post_drafts.json",
        "system_prompt": (
            "You write SHORT punchy Instagram hooks for women over 40 in "
            "Tarisha Starr's voice. Each hook is 3-8 words max, pain hook + "
            "emotional truth. Always use contractions (don't, can't). Never "
            "use em-dashes. British/NZ spelling. Examples that work: "
            "\"You're not done.\", \"Desire isn't dead. It's hiding.\", "
            "\"The good girl is exhausted.\""
        ),
        "user_template": (
            "Generate {n} new short hooks. Each entry should have: hook (3-8 "
            "words), caption (1 short engagement question), question (same "
            "or shorter), hashtags (array of 6-8 from the established pool). "
            "Return as JSON object with key \"posts\" containing array.\n\n"
            "Do not duplicate any of these existing hooks (case-insensitive):\n"
            "{existing}"
        ),
    },
    {
        "name": "journal_prompts",
        "label": "Journal prompts (6pm NZ)",
        "data_path": ROOT / "content" / "journal_prompts.json",
        "draft_filename": "journal_prompt_drafts.json",
        "system_prompt": (
            "You write personal journaling prompts for women over 40 in "
            "Tarisha Starr's voice. Each prompt starts with first-person "
            "language and ends in '...' for the reader to fill in. They "
            "feel intimate, specific, embodied. Use contractions. No "
            "em-dashes. British/NZ spelling. Examples: \"One thing my body "
            "told me today was...\", \"The honest answer to 'how are you?' "
            "today is...\", \"What I really want him to know is...\"."
        ),
        "user_template": (
            "Generate {n} new journal prompts. Each entry: prompt (ends with "
            "'...'), caption_tail (a short 'tell me yours' invitation tailored "
            "to the prompt). Return as JSON object with key \"prompts\".\n\n"
            "Do not duplicate any of these:\n{existing}"
        ),
    },
    {
        "name": "infographics",
        "label": "Infographics (8am NZ)",
        "data_path": ROOT / "content" / "infographics.json",
        "draft_filename": "infographic_drafts.json",
        "system_prompt": (
            "You design infographic ideas for women over 40 in Tarisha "
            "Starr's voice (sex, intimacy, midlife, embodiment, "
            "relationships). Each idea has a catchy title, a "
            "recognition-question caption, and a structured layout "
            "description (two-column compare, cycle diagram, 4-stage "
            "progression, 2x2 grid, etc) with content per section. "
            "Use contractions. No em-dashes. British/NZ spelling."
        ),
        "user_template": (
            "Generate {n} new infographic ideas. Each entry: title, caption "
            "(a recognition question), layout (text description of the "
            "infographic structure and content). Return as JSON object with "
            "key \"infographics\".\n\nDo not duplicate any of these titles:\n"
            "{existing}"
        ),
    },
]


def launch_date() -> date:
    raw = os.environ.get("POSTS_LAUNCH_DATE")
    if raw:
        try:
            return date.fromisoformat(raw.strip())
        except ValueError:
            pass
    return DEFAULT_LAUNCH


def alert_threshold() -> int:
    raw = os.environ.get("ALERT_THRESHOLD")
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass
    return DEFAULT_THRESHOLD


def remaining_for(data_path: Path) -> int:
    try:
        with data_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return 0
    n_total = len(data) if isinstance(data, list) else 0
    used = (date.today() - launch_date()).days + 1
    return max(0, n_total - used)


def existing_titles(data_path: Path, key: str) -> list[str]:
    try:
        with data_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    return [str(item.get(key, "")).strip() for item in data if isinstance(item, dict)]


def call_openai_text(api_key: str, model: str, system: str, user: str) -> str:
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def parse_drafts(raw: str) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("posts", "prompts", "infographics", "hooks", "drafts", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("Could not find a list of drafts in the model response")


def generate_drafts(api_key: str, model: str, stream: dict, n: int) -> list[dict]:
    if stream["name"] == "image_posts":
        existing = "\n".join(f"- {h}" for h in existing_titles(stream["data_path"], "hook"))
    elif stream["name"] == "journal_prompts":
        existing = "\n".join(f"- {p}" for p in existing_titles(stream["data_path"], "prompt"))
    else:
        existing = "\n".join(f"- {t}" for t in existing_titles(stream["data_path"], "title"))

    user = stream["user_template"].format(n=n, existing=existing)
    raw = call_openai_text(api_key, model, stream["system_prompt"], user)
    return parse_drafts(raw)


def write_draft_file(stream: dict, drafts: list[dict]) -> Path:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    path = DRAFTS_DIR / stream["draft_filename"]
    path.write_text(
        json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


# ----- Notion posting -------------------------------------------------------

def notion_request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"{NOTION_API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def notion_text(content: str, bold: bool = False) -> dict:
    return {
        "type": "text",
        "text": {"content": content[:2000]},
        "annotations": {"bold": bold},
    }


def notion_blocks_for_drafts(stream_name: str, drafts: list[dict]) -> list[dict]:
    blocks: list[dict] = []
    for i, d in enumerate(drafts, 1):
        # Heading per item
        if stream_name == "image_posts":
            heading = f"{i}. {d.get('hook', '').strip()}"
        elif stream_name == "journal_prompts":
            heading = f"{i}. {d.get('prompt', '').strip()}"
        else:
            heading = f"{i}. {d.get('title', '').strip()}"

        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [notion_text(heading, bold=True)]},
        })

        # Body
        if stream_name == "image_posts":
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        notion_text("Caption: ", bold=True),
                        notion_text(d.get("caption", "") or ""),
                    ]
                },
            })
            tags = " ".join(d.get("hashtags", []))
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [notion_text(tags)]},
            })
        elif stream_name == "journal_prompts":
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [notion_text(d.get("caption_tail", "") or "")]},
            })
        else:  # infographics
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        notion_text("Caption: ", bold=True),
                        notion_text(d.get("caption", "") or ""),
                    ]
                },
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        notion_text("Layout: ", bold=True),
                        notion_text(d.get("layout", "") or ""),
                    ]
                },
            })

        blocks.append({"object": "block", "type": "divider", "divider": {}})

    # Notion limits: 100 blocks per page-create call. Truncate if needed.
    return blocks[:99]


def post_drafts_to_notion(token: str, parent_page_id: str, stream: dict, drafts: list[dict]) -> str | None:
    title = f"{stream['label']} drafts ({date.today().isoformat()})"
    body = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [{"type": "text", "text": {"content": title}}],
        },
        "icon": {"type": "emoji", "emoji": "📝"},
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "⚠️"},
                    "rich_text": [
                        notion_text(
                            "HARD RULE: review and edit these drafts here BEFORE running "
                            "any image generator. The image generators only run when you click "
                            "Run workflow in GitHub.",
                            bold=True,
                        ),
                    ],
                    "color": "red_background",
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        notion_text(
                            f"Auto-generated because {stream['label']} dropped to inventory low. "
                            f"{len(drafts)} drafts below."
                        ),
                    ]
                },
            },
        ] + notion_blocks_for_drafts(stream["name"], drafts),
    }
    try:
        result = notion_request("POST", "/pages", token, body=body)
        return result.get("url")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Notion API error {e.code}: {err_body[:500]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Notion post failed: {e}", file=sys.stderr)
        return None


# ----- Email rendering ------------------------------------------------------

def render_email(report: list[dict]) -> str:
    text_parts: list[str] = []
    has_drafts = any(s.get("drafts") for s in report)

    if has_drafts:
        text_parts.append("*** ACTION NEEDED: One or more streams running low ***\n")
        text_parts.append("HARD RULE: review the drafts in Notion BEFORE running")
        text_parts.append("any image generator. Image generators are manual-trigger only.\n")
    else:
        text_parts.append("Daily inventory check (no action needed)\n")

    for s in report:
        text_parts.append(f"-- {s['label']} --")
        text_parts.append(f"Remaining: {s['remaining']} day(s)")
        if s.get("notion_url"):
            text_parts.append(f"Notion review page: {s['notion_url']}")
        if s.get("drafts"):
            text_parts.append(
                f"BELOW threshold ({s['threshold']}) -- {len(s['drafts'])} fresh drafts generated."
            )
            text_parts.append("Review and edit in Notion (link above).")
            text_parts.append("Full text included below for reference:")
            text_parts.append("")
            for i, d in enumerate(s["drafts"], 1):
                if s["name"] == "image_posts":
                    text_parts.append(f"{i}. {d.get('hook', '')}")
                    text_parts.append(f"   Caption: {d.get('caption', '')}")
                    text_parts.append(f"   Tags: {' '.join(d.get('hashtags', []))}")
                elif s["name"] == "journal_prompts":
                    text_parts.append(f"{i}. {d.get('prompt', '')}")
                    text_parts.append(f"   {d.get('caption_tail', '')}")
                else:
                    text_parts.append(f"{i}. {d.get('title', '')}")
                    text_parts.append(f"   {d.get('caption', '')}")
                    text_parts.append(f"   Layout: {d.get('layout', '')[:200]}...")
                text_parts.append("")
        else:
            text_parts.append("(above threshold, no drafts generated)")
        text_parts.append("")

    text_parts.append("---")
    text_parts.append("Workflow:")
    text_parts.append("1. Open the Notion link(s) above and edit drafts")
    text_parts.append("2. Copy approved entries into the live content/*.json")
    text_parts.append("3. Trigger the matching image generator workflow:")
    text_parts.append("   - journal:     generate-journal-images.yml (force=1 to remake all)")
    text_parts.append("   - infographic: generate-infographic-images.yml")
    text_parts.append("   - image hook:  you make images yourself in ChatGPT, drop in Dropbox")
    return "\n".join(text_parts)


def send_email(subject: str, body: str) -> None:
    sender = os.environ.get("EMAIL_FROM")
    recipients_raw = os.environ.get("EMAIL_TO", "")
    if not sender or not recipients_raw:
        print("EMAIL_FROM and EMAIL_TO must be set; skipping email", file=sys.stderr)
        return
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

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
    model = os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL
    threshold = alert_threshold()
    always_email = os.environ.get("ALWAYS_EMAIL") == "1"
    notion_token = os.environ.get("NOTION_TOKEN")
    notion_parent = os.environ.get("NOTION_DRAFTS_PARENT_PAGE_ID")

    report: list[dict] = []
    any_low = False

    for stream in STREAMS:
        remaining = remaining_for(stream["data_path"])
        entry = {
            "name": stream["name"],
            "label": stream["label"],
            "remaining": remaining,
            "threshold": threshold,
            "drafts": [],
            "notion_url": None,
        }

        if remaining <= threshold:
            any_low = True
            if not api_key:
                print(
                    f"{stream['name']} is low ({remaining}) but OPENAI_API_KEY not set; "
                    "skipping draft generation",
                    file=sys.stderr,
                )
            else:
                try:
                    drafts = generate_drafts(api_key, model, stream, n=30)
                    entry["drafts"] = drafts
                    path = write_draft_file(stream, drafts)
                    print(f"Wrote {len(drafts)} drafts to {path.relative_to(ROOT)}")

                    if notion_token and notion_parent:
                        url = post_drafts_to_notion(notion_token, notion_parent, stream, drafts)
                        if url:
                            entry["notion_url"] = url
                            print(f"Posted to Notion: {url}")
                    elif notion_token or notion_parent:
                        print(
                            "Notion posting skipped: need both NOTION_TOKEN and "
                            "NOTION_DRAFTS_PARENT_PAGE_ID.",
                            file=sys.stderr,
                        )
                except Exception as e:
                    print(
                        f"Failed to generate drafts for {stream['name']}: {e}",
                        file=sys.stderr,
                    )

        report.append(entry)

    if not any_low and not always_email:
        print("All streams above threshold; not sending email.")
        for s in report:
            print(f"  {s['label']}: {s['remaining']} remaining")
        return 0

    subject_prefix = "[ACTION] Inventory low" if any_low else "Inventory check"
    subject = f"{subject_prefix} - {date.today().isoformat()}"
    body = render_email(report)
    try:
        send_email(subject, body)
        print(f"Sent inventory email: {subject}")
    except Exception as e:
        print(f"Email failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
