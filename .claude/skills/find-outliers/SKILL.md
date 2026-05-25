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

## Inputs to collect first

Before doing any research, ask the user (in one message, only the missing ones):

1. **Niche** — specific, not generic. "Midlife women + intimacy" beats "wellness".
2. **Platforms** — any of Instagram, TikTok, Facebook, YouTube. Default: all four.
3. **Creator's voice / angle** — what they bring (experience, perspective, expertise).
4. **Format preference** — image posts, short video, carousels, long video. Default: whatever the niche's outliers use.
5. **Output location** — where to write the outlier sheet and the derivative posts. Default: `content/outliers.csv` and append to `content/posts.json` style files in this repo.

If the user says "use what's in the repo," read `README.md`, `content/formula.md`,
`content/hooks.md`, and `content/image-posts.md` to infer niche and voice.

## The system

### 1. Define the outlier rule

An outlier is a video that **massively outperforms the creator's average for that account**.
Working rule: views ≥ 10× the creator's median of their last 10 posts.
If the account's median is unknowable, fall back to: views ≥ 10× the platform's
typical view count for accounts of that follower size.

### 2. Build the outlier sheet (50 rows)

Create or append to `content/outliers.csv` with these columns:

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
`content/outlier-patterns.md` covering:

- The top 5 hook structures that recur (e.g. "STOP doing X", "I [result] in [time]")
- The top 3 topics that appear repeatedly
- The top 3 formats that appear repeatedly
- The emotional levers being pulled (curiosity, anger, vindication, recognition, fear)
- What is **absent** in the niche — gaps the user can own

### 4. Generate 50–100 derivative posts

For each post, produce a row in the same shape as `content/posts.json` already
uses in this repo (hook, caption, question, hashtags, image path / visual prompt).
Rules:

- Each derivative must trace back to at least one outlier `id` — record it as `source_outlier_ids`.
- Use the outlier's hook structure and topic as a template, but the user's experience and perspective is the body.
- Do not copy wording. Copy the *shape* of the hook, not the words.
- Hooks must follow the rules in `content/hooks.md` and `content/formula.md` if those exist: under 8 words, pattern interrupt, curiosity gap, no soft openers.
- Vary format across the batch — do not produce 50 of the same template.

### 5. Hand off to the existing pipeline

This repo already has a daily pipeline (`automation/scheduler.py`,
`automation/buffer_push.py`, `automation/daily_email.py`) that picks one post
per day from `content/posts.json`. After generating derivatives, append them
to `content/posts.json` so the existing scheduler can pick them up. Do not
overwrite the existing posts unless the user asks.

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

- `content/outliers.csv` has 50 rows, balanced across platforms and formats.
- `content/outlier-patterns.md` summarizes the patterns and gaps.
- `content/posts.json` has 50–100 new derivative posts appended, each tagged with `source_outlier_ids`.
- The user knows their next move: post the volume, let the algorithm learn, then graduate to Level 2 (double down on winners).

## What not to do

- Do not invent outlier URLs or view counts. If WebSearch can't verify, mark the row `unverified` and move on.
- Do not generate derivatives before the outlier sheet is full — the patterns won't be real.
- Do not collapse the sheet into one platform or one format. Balance is what makes the patterns generalize.
- Do not skip the pattern report — it's the bridge between research and creation.
