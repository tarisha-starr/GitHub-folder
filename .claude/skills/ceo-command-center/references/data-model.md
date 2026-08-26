# The nine files, field by field

All nine live in one directory, default `business/command-center/`. Every money
field is in the currency set once in `finance.json`. Every date is `YYYY-MM-DD`.
Every month is `YYYY-MM`.

Missing files become a warning at the top of the dashboard and an empty panel.
Missing fields inside a file are treated as zero or unknown, never guessed. Keys
starting with an underscore are ignored by every calculation, so the templates
can carry their own documentation in `_help`.

One underscore key does reach the page: a `_note` at the top level of any file
is printed under the masthead. Use it for a caveat that applies to everything
below, "figures exclude GST", "August is part-estimated", and that is how the
example data announces that none of its numbers are real.

Rows with an empty name are treated as template placeholders and skipped, so a
freshly copied set of templates renders as empty panels rather than flags about
nobody.

## finance.json

```json
{
  "currency": "NZD",
  "cash_on_hand": 41200,
  "months": [
    {"month": "2026-08", "revenue": 23150, "cash_collected": 19870,
     "expenses": 16050, "recurring_revenue": 9350, "new_customers": 8}
  ],
  "committed_future_revenue": [
    {"month": "2026-09", "amount": 4800, "note": "Two intensives paid in full"}
  ]
}
```

| Field | Notes |
|---|---|
| `currency` | Used for every money figure on the page. |
| `cash_on_hand` | The bank balance the day you updated the file. Drives runway. |
| `months[].month` | Oldest first is tidiest, but the file is sorted on load. |
| `months[].revenue` | Invoiced or booked in the month. |
| `months[].cash_collected` | What actually landed. The gap between these two is a flag. |
| `months[].expenses` | Everything paid out, contractors and ad spend included. |
| `months[].recurring_revenue` | The part that repeats next month with no new sale. |
| `months[].new_customers` | First-time buyers. |
| `committed_future_revenue` | Signed and undelivered, by the month it lands in. Feeds the forecast. |

At least two months are needed before anything shows a change, six before the
growth comparison means much.

## offers.json

```json
{
  "offers": [
    {"name": "Couples Intensive", "period": "2026-08", "price": 2400,
     "opportunities": 14, "units_sold": 5, "delivery_cost": 3100, "refunds": 0,
     "satisfaction": {"avg_score": 4.8, "scale": 5, "responses": 5},
     "notes": "Waitlist forming."}
  ]
}
```

| Field | Notes |
|---|---|
| `period` | Only the newest period is scored. Keep older rows for history. |
| `opportunities` | Anyone who could have bought: calls held, applications, checkouts started. Leave at 0 if you do not track it and the conversion column stays blank. |
| `delivery_cost` | Total for the units sold, not per unit. Contractor time, venue, materials, support. |
| `satisfaction` | Any scale, as long as `scale` says which. Under 3 responses the flag stays quiet. |
| `notes` | Where an estimate gets declared as an estimate. |

Subscriptions: monthly price in `price`, active members in `units_sold`, and
note it. The row then reads as one month of that subscription.

## leads.json

```json
{
  "follow_up_days": 7,
  "stage_weights": {"new": 0.1, "qualified": 0.25, "proposal": 0.5,
                    "negotiation": 0.75, "won": 1.0, "lost": 0.0},
  "leads": [
    {"name": "M. Whitiora", "source": "Podcast", "offer": "Couples Intensive",
     "stage": "negotiation", "value": 2400, "expected_close": "2026-09-04",
     "last_touch": "2026-08-24", "owner": "Tarisha", "next_step": "Send payment link"}
  ]
}
```

| Field | Notes |
|---|---|
| `stage` | Any key in `stage_weights`. Rename or add stages freely, the panel follows the file. |
| `stage_weights` | Probability each stage closes. Replace the defaults with your own close rates once you have enough closed deals. |
| `value` | Full value if it closes. For a subscription, use the value of the committed term. |
| `expected_close` | Puts the lead in a forecast month. A lead with no date is counted in the pipeline but not the forecast. |
| `last_touch` | Drives the follow-up flag. |
| `next_step` | One line, and it should be a verb. |

Keep won and lost leads in the file. They are what the win rate is made of.

## marketing.json

```json
{
  "min_spend_for_ranking": 200,
  "campaigns": [
    {"name": "Intensive launch", "channel": "Meta ads", "period": "2026-08",
     "spend": 1800, "leads": 96, "customers": 6, "revenue": 7400, "notes": ""}
  ]
}
```

| Field | Notes |
|---|---|
| `channel` | The grouping the table ranks on. Keep the spelling consistent across periods or the comparison breaks. |
| `spend` | Cash out. Zero for organic, which then shows no cost per lead. |
| `customers` | Leads that became paying clients, not leads that replied. |
| `revenue` | What you attribute to the campaign. Attribution is a judgement, so write your rule in `notes` and keep it steady. |
| `min_spend_for_ranking` | Below this, a channel is shown but not ranked. |

Keep last period's rows. Cost per lead is compared against the same channel and
campaign name in the period before.

