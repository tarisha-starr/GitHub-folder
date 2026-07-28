---
name: customer-voice
description: Mine the exact words customers use about their problems, from calls, emails, testimonials and workshop feedback, then turn them into sales copy, FAQs and content ideas. Use when the user says "what are women actually saying", "customer language", "why aren't people buying", "what objections come up", is writing or rewriting a sales page, or needs FAQ and content ideas grounded in real questions.
---

# Customer Voice Miner

Automations #12, #18 and #25 merged, because for a one-person business
they're the same job: find out what buyers actually say, then use their
words instead of yours.

The gap this fills: sales pages get written in *her* language. Buyers
search and think in *their* language. The two are rarely the same.

## Step 1: gather from every source

Work through as many as are available. More sources beat deeper mining of
one source.

**Zoom transcripts** — richest source. `recordings_list`, pull the VTT,
read what *participants* said, not what Tarisha said. Workshop calls where
women talk to each other are gold.

**Gmail** — `search_threads`. Useful queries:
- `label:clients` (64 messages, 27 threads)
- `label:"@ to follow up"`
- `to:me newer_than:1y` filtered to real humans, not newsletters
- Search terms: "is this for me", "my husband", "too late", "I'm scared",
  "does this work if", "can I afford"

Exclude the `Newsletters` label. It's 68,940 messages of other people's
marketing and will pollute everything.

**Testimonials** — `content/testimonials.json`, already in the repo.

**Notion** — `notion-search` for workshop feedback, application form
responses, program pages with participant notes.

## Step 2: extract verbatim, never paraphrase

The whole value is in the exact wording. Log each one as:

```json
{
  "quote": "exactly what she wrote or said",
  "source": "Zoom workshop 16 Jul / client email / testimonial 12",
  "type": "fear | objection | desired outcome | problem | question",
  "buyer": "married 40s / single / post-divorce / unknown"
}
```

A paraphrase like "women worry about their partner's reaction" is
worthless. "I don't know how to bring this up with him without him
thinking I'm saying he's failed me" is a sales page headline.

## Step 3: cluster

Group into recurring themes and count frequency. Order by how often it
comes up, not by how interesting it is.

Expect clusters like: fear of being too late, partner resistance, shame
about wanting more, "is this normal", money, time, fear of being seen,
previous attempts that didn't work.

Note which cluster maps to which program (SERW, Radiant Woman Circle,
From Roommates to Lovers, the Wanaka retreat).

## Step 4: turn it into three outputs

### Sales copy
For each of the top clusters, give:
- the objection in her buyer's exact words
- where on the sales page it should be answered
- a draft answer in Tarisha's voice

Sales pages live in Notion. Search before writing so you're editing the
current version, not an old draft.

### FAQ content (#18)
Any question asked three or more times becomes an FAQ entry, a post, or a
podcast segment. Draft them.

### Content backlog (#25)
Questions that keep coming up and aren't answered anywhere in her existing
content are the knowledge gaps. These are the highest-value content ideas
she has, because demand is already proven. Write them to
`content/drafts/` in the existing format.

## Rules

- **Anonymise everything.** Never carry a name, email address or
  identifying detail into a sales page, a post or a Notion page. Her
  buyers disclose intimate things. "A woman in her forties said" is the
  most specific it ever gets, and only with clearly non-identifying
  content.
- **Testimonials are quoted exactly.** Never restyle them into her voice.
- **Don't use a private client disclosure as marketing copy.** A woman
  telling Tarisha about her marriage in a client email did not consent to
  being a headline. Public testimonials and workshop feedback given for
  that purpose are fair use. A one-to-one confidence is not.
- **Report real frequency.** If something came up twice, say twice. Don't
  round a weak signal up into a trend to make the output look better.

## Finish

Lead with the top three clusters by frequency and what each one means for
the sales page. That's the decision she needs. The full log is reference.
