# Daily Image Posts + Email Automation

A content kit and daily automation pipeline for emotionally resonant image posts
targeting women over 40 around desire, intimacy, body, and midlife.

The image stops the scroll. The hook makes her feel caught.

## Contents

- `content/image-posts.md` — 20 ready-to-use image prompts paired with hooks
- `content/hooks.md` — reusable hook bank by theme
- `content/formula.md` — the pain-hook + emotional-truth formula
- `content/posts.json` — structured data the automation reads from
- `automation/daily_email.py` — sends one post per day via SMTP
- `automation/scheduler.py` — picks today's post deterministically by date
- `automation/requirements.txt` — Python dependencies
- `automation/.env.example` — config template (SMTP, recipients)
- `.github/workflows/daily-email.yml` — GitHub Actions cron that runs the job

## Quick start

```bash
cd automation
cp .env.example .env       # fill in SMTP creds + recipients
pip install -r requirements.txt
python daily_email.py      # send today's post
```

## Daily automation

The GitHub Action runs every day at 13:00 UTC and emails the next post in the
rotation. Configure these repository secrets:

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
- `EMAIL_FROM`, `EMAIL_TO`

## Notion

The same content is mirrored to Notion as a content calendar so you can plan,
edit, and check off posts as they go live.
