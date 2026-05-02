# Approval Flow — Email Before Anything Goes Live

**Hard rule for every level: nothing posts anywhere until you approve it by email.**

The existing pipeline (`automation/scheduler.py`, `automation/buffer_push.py`,
`automation/daily_email.py`) sends today's brief by email and queues to Buffer.
This document defines the additional **pre-publish approval gate** that sits
*before* anything reaches `content/posts.json` (which is the source the
scheduler reads from).

## The gate

```
research / generation
        │
        ▼
content/_pending/<artifact>     ← drafts land here, NOT in posts.json
        │
        ▼
email → user inbox              ← user reviews
        │
        ▼ (user replies "approve" or edits the file in-repo)
        ▼
content/posts.json              ← only now does it become live-eligible
        │
        ▼
scheduler / buffer_push / daily_email
```

## Where drafts live

Drafts wait in `content/_pending/` until approved. Suggested filenames:

- `content/_pending/outliers.csv` — Level 1 outlier sheet
- `content/_pending/outlier-patterns.md` — Level 1 pattern report
- `content/_pending/derivatives.json` — Level 1 derivative posts
- `content/_pending/winners-report.md` — Level 2 monthly winners analysis
- `content/_pending/doubledown.json` — Level 2 double-down posts
- `content/_pending/scaled-batch.json` — Level 3 scaled batch
- `content/_pending/comments/<post-id>.md` — self-comments for a post
- `content/_pending/hooks-batch.md` — generated hook candidates

Nothing in `content/_pending/` is read by the scheduler. It is review-only.

## Email format for review

The approval email should always include, inline (so user can read on phone
without opening attachments):

1. A one-line summary ("50 outliers ready for review", "20 double-down posts ready").
2. The full sheet/posts rendered as a readable HTML table (not just an attachment).
3. A clear **APPROVE / EDIT / REJECT** instruction block at the bottom:

   - **APPROVE** → reply with the word `approve` (or merge the PR / approve in repo)
   - **EDIT** → reply with the row IDs to change and what to change
   - **REJECT** → reply with the word `reject` and the batch is deleted

4. The git branch + a link to the file in GitHub so user can edit in-browser
   if they want to.

## Implementation notes

- Reuse `automation/daily_email.py` SMTP plumbing. Add a sibling script (e.g.
  `automation/review_email.py`) that takes a draft path + subject and emails
  the rendered contents. Do not invent a new email stack.
- Until the user wires up reply-parsing, "approval" = the user manually moves
  the file from `content/_pending/` to its live location and commits, OR
  merges a PR. That's fine — the gate's purpose is to make sure no automation
  ever auto-promotes a draft.
- The buffer/posting workflows must continue to read **only** from
  `content/posts.json`, never from `content/_pending/`.

## Per-level checkpoints

- **Level 1:** outlier sheet → email → approve → derivatives generated → email → approve → append to `posts.json`.
- **Level 2:** monthly winners report → email → approve → 20 double-down posts generated → email → approve → append to `posts.json`.
- **Level 3:** scaled batch (3–5/day) → email in weekly digest form → approve → append to `posts.json`.
- **All levels:** generated hooks → email → approve before they're attached to any post. Self-comments → email → approve before posting day.

## Subject line conventions

- `[REVIEW] Level 1 outliers — 50 rows ready`
- `[REVIEW] Level 1 derivatives — N posts ready`
- `[REVIEW] Level 2 winners report — <month>`
- `[REVIEW] Level 2 double-down — N posts ready`
- `[REVIEW] Level 3 scaled batch — week of <date>`
- `[REVIEW] Hooks batch — N candidates`
- `[REVIEW] Self-comments — post #<id>`

The `[REVIEW]` prefix makes it filterable in the inbox and distinct from the
existing `Daily post #N` sends.
