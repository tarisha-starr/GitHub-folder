---
name: monetize-audience
description: Use this skill when the user wants to turn their audience into income. Triggers include "monetize", "income streams", "digital product", "launch", "membership", "brand deals", "affiliate", "monetization roadmap", or any request about making money from followers. Maps strategy to current follower count (0-1K through 50K+) and produces a 90-day roadmap that goes through the email-approval gate before any launch content is appended to the live posts file.
---

# Monetize the Audience

## When to use

The creator is growing but making $0. Followers without monetization is a
hobby. This skill builds the income-stream plan for their current follower
count and writes a 90-day roadmap. Any launch content (announcement posts,
sales-page copy, email sequences) goes through the same approval gate as
every other artifact in this repo.

**Rule: don't wait for 100K. Start at 1K.**

## Cross-cutting rules (apply to everything this skill produces)

- **Hook rules:** every launch post, announcement, and email subject line
  follows `content/hooks-rules.md`. Under 8 words for hooks. No soft
  openers. Pattern interrupt or curiosity gap.
- **Comments strategy:** launch posts ship with 5–8 self-comments per
  `content/comments-strategy.md`. The launch post's comment section is the
  highest-stakes comment section the creator will run — treat it as a
  mini-FAQ for the offer (objections, price, who it's for, what's inside).
- **Approval gate:** the roadmap, the offer copy, and every launch post
  land in `content/_pending/` and go to the user by email per
  `content/approval-flow.md`. Nothing reaches `content/posts.json` or any
  external platform without explicit approval.

## The income ladder

Pick the rung that matches the creator's **current** follower count. Don't
skip rungs.

| Followers | Move | Why |
|---|---|---|
| 0 – 1K | Build the skill. Post. Learn what works. | No audience yet — no leverage. Use the `find-outliers` skill. |
| 1K – 5K | **Launch one small digital product.** $9 – $47 range. | Smallest validated income stream. Proves people will pay. |
| 5K – 10K | Add **affiliate marketing** + **brand deals.** | Audience is big enough that brands and affiliate networks will pay. |
| 10K – 50K | Launch a **paid community** or **membership.** Recurring revenue. | Audience is loyal enough for a monthly $. Compound income. |
| 50K+ | **Stack multiple income streams.** Products + community + brand + affiliate + content. | At this size diversification beats focus. |

The user's own stack at scale: private AI community, digital products,
brand deals, content. **Started with one simple product at 2,000 followers.**

## Inputs to collect first

In one message, ask only for what's missing:

1. **Niche** — same as the levels skills, confirm it hasn't shifted.
2. **Current follower count** (per platform if it varies meaningfully).
3. **Existing income streams** — anything already running, even small.
4. **Time available** — hours/week the creator can give monetization on top of content.
5. **Audience size on email** — list size if they have one. If zero, list-building moves to month 1 of the roadmap.
6. **What the audience already asks for** — DMs, comments, repeated questions. Best signal for what to package and sell.

## Step 1 — Build the 90-day roadmap

Run this prompt **with the user's actual numbers**, and write the output to
`content/_pending/monetization-roadmap.md`:

> You are a creator monetization strategist. My niche is **[NICHE]**. I have
> **[NUMBER]** followers. Build a 90-day monetization roadmap. Give me 3
> income streams I can start this month with step-by-step setup. Focus on
> digital products and community. Include realistic income expectations for
> month 1 vs month 6.

The roadmap file must contain:

- **Current rung** — which row of the income ladder the creator is on
- **3 income streams to start this month** — for each: what it is, why it fits this audience, step-by-step setup, realistic month-1 revenue, realistic month-6 revenue
- **Month 1 plan** — week-by-week tasks (build, soft-launch, hard-launch)
- **Month 2 plan** — iterate on what sold, expand the next stream
- **Month 3 plan** — stack a recurring stream (community / membership) if the audience size supports it
- **Pricing** — anchored to ladder rung, not aspirational
- **What to skip** — streams that look obvious but won't pay at this size (e.g. courses at 800 followers, brand deals at 2K)

## Step 2 — Send the roadmap for approval

Email per `content/approval-flow.md`. Subject:

