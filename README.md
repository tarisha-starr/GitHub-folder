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

## Brave question cards (Mon, Wed, Fri), two versions

Each card shows only the question and the website. Two versions post on
the same days, each as its own webhook call with a `brand` field so the
Zap can send it to the right account:

| brand | questions | cards | look |
|---|---|---|---|
| `serw` | `content/brave_questions.json` (40, for women) | `images/questions/serw/` | burgundy, navy, gold; SEXUALEMPOWERMENTFORWOMEN.COM footer bar |
| `couples` | `content/couples_questions.json` (40, for couples) | `images/questions/couples/` | Soft Autumn pine palette; theloveadventure.com |

- Re-render after editing either JSON: `node automation/render_question_cards.js`
  (or `BRAND=couples node ...` for one version).
- `automation/zapier_push_question.py` picks the card for today in NZ time.
  It posts only on Monday, Wednesday and Friday, starting on
  `QUESTIONS_LAUNCH_DATE` (default 2026-11-16), and stops after card 40.
- `.github/workflows/question-cards.yml` runs it at about 7:37am NZ.
- Optional repo variable `QUESTION_BRANDS` (default `serw,couples`) limits
  which versions post.

To switch it on, set `QUESTIONS_ENABLED=true` (alongside the existing
`ZAPIER_ENABLED=true`). In the Zap, route `post_type: "question"` by
`brand`: `serw` to the Sexual Empowerment for Women accounts, `couples`
to The Love Adventure accounts.

### Weekly reel: The Second Awakening (Sunday, SERW only)

Every Sunday a 9:16 reel recaps that week's three SERW questions: a title
card, the three questions (question and website only), then an end card
asking "Which one got you? Comment 1, 2 or 3." 14 reels in all (the last is a
single-question finale), posting from the Sunday after `QUESTIONS_LAUNCH_DATE`.

- `content/second_awakening_reels.json`: which questions each reel uses, plus its caption
- `videos/awakening/reel-<id>.mp4`: the reels (about 23 seconds, silent audio
  track, so add music in the app if you want it)
- `automation/render_awakening_reels.js`: re-render after editing questions
- `automation/zapier_push_reel.py` + `.github/workflows/awakening-reel.yml`:
  sends `post_type: "reel"`, `brand: "serw"` with `video_url` at about
  11:23am NZ on Sundays

It uses the same `QUESTIONS_ENABLED` switch as the cards.
