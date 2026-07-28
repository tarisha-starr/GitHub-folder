# Daily Image Posts + Email + Buffer

A content kit and daily automation pipeline for emotionally resonant image posts
targeting women over 40 around desire, intimacy, body, and midlife.

The image stops the scroll. The hook makes her feel caught.

## Contents

- `content/image-posts.md` — ready-to-use image prompts paired with hooks
- `content/hooks.md` — reusable hook bank by theme
- `content/formula.md` — the pain-hook + emotional-truth formula
- `content/posts.json` — structured data: hook, caption, question, hashtags, image path
- `images/` — actual post images, named `image-1.jpg` … `image-28.jpg`
- `automation/scheduler.py` — picks today's post deterministically by date
- `automation/daily_email.py` — sends today's brief via SMTP
- `automation/buffer_push.py` — queues today's post in Buffer via the Buffer API
- `automation/fetch_outliers.py` — pulls outlier videos from the YouTube Data API into `content/outliers.csv` (used by the `find-outliers` Level 1 skill)
- `.github/workflows/daily-email.yml` — runs both jobs daily on cron

## Automations

Two layers, built differently on purpose.

**Deterministic pipeline — Python + GitHub Actions.** Date-based rotation,
Buffer pushes, daily emails, image generation. No judgement needed. This is
everything in `automation/*.py` and `.github/workflows/`.

**Judgement work — Claude Skills** in `.claude/skills/`. These need the
connectors (Gmail, Notion, Zoom, Xero, Drive), and **connectors live inside
Claude, not inside GitHub Actions**. A cron job on GitHub can't read the
inbox or a Zoom transcript, so these run as skills instead.

| Skill | Does | Uses |
|---|---|---|
| `/brand-check` | Checks copy against the style guide before it ships | repo |
| `/repurpose-episode` | One recording into 20+ content drafts | Zoom, repo |
| `/call-to-actions` | Transcript into decisions, promises, next steps | Zoom, Notion |
| `/customer-voice` | Mines buyer language for sales copy and FAQs | Zoom, Gmail, Notion |
| `/inbox-triage` | Finds what actually needs a reply, drafts them | Gmail, Notion |
| `/testimonial-organizer` | Social proof sorted by objection and buyer | repo, Gmail, Zoom |
| `/money-brief` | Cash, unpaid invoices, reconciliation exceptions | Xero, Gmail |

See `AUTOMATION-AUDIT.md` for why these seven and not the other 43.

### Brand check

```bash
python3 automation/brand_check.py                    # all content
python3 automation/brand_check.py --text "some copy" # one string
python3 automation/brand_check.py --warn-only        # report, don't fail
```

Catches em-dashes, curly quotes, US spellings, uncontracted forms and banned
phrases from `content/style_guide.md`. Runs in CI on every content change.

It deliberately skips `content/testimonials.json`. Those are real women's own
words and never get restyled.

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

Drop the 28 images into `images/` named `image-1.jpg` through `image-28.jpg`,
matching the `image` field in `content/posts.json`. See `images/README.md`
for the full mapping. PNGs work too — just update the `image` field in
`content/posts.json` to match the extension.

The Buffer job pulls each image from its public GitHub raw URL, so the
images must be committed to `main` for Buffer to find them.

## Notion

The same content is mirrored to Notion under
**Social Media → Daily Image Posts + Email Automation** as a content
calendar so you can plan, edit, and check off posts as they go live.
