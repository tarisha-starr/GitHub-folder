# Every formula and every threshold

The dashboard makes claims about the business. This file is where those claims
are justified. It matches `scripts/command_center.py`; if you change one,
change the other in the same commit.

Two kinds of threshold. The ones that vary by business live in the data files,
so the owner can set them (follow-up days, capacity limits, minimum ad spend).
The ones that are close to universal live at the top of `command_center.py` as
constants. Both are listed below.

## Executive snapshot

| Figure | How it is worked out |
|---|---|
| Revenue, expenses, cash collected, recurring revenue | Straight from the latest row in `finance.json`. The latest row is the highest `month` value, not the last one in the file. |
| Profit | Revenue minus expenses. This is cash profit for the month, not accounting profit: no depreciation, no accruals. |
| Margin | Profit divided by revenue. |
| Collection gap | Revenue minus cash collected, and that gap as a share of revenue. Money invoiced that has not arrived. |
| Recurring share | Recurring revenue divided by revenue. How much of the month would repeat if nothing new sold. |
| Monthly burn | Mean expenses over the last three months. |
| Runway | Cash on hand divided by monthly burn. |
| Growth | Mean revenue over the last three months against the mean of the three before. Expenses the same way. Three months smooths a single big launch. |

### The forecast

    forecast = recurring revenue this month
             + weighted pipeline expected to close next month
             + committed future revenue booked for next month

Weighted pipeline is each open lead's value times the weight of its stage, from
`stage_weights` in `leads.json`, counted in the month of its `expected_close`.

This forecast is deliberately conservative. It counts only money that already
has a name attached: subscriptions that renew, deals already in the pipeline,
and work already paid for. It cannot see leads that have not arrived yet, so in
a business that sells inside the month it will read low. That is the right
error to make in a forecast an owner uses to decide whether to spend.

### Flags

| Flag | Fires when | Severity |
|---|---|---|
| Uncollected revenue | Collection gap is above 10 percent of revenue | high |
| Short runway | Runway is under 3 months | high |
| Loss-making month | Expenses exceed revenue | high |
| Expenses outrunning revenue | Three-month expense growth is more than 5 points above revenue growth | medium |

## Offer scorecard

Only rows for the newest `period` in `offers.json` are scored.

| Figure | How it is worked out |
|---|---|
| Gross | `price` times `units_sold` |
| Revenue | Gross minus refunds |
| Conversion | `units_sold` divided by `opportunities`. An opportunity is anyone who could have bought: a call held, an application, a checkout started. |
| Contribution | Revenue minus `delivery_cost`. What the offer leaves behind after being delivered, before overheads. |
| Margin | Contribution divided by revenue |
| Share of profit | This offer's contribution as a share of total contribution. It is what tells you which offer is actually carrying the business. |

For a subscription, put the monthly price in `price` and active members in
`units_sold`, and say so in `notes`. The scorecard then reads as monthly.

| Flag | Fires when | Severity |
|---|---|---|
| Thin margin | Margin under 40 percent | medium, or high under 25 percent |
| Weak satisfaction | Score under 80 percent of the scale, with at least 3 responses | medium |
| Refund rate | Refunds above 3 percent of gross | medium |

The three-response minimum stops one bad week from condemning an offer.

## Lead pipeline

| Figure | How it is worked out |
|---|---|
| Open leads | Any lead whose stage is not `won` or `lost` |
| Weighted value | Value times the stage weight from `stage_weights` |
| Win rate | Won divided by won plus lost, across every lead in the file |
| Gone quiet | Days since `last_touch` is greater than `follow_up_days` (default 7), open leads only |
| By source | Open value and weighted value per source, plus won and lost counts |

Default stage weights are 10, 25, 50, 75 percent. They are a starting point,
not a truth. Once there are fifty closed leads, replace them with the actual
close rate per stage and the forecast stops lying.

| Flag | Fires when | Severity |
|---|---|---|
| Quiet leads | Any open lead past `follow_up_days` | medium, or high at 3 or more |
| Past expected close | Open leads whose `expected_close` has passed | medium |

## Marketing performance

Scored for the newest `period` in `marketing.json`, compared against the period
before it where the same channel and campaign appear in both.

| Figure | How it is worked out |
|---|---|
| Cost per lead | `spend` divided by `leads` |
| Cost per client | `spend` divided by `customers` |
| Return on spend | `revenue` divided by `spend` |
| Lead to client | `customers` divided by `leads` |

Organic channels with zero spend show no cost per lead, which is honest: the
cost is time, and the dashboard does not price time. They still show leads,
clients and revenue, so they can be compared on output.

