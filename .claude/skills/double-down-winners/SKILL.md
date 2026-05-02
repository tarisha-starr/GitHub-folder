---
name: double-down-winners
description: Use this skill when the user is at Level 2 of social media growth (1,000 to 10,000 followers) and growth has slowed. Triggers include "double down", "level 2", "winners analysis", "monthly review", "what's working", or any request to analyze top vs bottom posts and produce a content plan that doubles down on winning patterns. The output goes through the email-approval gate before anything is appended to the live posts file.
---

# Level 2: Double Down On Winners (1K → 10K followers)

## When to use

The creator has 1K–10K followers but growth has stalled. They are still
posting random content hoping something pops. At this level, random kills
growth — the algorithm is learning the audience and needs clear signals.

The job is **not** to invent new content types. The job is to study what
already worked for them and do more of it.

## The cycle (run monthly)

| Week | Action |
|---|---|
| Week 1 | Pull the month's data. Identify top 5 and bottom 5 posts. Write the winners report. |
| Week 2–4 | Generate and post the 20 double-down posts that lean into the winning hooks, topics, and formats. |
| End of month | Review again. Repeat. |

## Cross-cutting rules (apply to everything this skill produces)

- **Hook rules:** every hook generated under this skill follows
  `content/hooks-rules.md`. Under 8 words. Pattern interrupt or curiosity gap.
  No soft openers, no advice voice, no clinical voice. Generate 15–20 hook
  candidates per post and pick the top one.
- **Comments strategy:** for every post that ships, also generate the 5–8
  self-comments per `content/comments-strategy.md`. Save them under
  `content/_pending/comments/<post-id>.md` so the user has them ready to
  paste in the first 5 minutes after publishing.
- **Approval gate:** nothing this skill generates goes directly into
  `content/posts.json`. Drafts land in `content/_pending/` and an email goes
  to the user per `content/approval-flow.md`. Only after the user approves
  do drafts get promoted to live.

## Inputs to collect first

In one message, ask the user only for what's missing:

1. **Where is the post-level data?** Options:
   - CSV they paste / drop in the repo (recommended)
   - Per-platform exports (IG insights, TikTok analytics, YT Studio, Meta)
   - Manual list of top 5 / bottom 5 with metrics
2. **Period** — which month/range to analyze. Default: trailing 30 days.
3. **Metrics priority** — views, saves, shares, comments, watch time, follows-from-post. Default order: shares > saves > comments > views.
4. **Niche/voice confirmation** — same niche file as Level 1, or has it shifted?

## Step 1 — Build the winners report

Run this analysis prompt **on the data the user provided**, and write the
output to `content/_pending/winners-report.md`:

> You are a social media growth analyst. Here are my top 5 and bottom 5
> posts from this month with their views, comments, shares, and saves.
> Identify what my winning posts have in common, what my losing posts have
> in common, and build me a content plan for next month that doubles down
> on the winning patterns. Give me 20 specific post ideas with hooks
> already written.

The report file must contain:

- **Top 5** — for each: hook (verbatim), topic, format, metrics
- **Bottom 5** — same fields
- **Winning patterns** — the hook structures, topics, formats, and emotional levers that recur in the top 5
- **Losing patterns** — what the bottom 5 share (and how to stop doing it)
- **Plan for next month** — 20 post ideas, each with hook + topic + format + which winning pattern it doubles down on

## Step 2 — Send the winners report for approval

Email the report per `content/approval-flow.md`. Subject:

`[REVIEW] Level 2 winners report — <month>`

Wait for approval before generating the 20 posts.

## Step 3 — Generate the 20 double-down posts

After approval, expand the 20 ideas into full posts. Each post must include:

- `id` (continuing from the last id in `content/posts.json`)
- `hook` — under 8 words, picked from a generated batch of 15–20 candidates
- `caption`
- `question` (engagement question)
- `hashtags`
- `visual` (visual prompt) and/or `image` path
- `themes`
- `source_winner_ids` — which top-5 post(s) this one doubles down on
- `winning_pattern` — the specific pattern (hook structure / topic / format) it leans into

Save the batch to `content/_pending/doubledown.json` (same shape as
`content/posts.json`). Do **not** append directly to `content/posts.json`.

## Step 4 — Generate the self-comments for every post in the batch

For each post in the batch, run the self-comments prompt from
`content/comments-strategy.md` and save the 6 self-comments to
`content/_pending/comments/<post-id>.md`. These will be pasted under the
post in the first 5 minutes after publishing.

## Step 5 — Send the batch for approval

Email per `content/approval-flow.md`. Inline-render the 20 posts as a table
(hook · topic · format · source_winner_ids · winning_pattern). Subject:

`[REVIEW] Level 2 double-down — 20 posts ready`

Include a sublink to `content/_pending/comments/` so the user can spot-check
the self-comments too.

## Step 6 — Promote on approval

Only after the user replies `approve` (or merges a PR / moves the file):

- Append the batch from `content/_pending/doubledown.json` to `content/posts.json`.
- Move the per-post self-comments from `content/_pending/comments/<id>.md`
  to a live location the user can find quickly on posting day (e.g.
  `content/comments/<id>.md`).
- Delete the now-empty pending files.

The existing `automation/scheduler.py` will pick up the new posts in date
order, and `automation/daily_email.py` will continue to send the daily brief.

## What "done" looks like for one monthly cycle

- `content/winners-report-<YYYY-MM>.md` — the approved analysis (moved out of `_pending/`).
- `content/posts.json` — has 20 new double-down posts appended.
- `content/comments/<id>.md` — one file per new post with the 5–8 self-comments ready to paste.
- The user has approved every artifact by email before it went live.

## What not to do

- Do **not** invent new content types because growth feels slow. The whole point of Level 2 is to stop doing that.
- Do **not** skip the bottom-5 analysis. Knowing what to stop doing is half the value.
- Do **not** auto-append to `content/posts.json` without an explicit approval. The gate is the contract.
- Do **not** ship a post without its self-comments. Comments are not optional at this level.
- Do **not** carry over Level 1's outlier-derived hooks unedited — by Level 2 the user has their **own** winning hook structures. Use those.
