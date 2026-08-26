"""Read the Command Center data files and work out what they mean.

Pure standard library. `build_report(data_dir, as_of)` returns one dict with a
section per panel of the dashboard, plus a list of flags: the things that
deserve attention, sorted worst first. `render_dashboard.py` turns that into
HTML, but the report is plain data, so anything else can use it too.

Every rule and threshold here is written up in ../references/metrics.md. When
you change a formula, change that file in the same commit, otherwise the
dashboard starts telling the owner things nobody can explain.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

FILES = [
    "finance", "offers", "leads", "marketing", "clients",
    "team", "decisions", "patterns", "agents",
]

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# Thresholds that are not per-business enough to live in the data files.
MARGIN_FLOOR = 0.40          # gross margin below this on an offer is a leak
SATISFACTION_FLOOR = 0.80    # share of the scale, so 4.0 out of 5
COLLECTION_GAP_LIMIT = 0.10  # invoiced but uncollected, share of revenue
REFUND_LIMIT = 0.03          # refunds as a share of gross revenue
CPL_RISE_LIMIT = 0.50        # cost per lead up this much on the prior period
RENEWAL_HORIZON = 30         # days ahead we count a renewal as imminent
LOW_ENGAGEMENT = 40          # out of 100
RUNWAY_FLOOR = 3.0           # months of cash


# --------------------------------------------------------------------- utils

def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _month_key(value):
    """Accept 2026-08 or 2026-08-01 and return 2026-08."""
    return str(value)[:7] if value else ""


def _next_month(month_key):
    year, month = int(month_key[:4]), int(month_key[5:7])
    return f"{year + 1}-01" if month == 12 else f"{year}-{month + 1:02d}"


def _month_label(month_key):
    try:
        return datetime.strptime(month_key, "%Y-%m").strftime("%B %Y")
    except ValueError:
        return month_key


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ratio(top, bottom):
    """Divide, or return None when the denominator makes the answer meaningless."""
    bottom = _num(bottom)
    return _num(top) / bottom if bottom else None


def _change(current, previous):
    previous = _num(previous)
    return (_num(current) - previous) / abs(previous) if previous else None


def _days_since(value, as_of):
    parsed = _parse_date(value)
    return (as_of - parsed).days if parsed else None


def _named(rows, key="name"):
    """Drop the placeholder rows the templates ship with."""
    return [row for row in rows if str(row.get(key, "") or "").strip()]


def _clean(payload):
    """Drop the _help and _note keys the templates carry."""
    if isinstance(payload, dict):
        return {k: v for k, v in payload.items() if not k.startswith("_")}
    return payload


def load_data(data_dir):
    """Load the nine files. Missing or broken ones become warnings, not crashes.

    A `_note` in any file is carried through to the top of the page. That is how
    a caveat that applies to the whole panel, "figures exclude GST", or "example
    data, none of it real", reaches the person reading the dashboard.
    """
    data_dir = Path(data_dir)
    data, warnings, notes = {}, [], []
    for name in FILES:
        path = data_dir / f"{name}.json"
        if not path.exists():
            data[name] = {}
            warnings.append(f"{name}.json is missing, so that panel is empty.")
            continue
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            data[name] = {}
            warnings.append(f"{name}.json is not valid JSON ({exc.msg}, line {exc.lineno}).")
            continue
        data[name] = _clean(payload)
        note = payload.get("_note") if isinstance(payload, dict) else None
        if note and note not in notes:
            notes.append(str(note))
    return data, warnings, notes


class Flags:
    """Collects what deserves attention, worst first."""

    def __init__(self):
        self.items = []

    def add(self, severity, section, title, detail=""):
        self.items.append({
            "severity": severity, "section": section,
            "title": title, "detail": detail,
        })

    def sorted(self):
        return sorted(self.items, key=lambda f: SEVERITY_ORDER.get(f["severity"], 3))


# ------------------------------------------------------------------ sections

def _executive_snapshot(finance, pipeline, flags):
    months = [m for m in finance.get("months", []) if _month_key(m.get("month"))]
    months.sort(key=lambda m: _month_key(m.get("month")))
    if not months:
        return {"empty": True, "history": []}

    current, previous = months[-1], months[-2] if len(months) > 1 else None
    month_key = _month_key(current.get("month"))
    revenue = _num(current.get("revenue"))
    expenses = _num(current.get("expenses"))
    collected = _num(current.get("cash_collected"))
    mrr = _num(current.get("recurring_revenue"))
    profit = revenue - expenses

    trailing = months[-3:]
    prior = months[-6:-3]
    avg = lambda rows, key: sum(_num(r.get(key)) for r in rows) / len(rows) if rows else 0.0

    forecast_month = _next_month(month_key)
    committed = sum(
        _num(row.get("amount")) for row in finance.get("committed_future_revenue", [])
        if _month_key(row.get("month")) == forecast_month
    )
    pipeline_next = pipeline.get("weighted_by_month", {}).get(forecast_month, 0.0)

    burn = avg(trailing, "expenses")
    cash_on_hand = _num(finance.get("cash_on_hand"))
    runway = _ratio(cash_on_hand, burn)

    gap = revenue - collected
    gap_share = _ratio(gap, revenue)
    if gap_share is not None and gap_share > COLLECTION_GAP_LIMIT:
        flags.add("high", "Executive snapshot",
                  f"{_pct(gap_share)} of {_month_label(month_key)} revenue is still uncollected",
                  "Invoiced but not in the bank. Chase it before it ages.")
    if runway is not None and runway < RUNWAY_FLOOR:
        flags.add("high", "Executive snapshot",
                  f"Cash covers {runway:.1f} months at the current burn",
                  "Below three months of cover.")
    if profit < 0:
        flags.add("high", "Executive snapshot",
                  f"{_month_label(month_key)} ran at a loss",
                  "Expenses came in above revenue.")

    revenue_growth = _change(avg(trailing, "revenue"), avg(prior, "revenue"))
    expense_growth = _change(avg(trailing, "expenses"), avg(prior, "expenses"))
    if (revenue_growth is not None and expense_growth is not None
            and expense_growth > revenue_growth + 0.05):
        flags.add("medium", "Executive snapshot",
                  "Expenses are growing faster than revenue",
                  f"Last three months: revenue {_pct(revenue_growth, signed=True)}, "
                  f"expenses {_pct(expense_growth, signed=True)} against the three before.")

    return {
        "empty": False,
        "month": month_key,
        "month_label": _month_label(month_key),
        "forecast_month": forecast_month,
        "forecast_month_label": _month_label(forecast_month),
        "revenue": revenue,
        "revenue_change": _change(revenue, previous.get("revenue")) if previous else None,
        "expenses": expenses,
        "expense_change": _change(expenses, previous.get("expenses")) if previous else None,
        "profit": profit,
        "margin": _ratio(profit, revenue),
        "cash_collected": collected,
        "collection_gap": gap,
        "collection_gap_share": gap_share,
        "mrr": mrr,
        "mrr_share": _ratio(mrr, revenue),
        "mrr_change": _change(mrr, previous.get("recurring_revenue")) if previous else None,
        "new_customers": _num(current.get("new_customers")),
        "cash_on_hand": cash_on_hand,
        "runway_months": runway,
        "monthly_burn": burn,
        "forecast": mrr + pipeline_next + committed,
        "forecast_parts": {
            "recurring": mrr, "pipeline": pipeline_next, "committed": committed,
        },
        "revenue_growth": revenue_growth,
        "expense_growth": expense_growth,
        "history": [
            {"month": _month_key(m.get("month")),
             "label": _month_label(_month_key(m.get("month"))),
             "revenue": _num(m.get("revenue")),
             "expenses": _num(m.get("expenses")),
             "profit": _num(m.get("revenue")) - _num(m.get("expenses")),
             "recurring_revenue": _num(m.get("recurring_revenue"))}
            for m in months
        ],
    }


def _offer_scorecard(offers_file, flags):
    rows = _named(offers_file.get("offers", []))
    if not rows:
        return {"empty": True, "offers": [], "period": ""}

    period = max((_month_key(r.get("period")) for r in rows if r.get("period")), default="")
    scored = []
    for row in rows:
        if period and _month_key(row.get("period")) != period:
            continue
        units = _num(row.get("units_sold"))
        gross = _num(row.get("price")) * units
        refunds = _num(row.get("refunds"))
        revenue = gross - refunds
        delivery = _num(row.get("delivery_cost"))
        contribution = revenue - delivery
        satisfaction = row.get("satisfaction") or {}
        scale = _num(satisfaction.get("scale"), 5) or 5
        score = _num(satisfaction.get("avg_score"))
        scored.append({
            "name": row.get("name", "Unnamed offer"),
            "price": _num(row.get("price")),
            "opportunities": _num(row.get("opportunities")),
            "units_sold": units,
            "conversion": _ratio(units, row.get("opportunities")),
            "revenue": revenue,
            "refunds": refunds,
            "refund_share": _ratio(refunds, gross),
            "delivery_cost": delivery,
            "contribution": contribution,
            "margin": _ratio(contribution, revenue),
            "per_unit_profit": _ratio(contribution, units),
            "satisfaction": score,
            "satisfaction_scale": scale,
            "satisfaction_share": _ratio(score, scale),
            "responses": int(_num(satisfaction.get("responses"))),
            "notes": row.get("notes", ""),
        })

    scored.sort(key=lambda o: o["contribution"], reverse=True)
    total_contribution = sum(o["contribution"] for o in scored)
    for offer in scored:
        offer["contribution_share"] = _ratio(offer["contribution"], total_contribution)
        if offer["margin"] is not None and offer["margin"] < MARGIN_FLOOR:
            flags.add("high" if offer["margin"] < 0.25 else "medium", "Offer scorecard",
                      f"{offer['name']} keeps {_pct(offer['margin'])} of what it sells",
                      f"{_money_plain(offer['revenue'])} sold, {_money_plain(offer['delivery_cost'])} "
                      "to deliver. Either the price or the delivery has to move.")
        if (offer["satisfaction_share"] is not None and offer["responses"] >= 3
                and offer["satisfaction_share"] < SATISFACTION_FLOOR):
            flags.add("medium", "Offer scorecard",
                      f"{offer['name']} is rated {offer['satisfaction']:g} out of "
                      f"{offer['satisfaction_scale']:g}",
                      f"Across {offer['responses']} responses.")
        if offer["refund_share"] is not None and offer["refund_share"] > REFUND_LIMIT:
            flags.add("medium", "Offer scorecard",
                      f"{offer['name']} refunded {_pct(offer['refund_share'])} of sales",
                      "Refunds usually mean the sale promised something delivery did not.")

    return {
        "empty": False,
        "period": period,
        "period_label": _month_label(period),
        "offers": scored,
        "total_revenue": sum(o["revenue"] for o in scored),
        "total_contribution": total_contribution,
    }


def _lead_pipeline(leads_file, as_of, flags):
    leads = _named(leads_file.get("leads", []))
    weights = leads_file.get("stage_weights") or {
        "new": 0.1, "qualified": 0.25, "proposal": 0.5,
        "negotiation": 0.75, "won": 1.0, "lost": 0.0,
    }
    follow_up_days = int(_num(leads_file.get("follow_up_days"), 7))
    if not leads:
        return {"empty": True, "weighted_by_month": {}, "leads": []}

    enriched, weighted_by_month = [], {}
    for lead in leads:
        stage = str(lead.get("stage", "new")).lower()
        value = _num(lead.get("value"))
        weight = _num(weights.get(stage), 0.0)
        silent = _days_since(lead.get("last_touch"), as_of)
        expected = _parse_date(lead.get("expected_close"))
        open_lead = stage not in ("won", "lost")
        overdue = bool(open_lead and silent is not None and silent > follow_up_days)
        enriched.append({
            "name": lead.get("name", "Unnamed"),
            "source": lead.get("source", "Unknown"),
            "offer": lead.get("offer", ""),
            "stage": stage,
            "value": value,
            "weighted": value * weight,
            "expected_close": expected,
            "days_to_close": (expected - as_of).days if expected else None,
            "last_touch": _parse_date(lead.get("last_touch")),
            "days_silent": silent,
            "owner": lead.get("owner", ""),
            "next_step": lead.get("next_step", ""),
            "open": open_lead,
            "overdue": overdue,
        })
        if open_lead and expected:
            key = expected.strftime("%Y-%m")
            weighted_by_month[key] = weighted_by_month.get(key, 0.0) + value * weight

    open_leads = [lead for lead in enriched if lead["open"]]
    by_stage = {}
    for stage in weights:
        rows = [lead for lead in enriched if lead["stage"] == stage]
        if stage in ("won", "lost") or rows:
            by_stage[stage] = {
                "count": len(rows),
                "value": sum(r["value"] for r in rows),
                "weighted": sum(r["weighted"] for r in rows),
            }

    by_source = {}
    for lead in enriched:
        entry = by_source.setdefault(
            lead["source"], {"count": 0, "value": 0.0, "weighted": 0.0, "won": 0, "lost": 0})
        entry["count"] += 1
        if lead["open"]:
            entry["value"] += lead["value"]
            entry["weighted"] += lead["weighted"]
        elif lead["stage"] == "won":
            entry["won"] += 1
        elif lead["stage"] == "lost":
            entry["lost"] += 1

    overdue = sorted([lead for lead in enriched if lead["overdue"]],
                     key=lambda lead: lead["days_silent"], reverse=True)
    stale_value = sum(lead["value"] for lead in overdue)
    if overdue:
        flags.add("high" if len(overdue) >= 3 else "medium", "Lead pipeline",
                  f"{len(overdue)} {_plural(len(overdue), 'lead has', 'leads have')} gone "
                  f"quiet for more than {follow_up_days} days",
                  f"{_money_plain(stale_value)} of pipeline, longest silence "
                  f"{overdue[0]['days_silent']} days ({overdue[0]['name']}).")

    late = [lead for lead in open_leads
            if lead["days_to_close"] is not None and lead["days_to_close"] < 0]
    if late:
        flags.add("medium", "Lead pipeline",
                  f"{len(late)} {_plural(len(late), 'deal is', 'deals are')} past "
                  "the expected close date",
                  "Either they moved, or the forecast is carrying deals that will not land.")

    won = by_stage.get("won", {}).get("count", 0)
    lost = by_stage.get("lost", {}).get("count", 0)

    return {
        "empty": False,
        "leads": sorted(enriched, key=lambda lead: (not lead["open"], -lead["weighted"])),
        "open_count": len(open_leads),
        "open_value": sum(lead["value"] for lead in open_leads),
        "weighted_value": sum(lead["weighted"] for lead in open_leads),
        "by_stage": by_stage,
        "by_source": dict(sorted(by_source.items(), key=lambda kv: kv[1]["weighted"], reverse=True)),
        "weighted_by_month": weighted_by_month,
        "overdue": overdue,
        "stale_value": stale_value,
        "follow_up_days": follow_up_days,
        "win_rate": _ratio(won, won + lost),
        "won": won,
        "lost": lost,
        "stage_weights": weights,
    }


def _marketing(marketing_file, flags):
    campaigns = _named(marketing_file.get("campaigns", []))
    if not campaigns:
        return {"empty": True, "campaigns": []}

    min_spend = _num(marketing_file.get("min_spend_for_ranking"), 200)
    period = max((_month_key(c.get("period")) for c in campaigns if c.get("period")), default="")
    prior_period = None
    earlier = sorted({_month_key(c.get("period")) for c in campaigns if c.get("period")})
    if len(earlier) > 1:
        prior_period = earlier[-2]

    def score(rows):
        out = []
        for row in rows:
            spend, leads = _num(row.get("spend")), _num(row.get("leads"))
            customers, revenue = _num(row.get("customers")), _num(row.get("revenue"))
            out.append({
                "name": row.get("name", "Unnamed"),
                "channel": row.get("channel", "Unknown"),
                "spend": spend,
                "leads": leads,
                "customers": customers,
                "revenue": revenue,
                "cpl": _ratio(spend, leads),
                "cac": _ratio(spend, customers),
                "roas": _ratio(revenue, spend),
                "lead_to_client": _ratio(customers, leads),
                "notes": row.get("notes", ""),
                "ranked": spend >= min_spend,
            })
        return out

    current = score([c for c in campaigns if _month_key(c.get("period")) == period])
    previous = score([c for c in campaigns if _month_key(c.get("period")) == prior_period]) \
        if prior_period else []
    prior_cpl = {(row["channel"], row["name"]): row["cpl"] for row in previous}

    for row in current:
        row["prior_cpl"] = prior_cpl.get((row["channel"], row["name"]))
        row["cpl_change"] = _change(row["cpl"], row["prior_cpl"]) \
            if row["cpl"] is not None and row["prior_cpl"] else None
        if row["ranked"] and row["roas"] is not None and row["roas"] < 1:
            flags.add("high", "Marketing performance",
                      f"{row['channel']} returned {row['roas']:.2f} for every dollar spent",
                      f"{_money_plain(row['spend'])} spent, {_money_plain(row['revenue'])} back. "
                      "Fix it or stop it.")
        elif row["cpl_change"] is not None and row["cpl_change"] > CPL_RISE_LIMIT:
            flags.add("medium", "Marketing performance",
                      f"{row['channel']} cost per lead is up {_pct(row['cpl_change'], signed=True)}",
                      f"From {_money_plain(row['prior_cpl'])} to {_money_plain(row['cpl'])}.")

    ranked = sorted([r for r in current if r["ranked"] and r["roas"] is not None],
                    key=lambda r: r["roas"], reverse=True)
    spend = sum(r["spend"] for r in current)
    leads = sum(r["leads"] for r in current)
    customers = sum(r["customers"] for r in current)
    revenue = sum(r["revenue"] for r in current)

    return {
        "empty": False,
        "period": period,
        "period_label": _month_label(period),
        "prior_period_label": _month_label(prior_period) if prior_period else "",
        "campaigns": sorted(current, key=lambda r: r["revenue"], reverse=True),
        "ranked": ranked,
        "unranked": [r for r in current if not r["ranked"]],
        "min_spend": min_spend,
        "totals": {
            "spend": spend, "leads": leads, "customers": customers, "revenue": revenue,
            "cpl": _ratio(spend, leads), "cac": _ratio(spend, customers),
            "roas": _ratio(revenue, spend), "lead_to_client": _ratio(customers, leads),
        },
    }


def _client_health(clients_file, as_of, flags):
    clients = _named(clients_file.get("clients", []))
    if not clients:
        return {"empty": True, "clients": [], "needs_attention": []}

    onboarding_days = int(_num(clients_file.get("onboarding_days"), 14))
    quiet_days = int(_num(clients_file.get("quiet_days"), 21))

    enriched, needs_attention = [], []
    for client in clients:
        status = str(client.get("status", "active")).lower()
        renewal = _parse_date(client.get("renewal_date"))
        quiet_for = _days_since(client.get("last_engagement"), as_of)
        age = _days_since(client.get("start_date"), as_of)
        churned_on = _parse_date(client.get("churned_on")) or _parse_date(
            client.get("last_engagement"))
        engagement = _num(client.get("engagement"))
        row = {
            "name": client.get("name", "Unnamed"),
            "offer": client.get("offer", ""),
            "status": status,
            "value": _num(client.get("value")),
            "start_date": _parse_date(client.get("start_date")),
            "days_since_start": age,
            "renewal_date": renewal,
            "days_to_renewal": (renewal - as_of).days if renewal else None,
            "last_engagement": _parse_date(client.get("last_engagement")),
            "days_quiet": quiet_for,
            "churned_on": churned_on if status == "churned" else None,
            "engagement": engagement,
            "owner": client.get("owner", ""),
            "notes": client.get("notes", ""),
            "reasons": [],
        }

        if status == "at_risk":
            row["reasons"].append("Marked at risk")
        if status == "onboarding" and age is not None and age > onboarding_days:
            row["reasons"].append(f"Onboarding has run {age} days")
        if status in ("active", "renewing", "at_risk") and quiet_for is not None \
                and quiet_for > quiet_days:
            row["reasons"].append(f"No engagement for {quiet_for} days")
        if status in ("active", "renewing", "at_risk") and engagement < LOW_ENGAGEMENT:
            row["reasons"].append(f"Engagement at {engagement:g} out of 100")
        if row["days_to_renewal"] is not None and 0 <= row["days_to_renewal"] <= RENEWAL_HORIZON \
                and engagement < 60 and status != "churned":
            row["reasons"].append(f"Renews in {row['days_to_renewal']} days on a low signal")

        enriched.append(row)
        if row["reasons"] and status != "churned":
            needs_attention.append(row)

    by_status = {}
    for row in enriched:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1

    paying = [r for r in enriched if r["status"] in ("active", "renewing", "at_risk")]
    churned_recent = [r for r in enriched if r["status"] == "churned"
                      and r["churned_on"] is not None
                      and (as_of - r["churned_on"]).days <= 30]
    renewals = sorted(
        [r for r in enriched if r["days_to_renewal"] is not None
         and 0 <= r["days_to_renewal"] <= 60 and r["status"] != "churned"],
        key=lambda r: r["days_to_renewal"])

    churn_rate = _ratio(len(churned_recent), len(paying) + len(churned_recent))
    if churned_recent:
        flags.add("high" if len(churned_recent) >= 2 else "medium", "Client health",
                  f"{len(churned_recent)} "
                  f"{_plural(len(churned_recent), 'cancellation')} in the last 30 days",
                  f"{_money_plain(sum(r['value'] for r in churned_recent))} of monthly value gone.")

    stalled = [r for r in needs_attention if any("Onboarding has run" in x for x in r["reasons"])]
    if stalled:
        flags.add("high", "Client health",
                  f"{len(stalled)} {_plural(len(stalled), 'client is', 'clients are')} "
                  "stuck in onboarding",
                  "They have paid and have not started. This is where refunds come from.")

    at_risk_renewals = [r for r in renewals if r["days_to_renewal"] <= RENEWAL_HORIZON
                        and r["engagement"] < 60]
    if at_risk_renewals:
        flags.add("medium", "Client health",
                  f"{len(at_risk_renewals)} "
                  f"{_plural(len(at_risk_renewals), 'renewal', 'renewals')} inside "
                  f"{RENEWAL_HORIZON} days {_plural(len(at_risk_renewals), 'looks', 'look')} shaky",
                  f"{_money_plain(sum(r['value'] for r in at_risk_renewals))} of value, "
                  "all on low engagement.")

    needs_attention.sort(key=lambda r: (-len(r["reasons"]), r["engagement"]))

    return {
        "empty": False,
        "clients": enriched,
        "by_status": by_status,
        "paying_count": len(paying),
        "paying_value": sum(r["value"] for r in paying),
        "needs_attention": needs_attention,
        "renewals": renewals,
        "renewal_value": sum(r["value"] for r in renewals),
        "churned_recent": churned_recent,
        "churn_rate": churn_rate,
        "onboarding_days": onboarding_days,
        "quiet_days": quiet_days,
    }


def _team_capacity(team_file, as_of, flags):
    people = _named(team_file.get("people", []))
    if not people:
        return {"empty": True, "people": []}

    overload = _num(team_file.get("overload_threshold"), 0.9)
    idle = _num(team_file.get("idle_threshold"), 0.6)

    enriched = []
    for person in people:
        capacity = _num(person.get("capacity_hours"))
        committed = _num(person.get("committed_hours"))
        deadlines = []
        for deadline in _named(person.get("deadlines", []), "item"):
            due = _parse_date(deadline.get("due"))
            status = str(deadline.get("status", "on_track")).lower()
            deadlines.append({
                "item": deadline.get("item", ""),
                "due": due,
                "days_left": (due - as_of).days if due else None,
                "status": status,
                "overdue": bool(due and due < as_of and status != "done"),
            })
        blockers = [b for b in person.get("blockers", []) if b.get("item")]
        utilisation = _ratio(committed, capacity)
        enriched.append({
            "name": person.get("name", "Unnamed"),
            "role": person.get("role", ""),
            "capacity_hours": capacity,
            "committed_hours": committed,
            "spare_hours": capacity - committed,
            "utilisation": utilisation,
            "state": ("overloaded" if utilisation is not None and utilisation > overload
                      else "spare" if utilisation is not None and utilisation < idle
                      else "steady"),
            "responsibilities": person.get("responsibilities", []),
            "deadlines": sorted(deadlines, key=lambda d: (d["days_left"] is None, d["days_left"])),
            "blockers": blockers,
        })

    overloaded = [p for p in enriched if p["state"] == "overloaded"]
    if overloaded:
        flags.add("medium", "Team capacity",
                  f"{', '.join(p['name'] for p in overloaded)} "
                  f"{'is' if len(overloaded) == 1 else 'are'} over capacity",
                  "Committed hours exceed available hours, so something will slip.")

    blocked = [(p, b) for p in enriched for b in p["blockers"]]
    if blocked:
        flags.add("medium", "Team capacity",
                  f"{len(blocked)} {_plural(len(blocked), 'blocker is', 'blockers are')} "
                  "waiting on someone",
                  "; ".join(f"{p['name']}: {b['item']}" for p, b in blocked[:3]))

    at_risk = [(p, d) for p in enriched for d in p["deadlines"]
               if d["overdue"] or d["status"] == "at_risk"]
    if at_risk:
        overdue = [pair for pair in at_risk if pair[1]["overdue"]]
        flags.add("high" if overdue else "medium", "Team capacity",
                  f"{len(at_risk)} {_plural(len(at_risk), 'deadline is', 'deadlines are')} "
                  "at risk or already past",
                  "; ".join(f"{d['item']} ({p['name']})" for p, d in at_risk[:3]))

    capacity = sum(p["capacity_hours"] for p in enriched)
    committed = sum(p["committed_hours"] for p in enriched)

    return {
        "empty": False,
        "people": sorted(enriched, key=lambda p: p["utilisation"] or 0, reverse=True),
        "total_capacity": capacity,
        "total_committed": committed,
        "total_spare": capacity - committed,
        "utilisation": _ratio(committed, capacity),
        "blocked": blocked,
        "at_risk_deadlines": at_risk,
        "overload_threshold": overload,
        "idle_threshold": idle,
    }


def _decision_log(decisions_file, as_of, flags):
    decisions = _named(decisions_file.get("decisions", []), "decision")
    if not decisions:
        return {"empty": True, "decisions": []}

    enriched = []
    for decision in decisions:
        review = _parse_date(decision.get("review_date"))
        status = str(decision.get("status", "open")).lower()
        enriched.append({
            "date": _parse_date(decision.get("date")),
            "decision": decision.get("decision", ""),
            "owner": decision.get("owner", ""),
            "supporting_data": decision.get("supporting_data", ""),
            "expected_outcome": decision.get("expected_outcome", ""),
            "review_date": review,
            "status": status,
            "result": decision.get("result", ""),
            "verdict": (decision.get("verdict") or "").lower() or None,
            "due_for_review": bool(review and review <= as_of and status != "closed"),
        })

    due = [d for d in enriched if d["due_for_review"]]
    if due:
        flags.add("medium", "Decision log",
                  f"{len(due)} "
                  f"{_plural(len(due), 'decision is past its', 'decisions are past their')} "
                  "review date",
                  "; ".join(d["decision"] for d in due[:3]))

    failed = [d for d in enriched if d["verdict"] == "did_not_work" and d["status"] != "closed"]
    if failed:
        flags.add("high", "Decision log",
                  f"{len(failed)} {_plural(len(failed), 'decision', 'decisions')} did "
                  "not work and are still running",
                  "; ".join(d["decision"] for d in failed[:3]))

    judged = [d for d in enriched if d["verdict"]]
    worked = [d for d in judged if d["verdict"] == "worked"]

    return {
        "empty": False,
        "decisions": sorted(enriched, key=lambda d: (d["date"] is None, d["date"]), reverse=True),
        "due_for_review": due,
        "open_count": len([d for d in enriched if d["status"] == "open"]),
        "reviewing_count": len([d for d in enriched if d["status"] == "reviewing"]),
        "closed_count": len([d for d in enriched if d["status"] == "closed"]),
        "judged_count": len(judged),
        "hit_rate": _ratio(len(worked), len(judged)),
    }


def _weekly_patterns(patterns_file, snapshot, offers, pipeline, clients, agents, flags):
    weeks = sorted(patterns_file.get("weeks", []),
                   key=lambda w: str(w.get("week_of", "")))
    latest = weeks[-1] if weeks else {}

    observed = []
    if not snapshot.get("empty"):
        if snapshot["revenue_change"] is not None:
            direction = "up" if snapshot["revenue_change"] >= 0 else "down"
            observed.append(f"Revenue {direction} {_pct(abs(snapshot['revenue_change']))} "
                            f"on the previous month.")
        if snapshot["mrr_change"] is not None and snapshot["mrr_change"] > 0:
            observed.append(f"Recurring revenue up {_pct(snapshot['mrr_change'])}, now "
                            f"{_pct(snapshot['mrr_share'])} of the month.")
    if not offers.get("empty") and offers["offers"]:
        best = offers["offers"][0]
        observed.append(f"{best['name']} carried "
                        f"{_pct(best['contribution_share'])} of the profit contribution.")
    if not pipeline.get("empty"):
        observed.append(f"{pipeline['open_count']} open leads worth "
                        f"{_money_plain(pipeline['weighted_value'])} weighted.")
    if not clients.get("empty") and clients["needs_attention"]:
        observed.append(f"{len(clients['needs_attention'])} clients need attention this week.")
    if not agents.get("empty") and agents["approvals"]:
        observed.append(f"{len(agents['approvals'])} agent outputs are waiting on you.")

    if weeks and not latest.get("priorities"):
        flags.add("low", "Weekly patterns",
                  "Last week closed without priorities set",
                  "The log records what happened but not what you decided to do about it.")

    return {
        "empty": not weeks,
        "weeks": list(reversed(weeks)),
        "latest": latest,
        "observed": observed,
    }


def _agent_hq(agents_file, as_of, flags):
    agents = _named(agents_file.get("agents", []))
    if not agents:
        return {"empty": True, "agents": [], "approvals": []}

    rework_threshold = _num(agents_file.get("rework_threshold"), 0.25)
    urgency_order = {"high": 0, "medium": 1, "low": 2}

    enriched, approvals = [], []
    for agent in agents:
        quality = agent.get("quality") or {}
        scale = _num(quality.get("scale"), 5) or 5
        pending = []
        for item in agent.get("approvals_needed", []):
            if not item.get("item"):
                continue
            waiting = _days_since(item.get("requested"), as_of)
            row = {
                "agent": agent.get("name", "Unnamed agent"),
                "item": item["item"],
                "urgency": str(item.get("urgency", "medium")).lower(),
                "requested": _parse_date(item.get("requested")),
                "days_waiting": waiting,
            }
            pending.append(row)
            approvals.append(row)
        activity = sorted(
            [{"date": _parse_date(a.get("date")), "summary": a.get("summary", ""),
              "outcome": a.get("outcome", "")}
             for a in agent.get("activity", []) if a.get("summary")],
            key=lambda a: (a["date"] is None, a["date"]), reverse=True)
        row = {
            "name": agent.get("name", "Unnamed agent"),
            "status": str(agent.get("status", "active")).lower(),
            "responsibilities": agent.get("responsibilities", []),
            "current_assignment": agent.get("current_assignment", ""),
            "approvals": sorted(pending, key=lambda a: urgency_order.get(a["urgency"], 1)),
            "rating": _num(quality.get("rating")),
            "scale": scale,
            "quality_share": _ratio(quality.get("rating"), scale),
            "reviews": int(_num(quality.get("reviews"))),
            "rework_rate": _num(quality.get("rework_rate")),
            "time_saved_hours_week": _num(agent.get("time_saved_hours_week")),
            "activity": activity,
        }
        enriched.append(row)

        if row["status"] == "active" and row["reviews"] >= 5 \
                and row["rework_rate"] > rework_threshold:
            flags.add("medium", "Agent HQ",
                      f"{row['name']} needs rework on {_pct(row['rework_rate'])} of its output",
                      f"Rated {row['rating']:g} out of {row['scale']:g} across "
                      f"{row['reviews']} reviews. Tighten the brief or narrow the job.")

    approvals.sort(key=lambda a: (urgency_order.get(a["urgency"], 1),
                                  -(a["days_waiting"] or 0)))
    urgent = [a for a in approvals if a["urgency"] == "high"
              or (a["days_waiting"] or 0) > 7]
    if urgent:
        flags.add("high" if any(a["urgency"] == "high" for a in urgent) else "medium",
                  "Agent HQ",
                  f"{len(urgent)} agent {_plural(len(urgent), 'output is', 'outputs are')} "
                  "waiting on your approval",
                  "; ".join(f"{a['agent']}: {a['item']}" for a in urgent[:3]))

    active = [a for a in enriched if a["status"] == "active"]
    rated = [a for a in enriched if a["reviews"] > 0]

    return {
        "empty": False,
        "agents": sorted(enriched, key=lambda a: (a["status"] != "active", a["name"])),
        "active_count": len(active),
        "paused_count": len([a for a in enriched if a["status"] != "active"]),
        "approvals": approvals,
        "hours_saved": sum(a["time_saved_hours_week"] for a in active),
        "avg_quality": (sum(a["rating"] * a["reviews"] for a in rated)
                        / sum(a["reviews"] for a in rated)) if rated else None,
        "quality_scale": rated[0]["scale"] if rated else 5,
        "rework_threshold": rework_threshold,
    }


# ------------------------------------------------------------------ assembly

def build_report(data_dir, as_of=None):
    global _CURRENCY
    as_of = as_of or date.today()
    data, warnings, notes = load_data(data_dir)
    _CURRENCY = data["finance"].get("currency", "")
    flags = Flags()

    pipeline = _lead_pipeline(data["leads"], as_of, flags)
    snapshot = _executive_snapshot(data["finance"], pipeline, flags)
    offers = _offer_scorecard(data["offers"], flags)
    marketing = _marketing(data["marketing"], flags)
    clients = _client_health(data["clients"], as_of, flags)
    team = _team_capacity(data["team"], as_of, flags)
    decisions = _decision_log(data["decisions"], as_of, flags)
    agents = _agent_hq(data["agents"], as_of, flags)
    patterns = _weekly_patterns(data["patterns"], snapshot, offers, pipeline,
                                clients, agents, flags)

    stale = _staleness(data, as_of)
    if stale:
        warnings.append("Data may be out of date: " + "; ".join(stale))

    return {
        "as_of": as_of,
        "currency": data["finance"].get("currency", ""),
        "snapshot": snapshot,
        "offers": offers,
        "pipeline": pipeline,
        "marketing": marketing,
        "clients": clients,
        "team": team,
        "decisions": decisions,
        "patterns": patterns,
        "agents": agents,
        "flags": flags.sorted(),
        "warnings": warnings,
        "notes": notes,
    }


def _staleness(data, as_of):
    """Say so when the newest month or week is well behind today."""
    notes = []
    months = [_month_key(m.get("month")) for m in data["finance"].get("months", [])]
    if months:
        newest = max(months)
        this_month = as_of.strftime("%Y-%m")
        if newest < _previous_month(this_month):
            notes.append(f"finance stops at {_month_label(newest)}")
    weeks = [str(w.get("week_of", "")) for w in data["patterns"].get("weeks", [])]
    weeks = [w for w in weeks if _parse_date(w)]
    if weeks:
        newest_week = _parse_date(max(weeks))
        if (as_of - newest_week) > timedelta(days=14):
            notes.append(f"the weekly log stops at {newest_week.isoformat()}")
    return notes


def _previous_month(month_key):
    year, month = int(month_key[:4]), int(month_key[5:7])
    return f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"


# -------------------------------------------------------------- formatting

_CURRENCY = ""


def _plural(count, singular, plural=None):
    """1 renewal, 2 renewals."""
    return singular if count == 1 else (plural or singular + "s")


def _pct(value, signed=False, places=0):
    if value is None:
        return "n/a"
    text = f"{value * 100:.{places}f}%"
    return f"+{text}" if signed and value > 0 else text


def _money_plain(value, currency=None):
    """Money in the report currency. Cents only when the number has them."""
    if value is None:
        return "n/a"
    currency = _CURRENCY if currency is None else currency
    prefix = f"{currency} " if currency else ""
    sign = "-" if value < 0 else ""
    value = abs(value)
    whole = abs(value - round(value)) < 0.005
    places = 0 if whole or value >= 100 else 2
    return f"{sign}{prefix}{value:,.{places}f}"


# Public formatting helpers, used by the renderer so both agree on style.
pct = _pct
money = _money_plain
month_label = _month_label
