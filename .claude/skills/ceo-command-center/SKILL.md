---
name: ceo-command-center
description: Build and read the CEO Command Center, the business dashboard covering revenue and profit, offers, leads, marketing, client health, team capacity, decisions, weekly patterns and the AI agents. Use it whenever the owner asks how the business is doing, what is working, where money is leaking, what to focus on this week, which offer is worth pushing, why cash feels tight, how the pipeline or the ads are performing, who is at risk of cancelling, who on the team is drowning, or what the agents are waiting on. Also use it when they want to log a decision, record a week, update any of those numbers, or see the dashboard itself.
---

# CEO Command Center

One dashboard that answers three questions: where is the business growing,
where is it leaking, and what deserves attention next. Nine panels, one data
directory, one renderer.

The name keeps the US spelling because that is what it is called. Everything
you write inside it follows the house rules: UK and NZ spelling, no dashes
used as punctuation.

## The nine panels

| Panel | The question it answers |
|---|---|
| Executive snapshot | Revenue, profit, cash collected, expenses, recurring revenue, forecast |
| Offer scorecard | Which offer sells, converts, delivers cheaply, and keeps clients happy |
| Lead pipeline | Who is in the pipeline, worth what, at which stage, and who has gone quiet |
| Marketing performance | What each channel costs per lead and per client, and what it returns |
| Client health | Onboarding, engagement, renewals, cancellations, and who needs attention |
| Team capacity | Who owns what, who is over capacity, what is blocked, what is late |
| Decision log | What was decided, on what evidence, and whether it worked |
| Weekly patterns | Wins, concerns, surprises, and the priorities that came out of them |
| Agent HQ | What the AI agents own, what is waiting on approval, and how good the output is |

## Where the data lives

Nine JSON files in `business/command-center/`, one per panel. The templates are
in `templates/`, a worked example is in `example/`.

```bash
mkdir -p business/command-center
cp .claude/skills/ceo-command-center/templates/*.json business/command-center/
```

**The data files are gitignored on purpose.** This repository is public, and
these files hold revenue, client names and team workload. Keep them local, or
point `--data` at a directory outside the repo. If the owner wants the numbers
versioned, that is a private repository, not this one. Say so rather than
quietly committing a client list.

## Running it

```bash
# from the repo root
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py

# any directory, any output path, any date
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py \
    --data business/command-center --out dashboards/command-center.html

# see it working before there is any real data
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py \
    --data .claude/skills/ceo-command-center/example \
    --out dashboards/example.html --as-of 2026-08-26
```

Standard library only, no install step. The script prints a short brief to the
terminal (the flags, the headline numbers, last week's priorities) and writes
the HTML. `--brief-out FILE` saves that brief, `--quiet` suppresses it.

To put the dashboard on the owner's phone, render with `--artifact` and pass
the file to the Artifact tool. That flag drops the page wrapper, which the
Artifact tool supplies itself. Publish the render, not the JSON.

## How to work with the owner

**When they ask how the business is doing.** Run the renderer, read the brief,
answer in your own words, worst news first. Do not read the dashboard out panel
by panel. Name the two or three things that matter and say what you would do
about each. Offer the dashboard link second.

**When they give you numbers.** Write them into the right file and re-render.
Numbers arrive in conversation ("we did about twenty two thousand in August,
maybe sixteen out"), in exports, or in screenshots. Put them in the file, then
say what changed in the flags.

**When they ask about one panel.** Read that file and the report, answer the
question, and mention any flag on the same panel that they have not asked
about. That is the whole point of the thing.

**Never invent a number.** An empty field is honest and the dashboard handles
it. A guessed field turns into a forecast, a flag, and eventually a decision.
If a figure is an estimate, say so in the `notes` field next to it.

**Round numbers are fine.** Owners rarely know their delivery cost to the
dollar. A considered estimate they can improve later beats an empty panel,
as long as it is marked as an estimate.

## The weekly rhythm

The dashboard is worth having only if someone looks at it on a schedule. See
`references/weekly-review.md` for the questions to walk through, what to write
into `patterns.json` and `decisions.json`, and how to close the loop on a
decision that has come due.

Monthly: update `finance.json` with the closed month, refresh `offers.json` and
`marketing.json` for the period, review every client's status.

## What each rule means

`references/metrics.md` holds every formula and every threshold: how the
forecast is built, what makes an offer a leak, when a lead counts as gone
quiet, what puts a client on the attention list. When you change a formula in
`scripts/command_center.py`, change that file in the same commit.

`references/data-model.md` is the field-by-field schema for all nine files,
including which fields are optional and what happens when they are missing.

## Structure

```
.claude/skills/ceo-command-center/
  SKILL.md
  references/
    data-model.md        every field in every file
    metrics.md           every formula, threshold and flag
    weekly-review.md     the operating rhythm
  scripts/
    command_center.py    loads the data and works out what it means
    render_dashboard.py  turns that into the HTML dashboard and the brief
  templates/             empty files to copy into business/command-center/
  example/               a fictional business, for demonstrating the thing
```