`[REVIEW] Monetization roadmap — 90 days`

Wait for approval before producing any launch content.

## Step 3 — Generate the launch artifacts (after roadmap approval)

For the **first** income stream in the approved roadmap, produce:

1. **Offer copy** → `content/_pending/launch/<offer-slug>/offer.md`
   - One-line promise (under 8 words)
   - Who it's for / who it's not for
   - What's inside (3–5 bullets)
   - Price + payment link plan
   - Guarantee or risk-reversal
2. **Sales page draft** → `content/_pending/launch/<offer-slug>/sales-page.md`
3. **Launch post sequence** → `content/_pending/launch/<offer-slug>/posts.json`
   - 5 launch posts spaced over 7–10 days (tease → reveal → social proof → objection-handler → last call)
   - Same shape as `content/posts.json`: hook, caption, question, hashtags, visual, themes
   - Each post tagged `launch_offer: <offer-slug>` and `launch_phase: <tease|reveal|proof|objection|last-call>`
4. **Email sequence** → `content/_pending/launch/<offer-slug>/emails.md`
   - 4 emails matching the post phases for whoever is on the user's list
5. **Self-comments** for each launch post → `content/_pending/comments/<post-id>.md`
   - At launch the comments are objection-handlers + FAQ (price, fit, what's inside, refund, time commitment)

## Step 4 — Send the launch artifacts for approval

Email per `content/approval-flow.md`. Subject:

`[REVIEW] Launch — <offer-slug> — N posts + sales page`

Inline-render the offer one-pager, the 5 launch posts as a table, and a
link to the sales page draft and email sequence.

## Step 5 — Promote on approval

Only after the user replies `approve` (or merges a PR / moves the file):

- Append `content/_pending/launch/<offer-slug>/posts.json` to `content/posts.json`
- Move launch self-comments from `content/_pending/comments/<id>.md` to `content/comments/<id>.md`
- Move sales page + offer copy + emails to `content/launches/<offer-slug>/`
- Delete the pending files

The existing scheduler will pick up the launch posts in date order. The
sales page and emails are reference docs the user (or a future automation)
ships to their funnel.

## Step 6 — Track and iterate (monthly)

After the launch finishes, write a results file to
`content/launches/<offer-slug>/results.md` covering:

- Revenue (gross, refunds, net)
- Conversion (clicks → buyers)
- Top-performing post in the sequence
- Top objections raised in comments / DMs (these become the next launch's copy)
- What to keep, what to change, what to kill

Then loop: pick the **second** income stream from the roadmap and repeat
Steps 3–5.

## Per-rung guardrails

- **1K – 5K:** keep the product **small** ($9 – $47). Don't build a $497 course at 2,000 followers — conversion math doesn't work, and the time spent kills content output.
- **5K – 10K:** brand deals only with brands the audience would actually use. One bad sponsorship at this stage tanks trust. Affiliate links go in caption + bio, not retrofitted into existing posts.
- **10K – 50K:** community price floor at $19/mo or $97/yr — anything cheaper is more support work than the revenue justifies.
- **50K+:** stop launching new products until the existing 3–4 streams are running clean. Add streams only when the bottleneck is income, not attention.

## What "done" looks like

- `content/launches/<offer-slug>/` exists with offer copy, sales page, emails, results
- `content/posts.json` has the approved launch sequence appended
- `content/comments/<id>.md` exists for every launch post
- The user has approved the roadmap and the launch artifacts by email before any of it went live
- Next move is recorded: either iterate on the same offer or pick the next stream from the roadmap

## What not to do

- Do **not** wait for 100K. Start at 1K with one small product.
- Do **not** skip rungs. A $497 course at 2K followers fails for math reasons, not effort reasons.
- Do **not** launch without a sales page draft and an objection-handler post in the sequence. Both must exist before posting starts.
- Do **not** auto-append launch posts to `content/posts.json` without explicit approval. The gate is the contract.
- Do **not** publish launch self-comments that read like ads. Each one is a mini-FAQ — title, objection, answer.
- Do **not** stop the content cadence during a launch. Launch posts go *into* the existing schedule, not in place of it.
