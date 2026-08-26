# The weekly review

Forty minutes, same slot every week. The dashboard is not the review, it is the
agenda. What makes it worth the time is that it ends in written priorities and,
sometimes, a logged decision.

## Before the review

Update whatever moved: leads touched or closed, clients who started or went
quiet, hours committed, agent activity. Then render:

```bash
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py
```

Read the brief that prints. If a data warning appears at the top, fix the data
first. Reviewing a stale panel wastes the whole slot.

## The walk through

Work down the flags, not down the panels. The flags are already ordered by
severity, and most weeks the first three are the review.

For each flag, three questions:

1. Is it true? A threshold crossed is not a fact about the business. A quiet
   lead may have told you last week they are away until March.
2. Is it new, or has it been there a month? A flag that keeps reappearing is
   either a decision nobody has made or a threshold set wrong.
3. What would have to change for it to go away, and is that worth doing?

Then the two questions the flags cannot answer:

- **What went better than expected?** Wins are the input to the next offer, and
  they are the thing that never gets written down.
- **What surprised you?** In either direction. Surprises are where the model of
  the business is wrong, which is more valuable than any flag.

## Writing the week

Append to `patterns.json`, `week_of` set to the Monday:

```json
{"week_of": "2026-08-24",
 "wins": [],
 "concerns": [],
 "surprises": [],
 "priorities": []}
```

Rules that keep it useful:

- The owner's own words. Do not translate "the retreat is not selling and I feel
  sick about the venue deposit" into "retreat conversion below target".
- Concerns can be feelings. A concern with no number behind it is often the
  earliest signal there is, and next month's numbers will tell you whether it
  was right.
- Three to five priorities, no more. A list of twelve is a list of none.
- Every priority names a person and a week. "Kill or fix Google search ads" is a
  priority. "Look at marketing" is a mood.

At the next review, read last week's priorities back before anything else. The
dashboard shows them under the weekly panel for exactly that reason.

## When a decision comes out of it

If the week produced a real decision, one that spends money, changes a price,
starts or stops something, log it in `decisions.json` while it is fresh:

```json
{"date": "2026-08-24", "decision": "", "owner": "",
 "supporting_data": "", "expected_outcome": "",
 "review_date": "", "status": "open", "result": "", "verdict": null}
```

`expected_outcome` is the field people skip and it is the one that makes the log
worth keeping. Without it, the review in eight weeks is a discussion about
whether things feel better.

Set `review_date` far enough out that the decision could have worked: a price
change needs a quarter, an ad change needs a fortnight.

## Closing a decision

When the dashboard flags a decision as due, set `status` to `reviewing`, write
what actually happened in `result`, and give it a verdict:

- `worked`, the expected outcome happened
- `mixed`, some of it happened, or it happened at a cost you did not expect
- `did_not_work`, it did not

Then set `status` to `closed` and act on it. A decision sitting at
`did_not_work` while still running is flagged high severity every week until
something changes, which is the point.

Nobody hits better than about two thirds. The hit rate on the panel is there to
make the failures ordinary enough to write down.

## The monthly pass

Once a month, on top of the weekly:

- Close out `finance.json` for the month just finished
- Refresh `offers.json` for the new period, including delivery costs
- Refresh `marketing.json` for the new period, keeping the old rows
- Walk every client and set their status honestly, especially `at_risk`
- Update `team.json` capacity if anyone's hours changed
- Review Agent HQ: is each agent still earning its place, is the rework rate
  falling, is anything waiting on approval that has been waiting a month

## The quarterly question

Once a quarter, ignore the flags and ask one thing: which offer is carrying the
business, and what would happen if it stopped. The share of profit column in the
offer scorecard usually answers it, and the answer is usually less comfortable
than the revenue number suggests.
