---
name: scale-whats-proven
description: Use this skill when the user is at Level 3 of social media growth (10K to 100K+ followers) and is ready to scale posting frequency from 1x/day to 3-5x/day, repurpose winning posts across platforms, and use AI to handle the volume. Triggers include "scale", "level 3", "ramp posting", "repurpose across platforms", "weekly batch", "100k", or any request to increase output without reinventing the niche. The output goes through the email-approval gate before anything is appended to the live posts file.
---

# Level 3: Scale What's Proven (10K → 100K+ followers)

## When to use

The creator has 10K+ followers and is tempted to reinvent themselves —
new styles, new niches, new formats. Growth slows when they do.

At this level the game is **not** discovery. It is **consistency and volume.**
The creator already knows what works. The job is to do more of it without
losing quality.

## Cross-cutting rules (apply to everything this skill produces)

- **Hook rules:** every hook follows `content/hooks-rules.md`. Under 8 words.
  Pattern interrupt or curiosity gap. Generate 15–20 candidates per post and
  pick the top one.
- **Comments strategy:** every post ships with 5–8 self-comments per
  `content/comments-strategy.md`. At 3–5x/day this is non-negotiable —
  comments are why posts hit millions, not why they hit thousands.
- **Approval gate:** nothing this skill generates goes directly into
  `content/posts.json`. Drafts land in `content/_pending/` and an email goes
  to the user per `content/approval-flow.md`. At Level 3 volume the email
  is a **weekly digest**, not per-post — see "Approval cadence" below.

## Inputs to collect first

In one message, ask only for what's missing:

1. **Current daily target** — 3, 4, or 5 posts/day? Default: 3, ramp to 5.
2. **Active platforms** — Instagram, TikTok, Facebook, YouTube Shorts, etc. Default: all four from `automation/buffer_profiles.json`.
3. **Last month's winners file** — path to the Level 2 winners report (or whichever month was most recent). This is the source of "what's proven."
4. **AI assist level** — drafts only / drafts + visuals / fully generated. Default: drafts + visuals, user refines tone.
5. **Repurpose mode** — single asset across all platforms vs. platform-tailored variants. Default: tailored (vertical video for IG/TikTok/Shorts, square for FB feed).

## The system

### 1. Carry forward Level 2 (do not stop the monthly cycle)

Level 3 does **not** replace the Level 2 monthly winners cycle — it runs on
top of it. Every month:

- Pull the month's data, identify top 5 / bottom 5
- Write the winners report (use the `double-down-winners` skill for this step)
- Feed the new winners into the Level 3 weekly batches

If the monthly winners cycle stops, Level 3 turns into volume without signal.
That's how creators plateau.

### 2. Ramp posting frequency

| Week | Posts/day | Notes |
|---|---|---|
| Week 1 | 1 | baseline (existing daily pipeline) |
| Week 2 | 2 | add a second daily slot — different platform mix |
| Week 3 | 3 | introduce repurposed variants |
| Week 4+ | 3–5 | full Level 3 cadence |

Ramp slowly so the user (and the algorithm) absorbs it.

### 3. Build the weekly batch

Each week, generate a batch of `(daily_target × 7)` posts — e.g. 21 posts
for 3/day, 35 for 5/day. Source: the most recent winners report and any
older winning patterns still pulling weight.

Each post in `content/_pending/scaled-batch.json` must include:

- `id` (continuing from `content/posts.json`)
- `scheduled_for` (ISO date — distribute across the week, multiple per day)
- `slot` (e.g. `morning` / `midday` / `evening`)
- `platform_targets` (list — e.g. `["instagram", "tiktok", "shorts"]`)
- `hook` (under 8 words, picked from a 15–20 candidate batch)
- `caption`
- `question`
- `hashtags`
- `visual` and/or `image`
- `themes`
- `source_winner_ids` — which winning post(s) this leans on
- `winning_pattern` — the hook structure / topic / format being repeated
- `repurpose_of` — set if this is a variant of another post in the same batch

### 4. Repurpose across platforms

For each top-performing post, generate platform-tailored variants instead of
posting the identical asset to all platforms. Examples:

- **IG Reels / TikTok / Shorts** — same vertical video, different first 1.5s hook tuned per platform's tolerance for text
- **IG carousel** — same idea as a 6–8 slide static carousel
- **Facebook feed** — square 1:1 cut with caption-first framing (FB rewards captions)
- **YouTube long** — bundle 4–6 short scripts into one 8–10 min video

Each variant is its own row in the batch with `repurpose_of` set to the
original post's id. Hooks are re-generated per variant (don't reuse the
same hook across platforms — algorithms penalize duplication).

### 5. Generate self-comments for every post in the batch

For every row in the batch, run the self-comments prompt from
`content/comments-strategy.md` and save the 6 self-comments to
`content/_pending/comments/<post-id>.md`. At 3–5x/day this is a lot of
comments — use AI to draft them, then refine the ones for the highest-stakes
slots (morning + evening).

### 6. Approval cadence — weekly digest

At Level 3 volume, per-batch emails are too noisy. Send **one weekly digest**
on Sunday for the week ahead.

Subject: `[REVIEW] Level 3 scaled batch — week of <date>`

The email contains:

1. Headline: "21 posts ready for the week of Mon DD–Sun DD"
2. **Posting calendar** — table grouped by day, then slot, with hook + platform_targets + winning_pattern
3. **By winning pattern** — which patterns are being repeated and how many times each
4. **Repurpose map** — which posts are originals vs. variants
5. **Self-comments** — link to `content/_pending/comments/`
6. APPROVE / EDIT / REJECT block (per `content/approval-flow.md`)

User can approve the whole batch, approve with edits to specific IDs, or
reject and request a regeneration.

### 7. Promote on approval, hand off to the pipeline

Only after the user approves:

- Append `content/_pending/scaled-batch.json` to `content/posts.json`
- Move per-post self-comments from `content/_pending/comments/<id>.md` to `content/comments/<id>.md`
- Delete the now-empty pending files

The existing `automation/scheduler.py` will need a small extension (if it
doesn't already) to honor `scheduled_for` + `slot` for multi-post days.
If the scheduler is still 1/day, **flag this to the user** before scaling
beyond 1/day — don't silently break the pipeline.

### 8. Quality control at scale

At 3–5 posts/day, quality drift is the failure mode. Two safeguards:

- **Top-of-batch review** — the user manually edits the 3 highest-stakes
  posts in each batch (the morning slots) so the week leads with their
  voice, not AI's.
- **Pattern budget** — no single winning pattern can be more than ~30% of
  a week's batch. Hard cap. If the batch tips past that, regenerate the
  surplus from a different pattern.

## What "done" looks like for one weekly cycle

- `content/scaled-batch-<YYYY-WW>.json` (approved) merged into `content/posts.json`
- `content/comments/<id>.md` exists for every post in the batch
- The user has approved the week's plan in one Sunday email
- The monthly Level 2 winners cycle is still running underneath this

## What not to do

- Do **not** stop the Level 2 monthly winners cycle. Level 3 sits on top of it, not in place of it.
- Do **not** reinvent the niche or test new formats just because growth feels slow. The whole Level 3 thesis is the opposite.
- Do **not** post the identical asset to all platforms. Repurpose into platform-native variants.
- Do **not** skip self-comments at Level 3 volume. They scale linearly with post count.
- Do **not** auto-append to `content/posts.json` without an approved weekly digest. The gate is the contract.
- Do **not** ramp past 1/day until the scheduler can handle multi-slot scheduling. Verify first.
- Do **not** let any one winning pattern eat more than 30% of a week. Variation within proven space — not random new ideas.
