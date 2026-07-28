# Automation Audit — all 50, scored against Tarisha's actual business

Audited 28 July 2026 against the real stack: this repo, Notion, Gmail,
Google Calendar, Google Drive, Zoom, Xero, Canva, Slack, Zapier, Buffer.

## The headline

The 50-item list was written for a B2B software company with a sales team,
a support queue, a CRM, a finance department and an HR function. This is a
solo creator business: online programs, a membership, a podcast and a
retreat. One person. No reps, no tickets, no hires, no CRM.

So the honest split:

| Verdict | Count | Meaning |
|---|---|---|
| **Build** | 13 | Real pain, real data already in your systems |
| **Adapt** | 9 | Good idea, but the B2B framing has to be rewritten for a creator business |
| **Skip** | 28 | Assumes staff, departments or systems you don't have |

Building 50 automations for a one-person business would be the mistake here.
Thirteen is the honest number, and seven of them are worth doing first.

## The architecture that matters

Your automations split into two kinds, and they are **not** built the same way.

**Deterministic pipeline → Python + GitHub Actions.** This is what you already
have: `scheduler.py`, `daily_email.py`, `buffer_push.py`, the 16 workflows in
`.github/workflows/`. Rotate content by date, push to Buffer, send an email.
No judgement required. This layer is working and doesn't need changing.

**Judgement work → Claude Skills.** Reading a Zoom transcript, mining customer
language from your inbox, checking a draft against your voice. These need your
connectors, and **your connectors live inside Claude, not inside GitHub Actions.**
A cron job on GitHub cannot read your Gmail or your Zoom recordings. This is why
the new automations in this audit ship as Skills in `.claude/skills/`, invoked by
you or fired on a schedule by a Routine.

Getting this backwards is the single most common way these projects fail. A
GitHub Action cannot see your inbox.

---

## Build now (7)

These have real pain behind them and the data already exists in your systems.

### 20. Brand Consistency Checker → `/brand-check`
**Why it's first:** your git history is full of you fixing this by hand.
"Remove em dashes from prompt captions per brand voice rule". "Strip ornamental
flourishes and force straight quotes". "Drop 'quietly' from prompts 76, 93, 98."
You already wrote the rules down in `content/style_guide.md`. You're just
enforcing them manually, repeatedly, after the fact.

Two layers shipped: a deterministic `automation/brand_check.py` that catches
em-dashes, curly quotes and Americanisms in CI before they ever reach a caption,
and a Skill for the judgement calls (voice, therapist-speak, coaching cliches).

### 11. Content Repurposing Engine → `/repurpose-episode`
**Why:** you have Zoom recordings with VTT transcripts sitting there, a podcast,
and a content pipeline that eats posts. Right now one 2-hour recording produces
one episode. It should produce the episode plus 8 image posts, 3 hooks, a
newsletter section and 5 reels, all in your existing `content/*.json` formats.
This is the highest leverage item on the list for you.

### 7 + 31. Call Action Items → `/call-to-actions`
**Why:** three recorded calls in the last month, every one with a transcript, and
nothing extracted from them. Turns a transcript into decisions, promises you
made, objections raised and next steps, written into Notion.

### 12 + 18 + 25. Customer Voice Miner → `/customer-voice`
**Why:** you have sales pages that need to convert, and your buyers' actual
language is sitting in Zoom transcripts, your `clients` Gmail label and your
workshop testimonials. This mines the recurring phrases, fears and objections,
then feeds them straight into sales copy and FAQ content. Merged with 18 and 25
because for a solo business they're the same job.

### 36 + 21 + 23. Inbox Triage → `/inbox-triage`
**Why:** 14,044 messages in your inbox, 3,006 unread. 68,940 newsletters. Real
buyer questions are drowning in that. This finds the ones that are actually
people asking to work with you, separates them from newsletters, and drafts
replies. Covers the useful half of the support automations too.

### 19. Testimonial Organizer → `/testimonial-organizer`
**Why:** `content/testimonials.json` has every testimonial tagged with the same
seven generic hashtags and no attribution. You can't answer "which testimonial
proves the intimacy objection for a married woman over 45?" This categorises
them by program, buyer type and problem solved, so launches can pull the right
proof instead of the next one in the list.