Channels below `min_spend_for_ranking` are listed but never ranked, so one
lucky sale on a tiny budget cannot top the table.

| Flag | Fires when | Severity |
|---|---|---|
| Losing channel | Return under 1.0, on a channel above the ranking floor | high |
| Rising cost per lead | Cost per lead up more than 50 percent on the prior period | medium |

Return counts revenue as attributed in the file. Attribution is a judgement,
not a measurement, so the flag is a prompt to look, not a verdict.

## Client health

| Figure | How it is worked out |
|---|---|
| Paying clients | Status `active`, `renewing` or `at_risk` |
| Value on the books | The sum of their `value` |
| Renewals | Renewal date inside 60 days |
| Cancellations | Status `churned` with `churned_on` inside 30 days. Falls back to `last_engagement` when `churned_on` is missing. |
| Churn rate | Recent cancellations divided by paying clients plus those cancellations |

A client lands on the attention list for any of these reasons, and the reasons
are shown so the owner knows which one:

- Marked `at_risk`
- Onboarding has run longer than `onboarding_days` (default 14)
- No engagement for longer than `quiet_days` (default 21)
- Engagement below 40 out of 100
- Renews within 30 days on engagement below 60

| Flag | Fires when | Severity |
|---|---|---|
| Cancellations | Any in the last 30 days | medium, or high at 2 or more |
| Stuck in onboarding | Any client past `onboarding_days` | high |
| Shaky renewals | Renewal inside 30 days on engagement under 60 | medium |

Onboarding is treated as the most urgent because a client who has paid and
never started is the one who asks for a refund.

## Team capacity

| Figure | How it is worked out |
|---|---|
| Utilisation | `committed_hours` divided by `capacity_hours` |
| Overloaded | Utilisation above `overload_threshold` (default 0.9) |
| Spare | Utilisation below `idle_threshold` (default 0.6) |
| Available capacity | Capacity minus committed, per person and in total |

Capacity is hours actually available for this business, not hours in a week.
For the owner that usually means far less than 40.

| Flag | Fires when | Severity |
|---|---|---|
| Over capacity | Anyone above the overload threshold | medium |
| Blockers | Any blocker logged | medium |
| Deadlines | Any deadline overdue or marked `at_risk` | high if overdue, otherwise medium |

## Decision log

| Figure | How it is worked out |
|---|---|
| Due for review | `review_date` has passed and status is not `closed` |
| Hit rate | Decisions with verdict `worked` divided by all decisions carrying a verdict |

| Flag | Fires when | Severity |
|---|---|---|
| Failed and still running | Verdict `did_not_work` while status is not `closed` | high |
| Review overdue | Past `review_date`, not closed | medium |

The first of those is the one that earns the panel its place. A decision that
has already been judged a failure and is still running is money leaving on a
schedule.

## Weekly patterns

Wins, concerns, surprises and priorities are written by hand. The dashboard
adds a short list of what the numbers say about the same week: the revenue
move, the recurring revenue move, which offer carried the profit, the open
pipeline, how many clients need attention, how many agent outputs are waiting.
Comparing the two lists is the exercise.

One flag, low severity: a week logged without priorities. The log is meant to
end in decisions, not observations.

## Agent HQ

| Figure | How it is worked out |
|---|---|
| Hours saved | The sum of `time_saved_hours_week` across active agents. Owner estimate. |
| Output quality | Mean rating across agents, weighted by how many outputs were reviewed |
| Rework rate | Per agent, the share of outputs that had to be redone |
| Approvals | Every item in `approvals_needed`, sorted by urgency then by how long it has waited |

| Flag | Fires when | Severity |
|---|---|---|
| Approvals waiting | Anything marked high urgency, or anything waiting over 7 days | high if urgent, otherwise medium |
| Rework too high | Rework above `rework_threshold` (default 0.25) with at least 5 reviews | medium |

An agent needing a quarter of its work redone is not saving the hours it
claims. The five-review minimum keeps a new agent from being condemned on its
first day.

## How flags are ordered

High before medium before low, otherwise in the order the panels are computed.
There is no scoring model behind it. A flag is a threshold crossed, nothing
more, and the wording says which threshold and by how much so the owner can
disagree with it.

## Data warnings

Separate from flags, and shown at the top of the page:

- A missing or unparseable file, named, with that panel left empty
- Finance data that stops more than one month back
- A weekly log whose newest entry is more than 14 days old

A stale dashboard that says so is useful. A stale dashboard that looks current
is worse than none.
