---
name: find-outliers
description: Use this skill when the user is at Level 1 of social media growth (0 to 1,000 followers) and needs to find outlier videos in their niche, log them to a spreadsheet, and turn them into 50–100 of their own posts. Triggers include "find outliers", "level 1", "outlier strategy", "build outlier sheet", or any request to research high-performing reference content in a niche before creating original content.
---

# Level 1: Find Outliers (0 → 1,000 followers)

## When to use

The creator has zero or near-zero followers and is trying to grow from scratch.
Original-from-scratch content grows slowly because the algorithm has no signal
about who they are or who should see their content. This skill runs the
outlier-modeling system: find 50 proven videos in the niche, extract the
patterns, and produce 50–100 derivative posts in the creator's voice.

## Cross-cutting rules (apply to everything this skill produces)

- **Hook rules:** every hook generated under this skill follows
  `content/hooks-rules.md`. Under 8 words. Pattern interrupt or curiosity
  gap. Generate 15–20 candidates per post and pick the top one.
- **Comments strategy:** for every derivative post, also generate the 5–8
  self-comments per `content/comments-strategy.md`. Save them under
  `content/_pending/comments/<post-id>.md` so the user has them ready to
  paste in the first 5 minutes after publishing.
- **Approval gate:** nothing this skill generates goes directly into
  `content/posts.json`. Drafts land in `content/_pending/` and an email goes
  to the user per `content/approval-flow.md`. Only after the user approves
  do drafts get promoted to live.

## Inputs to collect first

Before doing any research, ask the user (in one message, only the missing ones):

1. **Niche** — specific, not generic. "Midlife women + intimacy" beats "wellness".
2. **Platforms** — any of Instagram, TikTok, Facebook, YouTube. Default: all four.
3. **Creator's voice / angle** — what they bring (experience, perspective, expertise).
4. **Format preference** — image posts, short video, carousels, long video. Default: whatever the niche's outliers use.
5. **Output location** — where to write the outlier sheet and the derivative posts. Default: drafts to `content/_pending/outliers.csv` and `content/_pending/derivatives.json`; only promoted to `content/posts.json` after email approval.

If the user says "use what's in the repo," read `README.md`, `content/formula.md`,
`content/hooks.md`, and `content/image-posts.md` to infer niche and voice.

## The system

### 1. Define the outlier rule

An outlier is a video that **massively outperforms the creator's average for that account**.
Working rule: views ≥ 10× the creator's median of their last 10 posts.
If the account's median is unknowable, fall back to: views ≥ 10× the platform's
typical view count for accounts of that follower size.

### 2. Build the outlier sheet (50 rows)

Create or append to `content/_pending/outliers.csv` with these columns:

| column | notes |
|---|---|
| `id` | 1–50 |
| `platform` | instagram / tiktok / facebook / youtube |
| `url` | direct link to the post |
| `creator` | handle |
| `creator_avg_views` | their typical post |
| `views` | this post |
| `multiplier` | views / creator_avg_views |
| `hook` | the first line / first 1–2 seconds, verbatim |
| `topic` | one-line description of what the post is about |
| `format` | talking head / b-roll + text / carousel / static image / split-screen / etc. |
| `length` | seconds (or slide count) |
| `cta` | what the post asks for, if anything |
| `why_it_worked` | one sentence — pattern interrupt, controversy, curiosity gap, novelty, emotional truth |

Aim for **balance** across the four platforms and across the format types so the
patterns generalize. Do not fill the sheet with 50 versions of the same idea.

### 3. Extract patterns

After 50 rows are logged, write a short pattern report to
`content/_pending/outlier-patterns.md` covering:

- The top 5 hook structures that recur (e.g. "STOP doing X", "I [result] in [time]")
- The top 3 topics that appear repeatedly
- The top 3 formats that appear repeatedly
- The emotional levers being pulled (curiosity, anger, vindication, recognition, fear)
- What is **absent** in the niche — gaps the user can own

Then send the outlier sheet + pattern report for review per
`content/approval-flow.md`. Subject: `[REVIEW] Level 1 outliers — 50 rows ready`.
Wait for approval before generating derivatives.