### 44 + 46 + 47. Money Brief → `/money-brief`
**Why:** Xero is connected and currently unused by any automation. Unpaid
invoices, cash position and receipt matching are the three finance jobs a solo
business actually has. Folded into one skill because they're one weekly review.

---

## Build later (6)

Genuinely relevant, but lower urgency than the seven above.

| # | Automation | Note |
|---|---|---|
| 13 | Content Idea Researcher | Largely covered by your existing `automate-market-research` skill and `find-outliers`. Extend those rather than build new. |
| 14 | Newsletter Drafting | Worth it once `/repurpose-episode` is feeding it material. Build second. |
| 16 | Lead Magnet Delivery | Real, but needs a decision on where the list lives first. See "what's missing" below. |
| 17 | Content Library Organizer | Your `content/` folder is still findable. Revisit when it isn't. |
| 45 | Receipt Organizer | 1,292 emails on the `Receipts` label. Worth doing at tax time. |
| 15 | Campaign Performance Brief | Blocked: no analytics connector. See below. |

---

## Adapt, don't build as written (9)

The B2B framing is wrong but a creator-business version makes sense.

| # | As written | Your version |
|---|---|---|
| 1 | Inbound Lead Qualifier | You don't qualify leads against an ICP. You answer DMs and emails from women who found you. Covered by `/inbox-triage`. |
| 2 | Instant Lead Follow Up | Same. Speed matters at launch time, not always. |
| 4 | Meeting Prep Agent | Your "sales calls" are discovery calls and podcast guest interviews. Guest prep is already handled by `podcast-guest-outreach`. |
| 5 | Proposal Drafting | You have fixed-price programs, not proposals. The retreat at $8,500+ is the one exception where a personalised outline could pay. |
| 9 | Account Research | Rebuilt already as podcast guest research in `podcast-guest-outreach` + the Notion Guest Pipeline. |
| 22 | Reply Drafting | No agents to assist. Folded into `/inbox-triage`. |
| 24 | Conversation Summarizer | No handoffs, you're the only person. Only useful for long client threads. |
| 28 | Customer Onboarding | Real, but this belongs in your email platform's automation, not in Claude. |
| 34 | Weekly Business Report | Meaningful once Xero plus a list platform are both connected. Partly served by `/money-brief`. |

---

## Skip (28)

These assume staff, departments, queues or systems that don't exist here.
Building any of them would be building for a company you aren't.

**Sales pipeline (3, 6, 8, 10)** — all require a CRM with deal stages and reps.
You have programs with fixed prices and a launch calendar. There is no pipeline
to monitor, no lost deals to analyse by competitor, no rep forgetting to follow up.

**Support desk (26, 27, 29, 30)** — no ticket system, no queue, no volume, no
support manager to brief. Refund requests are rare enough to handle by hand.

**Operations for teams (32, 33, 35)** — SOP lookup and approval routing exist to
stop employees asking each other questions. You're one person. You are the SOP.

**HR, all of it (37, 38, 39, 40, 41)** — candidate screening, interview briefs,
employee onboarding, HR Q&A, employee feedback. No employees. Skip entirely.

**Finance for departments (43, 48, 49, 50)** — expense policies, budget variance,
access-controlled document search, month-end close tracking. All assume a finance
team and approved budgets. A solo business closes its books with an accountant.

**Also skip: 42** — invoice data extraction matters when you receive hundreds.
Xero already handles the volume you have.

---

## What's blocking the rest

Three gaps, each of which blocks real automations:

1. **No email list platform connected.** ConvertKit, Kajabi, Mailchimp, whatever
   you actually use, isn't reachable from here. This blocks 16 (lead magnet
   delivery), 14 (newsletter sending) and 28 (onboarding). Connecting it via
   Zapier would unlock all three. Highest-value connection you could make.

2. **No analytics.** No Buffer read access, no Instagram insights, no site
   analytics. This blocks 15 entirely. You're publishing daily and can't see
   what worked, which also weakens the outlier strategy.

3. **FMP connector needs re-authorising.** It's installed but unauthenticated.
   Irrelevant to this work, but worth clearing out.

One correction worth stating plainly: your Notion is doing the job a CRM would
do, and doing it well enough. Don't let anyone sell you a CRM off the back of
this list. The sales automations aren't failing because you lack a CRM, they're
failing because you don't have a sales team.