## clients.json

```json
{
  "onboarding_days": 14,
  "quiet_days": 21,
  "clients": [
    {"name": "N. Kapoor", "offer": "Radiant Woman Membership", "status": "active",
     "value": 47, "start_date": "2026-02-11", "renewal_date": "2026-09-11",
     "last_engagement": "2026-08-25", "engagement": 88, "owner": "Sam",
     "churned_on": null, "notes": ""}
  ]
}
```

| Field | Notes |
|---|---|
| `status` | `onboarding`, `active`, `at_risk`, `renewing`, `churned`. |
| `value` | Per month for a subscription, or the value of the programme for a one-off. Say which in `notes` if it matters. |
| `renewal_date` | `null` when there is nothing to renew. |
| `last_engagement` | The last time they showed up or replied. Whatever "showed up" means for that offer, applied consistently. |
| `engagement` | 0 to 100, your own measure. Sessions attended, lessons opened, replies. A crude score used the same way every week beats a precise one used once. |
| `churned_on` | The cancellation date. Only for churned clients. |

## team.json

```json
{
  "overload_threshold": 0.9,
  "idle_threshold": 0.6,
  "people": [
    {"name": "Sam", "role": "Operations", "capacity_hours": 25,
     "committed_hours": 21,
     "responsibilities": ["Pipeline follow-up", "Membership support"],
     "deadlines": [{"item": "Renewal outreach", "due": "2026-08-29", "status": "at_risk"}],
     "blockers": [{"item": "No access to the ads account", "waiting_on": "Tarisha"}]}
  ]
}
```

| Field | Notes |
|---|---|
| `capacity_hours` | Hours a week actually available for this business. |
| `committed_hours` | Hours already spoken for. |
| `responsibilities` | What they own, not what they did last week. |
| `deadlines[].status` | `on_track`, `at_risk`, `done`. Anything past its date and not done is treated as overdue whatever the status says. |
| `blockers[].waiting_on` | Name the person. A blocker with nobody attached never moves. |

Contractors belong here too, with their contracted hours as capacity.

## decisions.json

```json
{
  "decisions": [
    {"date": "2026-05-06", "decision": "Raise the Intensive from 1800 to 2400",
     "owner": "Tarisha", "supporting_data": "Sold out three months running at 1800",
     "expected_outcome": "Same volume, a third more revenue per client",
     "review_date": "2026-08-06", "status": "closed",
     "result": "Volume held at five a month, revenue per client up 33 percent",
     "verdict": "worked"}
  ]
}
```

| Field | Notes |
|---|---|
| `supporting_data` | The number or evidence behind it. Write it while you still remember, because in three months nobody will. |
| `expected_outcome` | What you said would happen. This is what makes the review possible. |
| `review_date` | When you promised to check. Past this date and not closed is a flag. |
| `status` | `open`, `reviewing`, `closed`. |
| `verdict` | `worked`, `mixed`, `did_not_work`, or `null` while open. |

Log the decision when you make it, not when you review it. A log written in
hindsight only ever records decisions that worked.

## patterns.json

```json
{
  "weeks": [
    {"week_of": "2026-08-24",
     "wins": ["Best week of the month for referrals"],
     "concerns": ["Expenses up for the third month running"],
     "surprises": ["A lead who went quiet in June came back and closed"],
     "priorities": ["Kill or fix Google search ads"]}
  ]
}
```

`week_of` is the Monday. Short sentences, the owner's own words. Priorities are
what makes it a log rather than a diary: see `weekly-review.md`.

## agents.json

```json
{
  "rework_threshold": 0.25,
  "agents": [
    {"name": "Daily post scheduler", "status": "active",
     "responsibilities": ["Pick the day's image post", "Queue it in Buffer"],
     "current_assignment": "Running the August image post sequence",
     "approvals_needed": [
       {"item": "Twelve hooks ready for review", "requested": "2026-08-22",
        "urgency": "medium"}],
     "quality": {"rating": 4.7, "scale": 5, "reviews": 24, "rework_rate": 0.08},
     "time_saved_hours_week": 4,
     "activity": [{"date": "2026-08-26", "summary": "Queued post 24",
                   "outcome": "Published"}]}
  ]
}
```

| Field | Notes |
|---|---|
| `status` | `active`, `paused`, `retired`. Only active agents count towards hours saved. |
| `approvals_needed[].urgency` | `high`, `medium`, `low`. High, or anything waiting over a week, is flagged. |
| `quality.rating` | Your own review of the output, not the agent's opinion of itself. |
| `quality.reviews` | How many outputs you actually looked at. Under 5 the rework flag stays quiet. |
| `quality.rework_rate` | Share of outputs you had to redo. This is the number that tells you whether the hours saved are real. |
| `time_saved_hours_week` | An honest estimate. It is the only figure here that justifies keeping the agent. |
| `activity` | Recent runs. The dashboard shows the four newest. |

In this repository the agents are the automations in `automation/` and the
skills in `.claude/skills/`: the daily post scheduler, the outlier researcher,
the podcast outreach, the infographic renderer.
