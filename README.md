# Daily Image Posts + Email + Buffer

A content kit and daily automation pipeline for emotionally resonant image posts
targeting women over 40 around desire, intimacy, body, and midlife.

The image stops the scroll. The hook makes her feel caught.

## Contents

- `content/image-posts.md` — 20 ready-to-use image prompts paired with hooks
- `content/hooks.md` — reusable hook bank by theme
- `content/formula.md` — the pain-hook + emotional-truth formula
- `content/posts.json` — structured data: hook, caption, question, hashtags, image path
- `images/` — actual post images, named `post-01.jpg` … `post-20.jpg`
- `automation/scheduler.py` — picks today's post deterministically by date
- `automation/daily_email.py` — sends today's brief via SMTP
- `automation/buffer_push.py` — queues today's post in Buffer via the Buffer API
- `.github/workflows/daily-email.yml` — runs both jobs daily on cron

## Quick start

```bash
cd automation
cp .env.example .env       # fill in SMTP + Buffer creds
pip install -r requirements.txt
python daily_email.py      # send today's email
python buffer_push.py      # queue today's post in Buffer
```

## Daily automation

The GitHub Action runs every day at 13:00 UTC. There are two jobs:

1. **send-email** — always runs. Emails today's brief (hook, caption,
   question, hashtags, visual prompt) to whoever is listed in `EMAIL_TO`.
2. **push-to-buffer** — runs only when the repository variable
   `BUFFER_ENABLED` is set to `true`. Posts today's image + caption to
   every Buffer profile listed in `BUFFER_PROFILE_IDS`.

### Required GitHub secrets

| Secret | Used by | Notes |
|---|---|---|
| `SMTP_HOST` | email | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | email | e.g. `587` |
| `SMTP_USER` | email | full address |
| `SMTP_PASS` | email | Gmail app password (16 chars) |
| `EMAIL_FROM` | email | `Daily Posts <you@gmail.com>` |
| `EMAIL_TO` | email | comma-separated recipients |
| `BUFFER_ACCESS_TOKEN` | buffer | personal access token from https://buffer.com/developers/apps |
| `BUFFER_PROFILE_IDS` | buffer | comma-separated channel IDs |

### Required GitHub variables

| Variable | Used by | Notes |
|---|---|---|
| `BUFFER_ENABLED` | workflow gate | set to `true` to enable Buffer job |
| `IMAGE_RAW_BASE` | buffer | e.g. `https://raw.githubusercontent.com/tarisha-starr/GitHub-folder/main` |

## Adding the images

Drop the 20 images into `images/` named `post-01.jpg` through `post-20.jpg`.
See `images/README.md` for the full mapping. PNGs work too — just update the
`image` field in `content/posts.json` to match the extension.

The Buffer job pulls each image from its public GitHub raw URL, so the
images must be committed to `main` for Buffer to find them.

## Notion

The same content is mirrored to Notion under
**Social Media → Daily Image Posts + Email Automation** as a content
calendar so you can plan, edit, and check off posts as they go live.