### 4. Generate 50–100 derivative posts (after sheet approval)

For each post, produce a row in the same shape as `content/posts.json` already
uses in this repo (hook, caption, question, hashtags, image path / visual prompt).
Rules:

- Each derivative must trace back to at least one outlier `id` — record it as `source_outlier_ids`.
- Use the outlier's hook structure and topic as a template, but the user's experience and perspective is the body.
- Do not copy wording. Copy the *shape* of the hook, not the words.
- Hooks must follow `content/hooks-rules.md` and the niche tone in `content/hooks.md` + `content/formula.md`.
- Vary format across the batch — do not produce 50 of the same template.

Save the batch to `content/_pending/derivatives.json` (same shape as
`content/posts.json`). Do **not** append directly to `content/posts.json`.

### 5. Generate self-comments for every derivative

For each derivative post, run the self-comments prompt from
`content/comments-strategy.md` and save the 6 self-comments to
`content/_pending/comments/<post-id>.md`. These get pasted under the post
in the first 5 minutes after publishing.

### 6. Send the batch for approval

Email per `content/approval-flow.md`. Inline-render the derivatives as a
readable table (hook · topic · format · source_outlier_ids). Subject:

`[REVIEW] Level 1 derivatives — N posts ready`

### 7. Promote on approval, then hand off to the existing pipeline

Only after the user replies `approve` (or merges a PR / moves the file):

- Append `content/_pending/derivatives.json` to `content/posts.json`.
- Move the per-post self-comments from `content/_pending/comments/<id>.md`
  to `content/comments/<id>.md`.
- Delete the now-empty pending files.

The existing pipeline (`automation/scheduler.py`, `automation/buffer_push.py`,
`automation/daily_email.py`) reads `content/posts.json` only — never the
pending folder — so nothing publishes until promotion happens.

## Prompt to use for outlier research

When the user wants Claude to actually go find outliers (vs. them pasting links
in), use this research prompt verbatim with WebSearch:

> Find 50 outlier short-form videos in the niche of **[NICHE]** across Instagram,
> TikTok, Facebook, and YouTube Shorts. An outlier is a video where view count
> is at least 10× the creator's typical post. For each one return: platform,
> URL, creator handle, the creator's typical view count, this post's view count,
> the hook (verbatim first line or first 1–2 seconds), topic, format, length,
> CTA, and one sentence on why it worked. Spread the 50 across the four
> platforms and across format types. Do not return videos from the same creator
> more than 3 times.

## Prompt to use for derivative generation

> You are a content strategist for a creator in the niche of **[NICHE]** with
> the voice and perspective of **[VOICE]**. Below are 50 outlier posts with
> their hooks, topics, and formats. Generate **[N]** original derivative posts
> in this creator's voice. Each post must: cite which outlier IDs it draws
> from, use a hook under 8 words, follow the hook rules (pattern interrupt,
> curiosity gap, no soft openers), and pair with a visual prompt. Vary format
> across the batch. Do not copy wording — copy the shape.

## What "done" looks like

- `content/outliers.csv` has 50 approved rows, balanced across platforms and formats.
- `content/outlier-patterns.md` summarizes the patterns and gaps.
- `content/posts.json` has 50–100 new derivative posts appended, each tagged with `source_outlier_ids`.
- `content/comments/<id>.md` exists for every new post with 5–8 self-comments ready to paste.
- The user has approved every artifact by email before it went live.
- Next move: post the volume, let the algorithm learn, then graduate to Level 2.

## What not to do

- Do not invent outlier URLs or view counts. If WebSearch can't verify, mark the row `unverified` and move on.
- Do not generate derivatives before the outlier sheet is approved — the patterns won't be real.
- Do not collapse the sheet into one platform or one format. Balance is what makes the patterns generalize.
- Do not skip the pattern report — it's the bridge between research and creation.
- Do not auto-append to `content/posts.json` without an explicit approval. The gate is the contract.
- Do not ship a post without its self-comments. Comments are not optional at this level.
