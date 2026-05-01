"""Send today's image post brief by email.

Reads SMTP config and recipients from environment variables, picks the
post for today via scheduler.todays_post(), and sends a formatted email
that the content creator can hand to a designer or paste into a generator.
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

from scheduler import todays_post


def render_text(post: dict) -> str:
    themes = ", ".join(post.get("themes", []))
    return (
        f"Post #{post['id']} — today's brief\n\n"
        f"Hook (overlay text):\n  {post['hook']}\n\n"
        f"Visual prompt:\n  {post['visual']}\n\n"
        f"Themes: {themes}\n"
    )


def render_html(post: dict) -> str:
    themes = ", ".join(post.get("themes", []))
    return f"""\
<!doctype html>
<html>
  <body style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #222;">
    <p style="color: #888; font-size: 13px;">Post #{post['id']} — today's brief</p>
    <h2 style="font-size: 22px; line-height: 1.35; margin: 0 0 24px;">{post['hook']}</h2>
    <p style="font-size: 14px; color: #555; margin: 0 0 6px;"><strong>Visual prompt</strong></p>
    <p style="font-size: 15px; line-height: 1.5; margin: 0 0 24px;">{post['visual']}</p>
    <p style="font-size: 13px; color: #888;">Themes: {themes}</p>
  </body>
</html>
"""


def build_message(post: dict, sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Daily post #{post['id']}: {post['hook']}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_text(post))
    msg.add_alternative(render_html(post), subtype="html")
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
    post = todays_post()
    msg = build_message(post, sender, recipients)
    send(msg)
    print(f"Sent post #{post['id']} to {len(recipients)} recipient(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
