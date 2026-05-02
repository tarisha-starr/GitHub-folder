"""Send today's image post brief by email.

Picks today's post via scheduler.todays_post(). If no post for today
(out of inventory or before launch date), sends an inventory alert
instead. After a successful daily send, also fires a "create more
posts" warning email when remaining inventory drops to ALERT_THRESHOLD
or below.
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

from scheduler import ALERT_THRESHOLD, remaining_count, todays_post


def render_text(post: dict, remaining: int) -> str:
    themes = ", ".join(post.get("themes", []))
    hashtags = " ".join(post.get("hashtags", []))
    return (
        f"Post #{post['id']} - today's brief\n\n"
        f"Hook (overlay text):\n  {post['hook']}\n\n"
        f"Caption:\n{post.get('caption', post['hook'])}\n\n"
        f"Engagement question:\n  {post.get('question', '')}\n\n"
        f"Hashtags:\n  {hashtags}\n\n"
        f"Visual prompt:\n  {post['visual']}\n\n"
        f"Image file: {post.get('image', '(missing)')}\n"
        f"Themes: {themes}\n\n"
        f"Posts remaining after today: {remaining}\n"
    )


def render_html(post: dict, remaining: int) -> str:
    themes = ", ".join(post.get("themes", []))
    hashtags = " ".join(post.get("hashtags", []))
    caption_html = post.get("caption", post["hook"]).replace("\n", "<br>")
    return f"""\
<!doctype html>
<html>
  <body style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #222;">
    <p style="color: #888; font-size: 13px;">Post #{post['id']} &mdash; today's brief</p>
    <h2 style="font-size: 22px; line-height: 1.35; margin: 0 0 24px;">{post['hook']}</h2>

    <p style="font-size: 14px; color: #555; margin: 0 0 6px;"><strong>Caption</strong></p>
    <p style="font-size: 15px; line-height: 1.55; margin: 0 0 24px;">{caption_html}</p>

    <p style="font-size: 14px; color: #555; margin: 0 0 6px;"><strong>Engagement question</strong></p>
    <p style="font-size: 16px; font-style: italic; line-height: 1.5; margin: 0 0 24px;">{post.get('question', '')}</p>

    <p style="font-size: 14px; color: #555; margin: 0 0 6px;"><strong>Hashtags</strong></p>
    <p style="font-size: 13px; color: #3a6ea5; margin: 0 0 24px;">{hashtags}</p>

    <p style="font-size: 14px; color: #555; margin: 0 0 6px;"><strong>Visual prompt</strong></p>
    <p style="font-size: 15px; line-height: 1.5; margin: 0 0 12px;">{post['visual']}</p>

    <p style="font-size: 13px; color: #888;">Image file: {post.get('image', '(missing)')} &middot; Themes: {themes}</p>
    <p style="font-size: 12px; color: #aaa; margin-top: 24px;">Posts remaining after today: {remaining}</p>
  </body>
</html>
"""


def build_message(post: dict, remaining: int, sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Daily post #{post['id']}: {post['hook']}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_text(post, remaining))
    msg.add_alternative(render_html(post, remaining), subtype="html")
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
    post = todays_post()
    remaining = remaining_count()

    if post is None:
        send(build_alert_empty(sender, recipients))
        print("No post for today; sent inventory-empty alert")
        return 0

    send(build_message(post, remaining, sender, recipients))
    print(f"Sent post #{post['id']} to {len(recipients)} recipient(s); {remaining} remaining")

    if 0 < remaining <= ALERT_THRESHOLD:
        send(build_alert_low(remaining, sender, recipients))
        print(f"Inventory-low alert sent ({remaining} remaining)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
