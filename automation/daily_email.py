"""Send today's image post by email — clean copy-paste format.

The body of the email IS the caption itself (no labels, no headings).
A single line at the bottom links to the image file. Subject is the
hook so it's scannable in the inbox.

When inventory drops to ALERT_THRESHOLD or below, sends a separate
'create more posts' email after the daily send. When inventory is
exhausted, sends a single 'no post' alert instead.
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

from scheduler import (
    ALERT_THRESHOLD,
    repurposed_1pm_entry,
    repurposed_1pm_remaining,
)


def image_url(image_path: str) -> str:
    raw_base = os.environ.get("IMAGE_RAW_BASE", "").rstrip("/")
    if not raw_base or not image_path:
        return ""
    return f"{raw_base}/{image_path}"


def render_text_post(post: dict) -> str:
    caption = post.get("caption", post["hook"])
    hashtags = " ".join(post.get("hashtags", []))
    img = image_url(post.get("image", ""))
    parts = [caption]
    if hashtags:
        parts += ["", hashtags]
    if img:
        parts += ["", img]
    return "\n".join(parts) + "\n"


def render_html_post(post: dict) -> str:
    caption_html = post.get("caption", post["hook"]).replace("\n", "<br>")
    hashtags = " ".join(post.get("hashtags", []))
    img = image_url(post.get("image", ""))
    return f"""\
<!doctype html>
<html>
  <body style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #222; padding: 24px;">
    <div style="font-size: 16px; line-height: 1.6; white-space: pre-wrap;">{caption_html}</div>
    <p style="font-size: 13px; color: #3a6ea5; margin: 24px 0 0 0;">{hashtags}</p>
    <p style="font-size: 12px; color: #888; margin: 24px 0 0 0;">
      <a href="{img}" style="color: #888;">{img}</a>
    </p>
  </body>
</html>
"""


def testimonial_caption(entry: dict) -> str:
    text = entry["text"]
    attribution = entry.get("attribution", "").strip()
    hashtags = " ".join(entry.get("hashtags", []))
    parts = [f"“{text}”"]
    if attribution:
        parts += ["", f"— {attribution}"]
    if hashtags:
        parts += ["", hashtags]
    return "\n".join(parts)


def render_text_testimonial(entry: dict) -> str:
    img = image_url(entry.get("image", ""))
    body = testimonial_caption(entry)
    if img:
        body += "\n\n" + img
    return body + "\n"


def render_html_testimonial(entry: dict) -> str:
    caption_html = testimonial_caption(entry).replace("\n", "<br>")
    img = image_url(entry.get("image", ""))
    return f"""\
<!doctype html>
<html>
  <body style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #222; padding: 24px;">
    <div style="font-size: 16px; line-height: 1.6; white-space: pre-wrap;">{caption_html}</div>
    <p style="font-size: 12px; color: #888; margin: 24px 0 0 0;">
      <a href="{img}" style="color: #888;">{img}</a>
    </p>
  </body>
</html>
"""


def build_message_post(post: dict, sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = post["hook"]
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_text_post(post))
    msg.add_alternative(render_html_post(post), subtype="html")
    return msg


def build_message_testimonial(entry: dict, sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    name = entry.get("attribution", "").strip()
    subject_tail = f" — {name}" if name else ""
    msg["Subject"] = f"Testimonial #{entry['id']}{subject_tail}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_text_testimonial(entry))
    msg.add_alternative(render_html_testimonial(entry), subtype="html")
    return msg


def build_alert_low(remaining: int, sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Only {remaining} post(s) left — create more"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    body = (
        f"Heads up — your daily-post inventory is running low.\n\n"
        f"Posts remaining (after today): {remaining}\n\n"
        f"To keep the daily send running uninterrupted:\n"
        f"  1. Add new images to your Dropbox folder\n"
        f"  2. Re-run the 'Fetch Dropbox images' workflow\n"
        f"  3. Append new entries to content/posts.json\n"
        f"  4. Update images/mapping.json\n"
    )
    msg.set_content(body)
    return msg


def build_alert_empty(sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "No post for today — inventory exhausted"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    body = (
        "There is no post scheduled for today.\n\n"
        "Either the launch date hasn't arrived yet, or you've published "
        "every post in content/posts.json.\n\n"
        "Add new posts and re-run the daily workflow to resume.\n"
    )
    msg.set_content(body)
    return msg


def send(msg: EmailMessage) -> None:
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
    sender = os.environ.get("EMAIL_FROM")
    recipients_raw = os.environ.get("EMAIL_TO", "")
    if not sender or not recipients_raw:
        print("EMAIL_FROM and EMAIL_TO must be set", file=sys.stderr)
        return 1

    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    slot = repurposed_1pm_entry()
    remaining = repurposed_1pm_remaining()

    if slot is None:
        send(build_alert_empty(sender, recipients))
        print("No 1pm post today; sent inventory-empty alert")
        return 0

    if slot["kind"] == "testimonial":
        entry = slot["data"]
        send(build_message_testimonial(entry, sender, recipients))
        print(f"Sent testimonial #{entry['id']} to {len(recipients)} recipient(s); {remaining} remaining")
    else:
        post = slot["data"]
        send(build_message_post(post, sender, recipients))
        print(f"Sent post #{post['id']} to {len(recipients)} recipient(s); {remaining} remaining")

    if 0 < remaining <= ALERT_THRESHOLD:
        send(build_alert_low(remaining, sender, recipients))
        print(f"Inventory-low alert sent ({remaining} remaining)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
