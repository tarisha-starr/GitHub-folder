#!/usr/bin/env python3
"""Render the CEO Command Center dashboard from the data files.

    python3 render_dashboard.py                       # data + default output path
    python3 render_dashboard.py --data DIR --out FILE
    python3 render_dashboard.py --as-of 2026-08-26    # pretend it is that day
    python3 render_dashboard.py --artifact            # body-only, for publishing
    python3 render_dashboard.py --brief-out brief.md  # also write the text brief

One self-contained HTML file, no external requests, no libraries. The numbers
come from command_center.build_report, which is where the formulas live.

--artifact drops the <!doctype>, <html>, <head> and <body> wrapper so the file
can go straight to the Artifact tool, which supplies its own skeleton.
"""

from __future__ import annotations

import argparse
import html
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from command_center import build_report, money, pct  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DATA = ROOT / "business" / "command-center"
DEFAULT_OUT = ROOT / "dashboards" / "command-center.html"

SECTIONS = [
    ("attention", "Attention"),
    ("snapshot", "Executive snapshot"),
    ("offers", "Offers"),
    ("pipeline", "Pipeline"),
    ("marketing", "Marketing"),
    ("clients", "Clients"),
    ("team", "Team"),
    ("decisions", "Decisions"),
    ("patterns", "Weekly patterns"),
    ("agents", "Agent HQ"),
]

STYLE = """
:root {
  --paper: #FDFBF5; --card: #FBF7EE; --sunk: #F5EFE3;
  --ink: #2A2520; --ink-soft: #6B6254; --line: #E4DCC9;
  --pine: #2D3E2C; --moss: #5D6B3F; --terracotta: #C75D3D; --rust: #9E4A2A;
  --gold: #B8945A; --camel: #C9A579; --taupe: #A89580;
  --high: #9E4A2A; --medium: #B8945A; --low: #5D6B3F;
}
:root:not([data-theme="light"]) { color-scheme: light dark; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #14180F; --card: #1F2C1F; --sunk: #182115;
    --ink: #F2ECDE; --ink-soft: #ADA593; --line: #33402F;
    --pine: #C9D6C2; --moss: #9DB077; --terracotta: #E08258; --rust: #E08258;
    --gold: #D2B27A; --camel: #C9A579; --taupe: #A89580;
    --high: #E08258; --medium: #D2B27A; --low: #9DB077;
  }
}
:root[data-theme="dark"] {
  --paper: #14180F; --card: #1F2C1F; --sunk: #182115;
  --ink: #F2ECDE; --ink-soft: #ADA593; --line: #33402F;
  --pine: #C9D6C2; --moss: #9DB077; --terracotta: #E08258; --rust: #E08258;
  --gold: #D2B27A; --camel: #C9A579; --taupe: #A89580;
  --high: #E08258; --medium: #D2B27A; --low: #9DB077;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font: 400 16px/1.55 "Iowan Old Style", Palatino, Georgia, serif;
  -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 1180px; margin: 0 auto; padding: 32px 20px 96px; }
h1, h2, h3 { font-weight: 400; letter-spacing: 0.01em; margin: 0; }
h1 { font-size: 30px; }
h2 { font-size: 21px; }
h3 { font-size: 16px; }
p { margin: 0 0 10px; }
a { color: var(--rust); }
.masthead { border-bottom: 2px solid var(--pine); padding-bottom: 18px; margin-bottom: 8px; }
.masthead .meta, .sub {
  font-family: ui-sans-serif, system-ui, "Helvetica Neue", Arial, sans-serif;
  font-size: 13px; color: var(--ink-soft); letter-spacing: 0.02em;
}
.masthead .meta { margin-top: 8px; }
nav.jump {
  position: sticky; top: 0; z-index: 5; background: var(--paper);
  border-bottom: 1px solid var(--line); padding: 10px 0; margin-bottom: 28px;
  display: flex; flex-wrap: wrap; gap: 6px 14px;
}
nav.jump a {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.08em; text-decoration: none;
  color: var(--ink-soft);
}
nav.jump a:hover { color: var(--rust); }
section { margin: 0 0 40px; scroll-margin-top: 64px; }
section > header { margin-bottom: 14px; }
.card {
  background: var(--card); border: 1px solid var(--line); border-radius: 3px;
  padding: 18px 20px;
}
.grid { display: grid; gap: 14px; }
.tiles { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
@media (min-width: 900px) { .tiles.six { grid-template-columns: repeat(3, 1fr); } }
.cols-2 { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
.cols-3 { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.tile .label {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 11px;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-soft);
}
.tile .value { font-size: 28px; line-height: 1.15; margin: 6px 0 4px; }
.tile .note { font-size: 13px; color: var(--ink-soft); }
.up { color: var(--moss); } .down { color: var(--rust); }
.flag { display: flex; gap: 12px; padding: 12px 0; border-top: 1px solid var(--line); }
.flag:first-child { border-top: 0; }
.flag .dot {
  width: 9px; height: 9px; border-radius: 50%; margin-top: 8px; flex: 0 0 9px;
}
.dot.high { background: var(--high); }
.dot.medium { background: var(--medium); }
.dot.low { background: var(--low); }
.flag .body { flex: 1; }
.flag .title { font-size: 17px; }
.flag .detail, .flag .where { font-size: 13px; color: var(--ink-soft); }
.flag .where {
  font-family: ui-sans-serif, system-ui, sans-serif; text-transform: uppercase;
  letter-spacing: 0.08em; font-size: 10px; margin-bottom: 2px;
}
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td {
  text-align: right; padding: 9px 10px; border-bottom: 1px solid var(--line);
  white-space: nowrap;
}
th:first-child, td:first-child { text-align: left; white-space: normal; min-width: 200px; }
thead th {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-soft);
  font-weight: 600; white-space: nowrap;
}
tbody tr:last-child td { border-bottom: 0; }
tfoot td { font-weight: 600; border-top: 2px solid var(--line); border-bottom: 0; }
td.name { font-size: 15px; }
.wraptext { display: block; white-space: normal; min-width: 210px; }
td .sub { display: block; }
.bar { background: var(--sunk); height: 8px; border-radius: 4px; overflow: hidden; min-width: 70px; }
.bar span { display: block; height: 100%; background: var(--moss); }
.bar span.warn { background: var(--terracotta); }
.bar span.mid { background: var(--camel); }
.pill {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 11px;
  letter-spacing: 0.04em; padding: 2px 8px; border-radius: 999px;
  border: 1px solid var(--line); background: var(--sunk); white-space: nowrap;
}
.pill.warn { border-color: var(--terracotta); color: var(--rust); }
.pill.good { border-color: var(--moss); color: var(--moss); }
ul.plain { margin: 0; padding-left: 18px; }
ul.plain li { margin-bottom: 4px; }
.rowline {
  display: flex; justify-content: space-between; gap: 6px 12px;
  align-items: baseline; flex-wrap: wrap;
}
.muted { color: var(--ink-soft); font-size: 13px; }
.chart { width: 100%; height: auto; display: block; }
.legend {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px;
  color: var(--ink-soft); display: flex; gap: 16px; margin-top: 8px; flex-wrap: wrap;
}
.legend i { display: inline-block; width: 10px; height: 10px; margin-right: 5px; }
.warnbox {
  border-left: 3px solid var(--terracotta); background: var(--sunk);
  padding: 10px 14px; margin-bottom: 20px; font-size: 14px;
}
.notebox {
  border-left: 3px solid var(--gold); background: var(--sunk);
  padding: 10px 14px; margin-bottom: 20px; font-size: 14px;
}
details summary { cursor: pointer; font-size: 14px; color: var(--ink-soft); }
@media (max-width: 640px) {
  .wrap { padding: 20px 14px 72px; }
  h1 { font-size: 24px; }
  .tile .value { font-size: 24px; }
}
"""


# ------------------------------------------------------------------ helpers

def esc(value):
    return html.escape(str(value)) if value is not None else ""


def fmt_money(value, currency=""):
    """Money for the page. Tables pass no currency, since the masthead says it once."""
    return money(value, currency)


def fmt_date(value):
    return value.strftime("%-d %b %Y") if isinstance(value, date) else "n/a"


def days(count):
    """3 days, 1 day, n/a."""
    if count is None:
        return "n/a"
    count = int(count)
    return f"{count} day" if abs(count) == 1 else f"{count} days"


def delta(value, invert=False, suffix="on the previous month"):
    """Colour a change. invert=True means going up is the bad direction."""
    if value is None:
        return '<span class="note">no comparison yet</span>'
    good = (value < 0) if invert else (value >= 0)
    css = "up" if good else "down"
    return (f'<span class="note {css}">{esc(pct(value, signed=True))} {esc(suffix)}</span>')


def tile(label, value, note=""):
    return (f'<div class="card tile"><div class="label">{esc(label)}</div>'
            f'<div class="value">{value}</div><div class="note">{note}</div></div>')


def bar(share, tone="", width_cap=1.0):
    share = 0.0 if share is None else max(0.0, min(share / width_cap, 1.0))
    return f'<div class="bar"><span class="{tone}" style="width:{share * 100:.1f}%"></span></div>'


def section(anchor, title, sub, body):
    subline = f'<div class="sub">{esc(sub)}</div>' if sub else ""
    return (f'<section id="{anchor}"><header><h2>{esc(title)}</h2>{subline}</header>'
            f'{body}</section>')


def table(headers, rows, foot=None):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
                   for row in rows)
    footer = ("<tfoot><tr>" + "".join(f"<td>{cell}</td>" for cell in foot) + "</tr></tfoot>"
              if foot else "")
    return (f'<div class="card scroll"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{body}</tbody>{footer}</table></div>')


def empty(message):
    return f'<div class="card muted">{esc(message)}</div>'


# ------------------------------------------------------------------ sections

def render_attention(report):
    flags = report["flags"]
    if not flags:
        return section("attention", "What deserves attention next",
                       "Nothing tripped a threshold this run.",
                       empty("No flags. Either the business is calm or the data is thin."))
    items = "".join(
        f'<div class="flag"><div class="dot {esc(f["severity"])}"></div><div class="body">'
        f'<div class="where">{esc(f["section"])}</div>'
        f'<div class="title">{esc(f["title"])}</div>'
        f'<div class="detail">{esc(f["detail"])}</div></div></div>'
        for f in flags)
    counts = {}
    for f in flags:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    order = {"high": 0, "medium": 1, "low": 2}
    sub = ", ".join(f"{n} {name}" for name, n in
                    sorted(counts.items(), key=lambda kv: order.get(kv[0], 3)))
    return section("attention", "What deserves attention next",
                   f"{len(flags)} flags: {sub}.", f'<div class="card">{items}</div>')


def revenue_chart(history, currency):
    """Columns for revenue with expenses drawn inside, so profit is the gap."""
    if not history:
        return ""
    history = history[-12:]
    peak = max([h["revenue"] for h in history] + [h["expenses"] for h in history]) or 1
    width, height = 720, 200
    pad_bottom, pad_top = 26, 10
    slot = width / len(history)
    col = min(46, slot * 0.55)
    bars = []
    for i, row in enumerate(history):
        centre = slot * (i + 0.5)
        rev_h = (row["revenue"] / peak) * (height - pad_bottom - pad_top)
        exp_h = (row["expenses"] / peak) * (height - pad_bottom - pad_top)
        base = height - pad_bottom
        bars.append(
            f'<rect x="{centre - col / 2:.1f}" y="{base - rev_h:.1f}" width="{col:.1f}" '
            f'height="{rev_h:.1f}" fill="var(--moss)" opacity="0.85"></rect>'
            f'<rect x="{centre - col / 6:.1f}" y="{base - exp_h:.1f}" width="{col / 3:.1f}" '
            f'height="{exp_h:.1f}" fill="var(--taupe)"></rect>'
            f'<text x="{centre:.1f}" y="{height - 8}" text-anchor="middle" '
            f'font-size="11" fill="var(--ink-soft)" '
            f'font-family="ui-sans-serif, system-ui, sans-serif">'
            f'{esc(row["label"][:3])}</text>')
    return (
        f'<div class="card"><svg class="chart" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="Revenue and expenses by month">'
        f'<line x1="0" y1="{height - pad_bottom}" x2="{width}" y2="{height - pad_bottom}" '
        f'stroke="var(--line)"></line>{"".join(bars)}</svg>'
        f'<div class="legend"><span><i style="background:var(--moss)"></i>Revenue</span>'
        f'<span><i style="background:var(--taupe)"></i>Expenses</span>'
        f'<span>Peak month {esc(fmt_money(peak, currency))}</span></div></div>')


def render_snapshot(report):
    snap, currency = report["snapshot"], report["currency"]
    if snap.get("empty"):
        return section("snapshot", "Executive snapshot", "",
                       empty("No months in finance.json yet."))

    parts = snap["forecast_parts"]
    tiles = "".join([
        tile("Revenue", esc(fmt_money(snap["revenue"], currency)),
             delta(snap["revenue_change"])),
        tile("Profit", esc(fmt_money(snap["profit"], currency)),
             f'<span class="note">{esc(pct(snap["margin"]))} margin</span>'),
        tile("Cash collected", esc(fmt_money(snap["cash_collected"], currency)),
             f'<span class="note">{esc(fmt_money(snap["collection_gap"], currency))} '
             f'still owed ({esc(pct(snap["collection_gap_share"]))})</span>'),
        tile("Expenses", esc(fmt_money(snap["expenses"], currency)),
             delta(snap["expense_change"], invert=True)),
        tile("Recurring revenue", esc(fmt_money(snap["mrr"], currency)),
             f'<span class="note">{esc(pct(snap["mrr_share"]))} of the month, '
             f'{esc(pct(snap["mrr_change"], signed=True))}</span>'),
        tile(f"Forecast, {snap['forecast_month_label']}",
             esc(fmt_money(snap["forecast"], currency)),
             f'<span class="note">{esc(fmt_money(parts["recurring"], currency))} recurring, '
             f'{esc(fmt_money(parts["pipeline"], currency))} weighted pipeline, '
             f'{esc(fmt_money(parts["committed"], currency))} already committed</span>'),
    ])

    runway = (f'cash covers {snap["runway_months"]:.1f} months at '
              f'{fmt_money(snap["monthly_burn"], currency)} a month'
              if snap["runway_months"] is not None
              else "cash on hand has not been recorded, so there is no runway figure")
    strip = (
        f'<div class="card"><div class="rowline"><div>'
        f'<strong>Where it is growing.</strong> Revenue over the last three months is '
        f'{esc(pct(snap["revenue_growth"], signed=True))} against the three before, '
        f'with {esc(int(snap["new_customers"]))} new customers in '
        f'{esc(snap["month_label"])}.</div></div>'
        f'<div class="rowline" style="margin-top:8px"><div>'
        f'<strong>Where it is leaking.</strong> Expenses are '
        f'{esc(pct(snap["expense_growth"], signed=True))} over the same span, '
        f'{esc(fmt_money(snap["collection_gap"], currency))} of invoiced revenue is '
        f'uncollected, and {esc(runway)}.</div></div></div>')

    return section("snapshot", "Executive snapshot", snap["month_label"],
                   f'<div class="grid tiles six">{tiles}</div>'
                   f'<div class="grid cols-2" style="margin-top:14px">'
                   f'{revenue_chart(snap["history"], currency)}{strip}</div>')


def render_offers(report):
    offers = report["offers"]
    if offers.get("empty"):
        return section("offers", "Offer scorecard", "", empty("No offers recorded yet."))

    rows = []
    for offer in offers["offers"]:
        margin_tone = "" if (offer["margin"] or 0) >= 0.6 else \
            "mid" if (offer["margin"] or 0) >= 0.4 else "warn"
        satisfaction = (f'{offer["satisfaction"]:g} / {offer["satisfaction_scale"]:g}'
                        f'<span class="sub muted">{offer["responses"]} responses</span>'
                        if offer["responses"] else '<span class="muted">no responses</span>')
        rows.append([
            f'<span class="name">{esc(offer["name"])}</span>'
            f'<span class="sub muted">{esc(offer["notes"])}</span>',
            esc(fmt_money(offer["price"])),
            f'{esc(int(offer["units_sold"]))} <span class="sub muted">of '
            f'{esc(int(offer["opportunities"]))}</span>',
            esc(pct(offer["conversion"], places=1)),
            esc(fmt_money(offer["revenue"])),
            esc(fmt_money(offer["delivery_cost"])),
            esc(fmt_money(offer["contribution"])),
            f'{esc(pct(offer["margin"]))}{bar(offer["margin"], margin_tone)}',
            satisfaction,
            f'{esc(pct(offer["contribution_share"]))}{bar(offer["contribution_share"])}',
        ])
    foot = ["Total", "", "", "", esc(fmt_money(offers["total_revenue"])), "",
            esc(fmt_money(offers["total_contribution"])), "", "", ""]
    return section(
        "offers", "Offer scorecard",
        f'{offers["period_label"]}. Contribution is revenue after refunds and delivery cost.',
        table(["Offer", "Price", "Sold", "Conversion", "Revenue", "Delivery",
               "Contribution", "Margin", "Satisfaction", "Share of profit"], rows, foot))


def render_pipeline(report):
    pipe, currency = report["pipeline"], report["currency"]
    if pipe.get("empty"):
        return section("pipeline", "Lead pipeline", "", empty("No leads recorded yet."))

    peak = max([s["value"] for s in pipe["by_stage"].values()] or [1]) or 1
    stage_rows = [[
        esc(stage.replace("_", " ").title()),
        esc(pipe["by_stage"][stage]["count"]),
        esc(fmt_money(pipe["by_stage"][stage]["value"])),
        esc(fmt_money(pipe["by_stage"][stage]["weighted"])),
        bar(pipe["by_stage"][stage]["value"] / peak),
    ] for stage in pipe["by_stage"]]

    source_rows = [[
        esc(source),
        esc(data["count"]),
        esc(fmt_money(data["value"])),
        esc(fmt_money(data["weighted"])),
        f'{data["won"]} won, {data["lost"]} lost',
    ] for source, data in pipe["by_source"].items()]

    follow_rows = []
    for lead in pipe["leads"]:
        if not lead["open"]:
            continue
        status = ('<span class="pill warn">overdue</span>' if lead["overdue"]
                  else '<span class="pill good">on track</span>')
        close = (f'{esc(fmt_date(lead["expected_close"]))}'
                 f'<span class="sub muted">{"in " if lead["days_to_close"] >= 0 else ""}'
                 f'{days(abs(lead["days_to_close"]))}'
                 f'{"" if lead["days_to_close"] >= 0 else " ago"}</span>'
                 if lead["days_to_close"] is not None else "not set")
        follow_rows.append([
            f'<span class="name">{esc(lead["name"])}</span>'
            f'<span class="sub muted">{esc(lead["offer"])} · {esc(lead["source"])}</span>',
            esc(lead["stage"].title()),
            esc(fmt_money(lead["value"])),
            esc(fmt_money(lead["weighted"])),
            close,
            days(lead["days_silent"]),
            f'{status}<span class="sub muted wraptext">{esc(lead["next_step"])}</span>',
            esc(lead["owner"]),
        ])

    tiles = "".join([
        tile("Open leads", esc(pipe["open_count"]),
             f'<span class="note">{esc(fmt_money(pipe["open_value"], currency))} '
             f'at full value</span>'),
        tile("Weighted pipeline", esc(fmt_money(pipe["weighted_value"], currency)),
             '<span class="note">value times the close rate for each stage</span>'),
        tile("Win rate", esc(pct(pipe["win_rate"])),
             f'<span class="note">{pipe["won"]} won, {pipe["lost"]} lost</span>'),
        tile("Needs a follow-up", esc(len(pipe["overdue"])),
             f'<span class="note">{esc(fmt_money(pipe["stale_value"], currency))} quiet for '
             f'more than {pipe["follow_up_days"]} days</span>'),
    ])

    return section(
        "pipeline", "Lead pipeline",
        "Weighted value uses the stage weights in leads.json.",
        f'<div class="grid tiles">{tiles}</div>'
        f'<div class="grid cols-2" style="margin-top:14px">'
        f'{table(["Stage", "Leads", "Value", "Weighted", ""], stage_rows)}'
        f'{table(["Source", "Leads", "Open value", "Weighted", "Closed"], source_rows)}'
        f'</div><div style="margin-top:14px">'
        f'{table(["Lead", "Stage", "Value", "Weighted", "Expected close", "Silent", "Follow-up", "Owner"], follow_rows)}'
        f'</div>')


def render_marketing(report):
    mk, currency = report["marketing"], report["currency"]
    if mk.get("empty"):
        return section("marketing", "Marketing performance", "",
                       empty("No campaigns recorded yet."))

    totals = mk["totals"]
    tiles = "".join([
        tile("Spend", esc(fmt_money(totals["spend"], currency)),
             f'<span class="note">{esc(int(totals["leads"]))} leads, '
             f'{esc(int(totals["customers"]))} clients</span>'),
        tile("Cost per lead", esc(fmt_money(totals["cpl"], currency)),
             '<span class="note">blended across every channel</span>'),
        tile("Cost per client", esc(fmt_money(totals["cac"], currency)),
             f'<span class="note">{esc(pct(totals["lead_to_client"], places=1))} '
             f'of leads convert</span>'),
        tile("Return on spend", f'{totals["roas"]:.2f}x' if totals["roas"] else "n/a",
             f'<span class="note">{esc(fmt_money(totals["revenue"], currency))} '
             f'attributed</span>'),
    ])

    rows = []
    for row in mk["campaigns"]:
        roas = f'{row["roas"]:.2f}x' if row["roas"] is not None else "n/a"
        if row["roas"] is not None and row["ranked"]:
            roas = (f'<span class="pill warn">{roas}</span>' if row["roas"] < 1
                    else f'<span class="pill good">{roas}</span>')
        cpl = esc(fmt_money(row["cpl"])) if row["cpl"] is not None else "no spend"
        if row["cpl_change"] is not None:
            css = "down" if row["cpl_change"] > 0 else "up"
            cpl += f'<span class="sub {css}">{esc(pct(row["cpl_change"], signed=True))}</span>'
        rows.append([
            f'<span class="name">{esc(row["channel"])}</span>'
            f'<span class="sub muted">{esc(row["name"])}</span>',
            esc(fmt_money(row["spend"])),
            esc(int(row["leads"])),
            cpl,
            esc(int(row["customers"])),
            esc(fmt_money(row["cac"])) if row["cac"] is not None else "n/a",
            esc(fmt_money(row["revenue"])),
            roas,
        ])
    foot = ["Total", esc(fmt_money(totals["spend"])), esc(int(totals["leads"])),
            esc(fmt_money(totals["cpl"])), esc(int(totals["customers"])),
            esc(fmt_money(totals["cac"])),
            esc(fmt_money(totals["revenue"])),
            f'{totals["roas"]:.2f}x' if totals["roas"] else "n/a"]

    if mk["ranked"]:
        best = mk["ranked"][0]
        ranking = (f'Top channel this period: <strong>{esc(best["channel"])}</strong> at '
                   f'{best["roas"]:.2f}x on {esc(fmt_money(best["spend"], currency))}. '
                   f'Channels under {esc(fmt_money(mk["min_spend"], currency))} of spend are '
                   f'listed but not ranked, so one lucky sale cannot top the table.')
    else:
        ranking = "No channel has enough spend behind it to rank yet."

    prior = (f' Cost per lead is compared with {mk["prior_period_label"]}.'
             if mk["prior_period_label"] else "")
    return section("marketing", "Marketing performance", mk["period_label"] + "." + prior,
                   f'<div class="grid tiles">{tiles}</div>'
                   f'<div style="margin-top:14px">'
                   f'{table(["Channel", "Spend", "Leads", "Cost per lead", "Clients", "Cost per client", "Revenue", "Return"], rows, foot)}'
                   f'</div><div class="card muted" style="margin-top:14px">{ranking}</div>')


def render_clients(report):
    ch, currency = report["clients"], report["currency"]
    if ch.get("empty"):
        return section("clients", "Client health", "", empty("No clients recorded yet."))

    status_line = ", ".join(f"{count} {status.replace('_', ' ')}"
                            for status, count in sorted(ch["by_status"].items()))
    tiles = "".join([
        tile("Paying clients", esc(ch["paying_count"]),
             f'<span class="note">{esc(fmt_money(ch["paying_value"], currency))} '
             f'of value on the books</span>'),
        tile("Need attention", esc(len(ch["needs_attention"])),
             '<span class="note">stalled, quiet, at risk, or renewing badly</span>'),
        tile("Renewals in 60 days", esc(len(ch["renewals"])),
             f'<span class="note">{esc(fmt_money(ch["renewal_value"], currency))} '
             f'up for renewal</span>'),
        tile("Cancellations, 30 days", esc(len(ch["churned_recent"])),
             f'<span class="note">{esc(pct(ch["churn_rate"]))} of the base</span>'),
    ])

    attention_rows = [[
        f'<span class="name">{esc(row["name"])}</span>'
        f'<span class="sub muted">{esc(row["offer"])}</span>',
        f'<span class="pill{" warn" if row["status"] == "at_risk" else ""}">'
        f'{esc(row["status"].replace("_", " "))}</span>',
        esc(fmt_money(row["value"])),
        f'{esc(int(row["engagement"]))}{bar(row["engagement"] / 100, "warn" if row["engagement"] < 40 else "mid" if row["engagement"] < 70 else "")}',
        days(row["days_quiet"]),
        f'<span class="wraptext">{"; ".join(esc(r) for r in row["reasons"])}</span>',
        esc(row["owner"]),
    ] for row in ch["needs_attention"]]

    renewal_rows = [[
        f'<span class="name">{esc(row["name"])}</span>'
        f'<span class="sub muted">{esc(row["offer"])}</span>',
        esc(fmt_date(row["renewal_date"])),
        days(row["days_to_renewal"]),
        esc(fmt_money(row["value"])),
        f'{esc(int(row["engagement"]))} / 100',
        esc(row["owner"]),
    ] for row in ch["renewals"]]

    churn_rows = [[
        esc(row["name"]),
        esc(row["offer"]),
        esc(fmt_money(row["value"])),
        esc(fmt_date(row["last_engagement"])),
        f'<span class="wraptext">{esc(row["notes"])}</span>',
    ] for row in ch["churned_recent"]]

    body = f'<div class="grid tiles">{tiles}</div><div style="margin-top:14px">'
    body += (table(["Client", "Status", "Value", "Engagement", "Quiet for",
                    "Why it is flagged", "Owner"], attention_rows)
             if attention_rows else empty("Nobody is flagged. Rare and worth noticing."))
    body += "</div>"
    if renewal_rows:
        body += ('<h3 style="margin:20px 0 8px">Renewals in the next 60 days</h3>'
                 + table(["Client", "Renews", "In", "Value", "Engagement", "Owner"],
                         renewal_rows))
    if churn_rows:
        body += ('<h3 style="margin:20px 0 8px">Cancelled in the last 30 days</h3>'
                 + table(["Client", "Offer", "Value", "Last seen", "What they said"],
                         churn_rows))
    return section("clients", "Client health",
                   f'{status_line}. Onboarding is flagged after {ch["onboarding_days"]} days, '
                   f'silence after {ch["quiet_days"]}.', body)


def render_team(report):
    team = report["team"]
    if team.get("empty"):
        return section("team", "Team capacity", "", empty("No people recorded yet."))

    cards = []
    for person in team["people"]:
        util = person["utilisation"]
        tone = "warn" if person["state"] == "overloaded" else \
            "" if person["state"] == "spare" else "mid"
        deadlines = "".join(
            f'<li>{esc(d["item"])} <span class="muted">'
            f'{esc(fmt_date(d["due"]))}'
            f'{", overdue" if d["overdue"] else ", at risk" if d["status"] == "at_risk" else ""}'
            f'</span></li>' for d in person["deadlines"]) or '<li class="muted">None logged</li>'
        blockers = "".join(
            f'<li>{esc(b["item"])} <span class="muted">waiting on '
            f'{esc(b.get("waiting_on", "someone"))}</span></li>'
            for b in person["blockers"]) or '<li class="muted">None</li>'
        cards.append(
            f'<div class="card person"><div class="rowline"><h3>{esc(person["name"])}</h3>'
            f'<span class="pill{" warn" if person["state"] == "overloaded" else ""}">'
            f'{esc(pct(util))} used</span></div>'
            f'<div class="muted">{esc(person["role"])} · '
            f'{person["committed_hours"]:g}h committed of {person["capacity_hours"]:g}h, '
            f'{person["spare_hours"]:g}h spare</div>'
            f'{bar(util, tone)}'
            f'<div class="muted" style="margin-top:10px">Owns: '
            f'{esc(", ".join(person["responsibilities"]) or "nothing logged")}</div>'
            f'<div style="margin-top:8px"><strong class="sub">Deadlines</strong>'
            f'<ul class="plain">{deadlines}</ul></div>'
            f'<div style="margin-top:8px"><strong class="sub">Blockers</strong>'
            f'<ul class="plain">{blockers}</ul></div></div>')

    summary = (f'{team["total_committed"]:g}h committed of {team["total_capacity"]:g}h across '
               f'{len(team["people"])} people, {team["total_spare"]:g}h spare, '
               f'{pct(team["utilisation"])} used.')
    return section("team", "Team capacity", summary,
                   f'<div class="grid cols-3">{"".join(cards)}</div>')


def render_decisions(report):
    log = report["decisions"]
    if log.get("empty"):
        return section("decisions", "Decision log", "", empty("No decisions recorded yet."))

    verdict_pill = {
        "worked": '<span class="pill good">worked</span>',
        "mixed": '<span class="pill">mixed</span>',
        "did_not_work": '<span class="pill warn">did not work</span>',
    }
    due_marker = '<span class="sub down">review is due</span>'
    rows = [[
        f'<span class="name">{esc(d["decision"])}</span>'
        f'<span class="sub muted">{esc(fmt_date(d["date"]))} · {esc(d["owner"])}</span>',
        f'<span class="pill">{esc(d["status"])}</span>',
        verdict_pill.get(d["verdict"], '<span class="muted">open</span>'),
        esc(fmt_date(d["review_date"])) + (due_marker if d["due_for_review"] else ""),
        f'<span class="wraptext">{esc(d["supporting_data"])}</span>',
        f'<span class="wraptext">{esc(d["expected_outcome"])}</span>',
        (f'<span class="wraptext">{esc(d["result"])}</span>' if d["result"]
         else '<span class="muted">not reviewed</span>'),
    ] for d in log["decisions"]]

    sub = (f'{log["open_count"]} open, {log["reviewing_count"]} in review, '
           f'{log["closed_count"]} closed. Of the {log["judged_count"]} judged, '
           f'{pct(log["hit_rate"])} worked.')
    return section("decisions", "Decision log", sub,
                   table(["Decision", "Status", "Verdict", "Review",
                          "What it was based on", "Expected", "What happened"], rows))


def render_patterns(report):
    pat = report["patterns"]
    latest = pat.get("latest") or {}
    observed = "".join(f"<li>{esc(item)}</li>" for item in pat["observed"])

    def column(title, items, fallback):
        body = "".join(f"<li>{esc(item)}</li>" for item in items) or \
            f'<li class="muted">{esc(fallback)}</li>'
        return (f'<div class="card"><h3>{esc(title)}</h3>'
                f'<ul class="plain">{body}</ul></div>')

    columns = "".join([
        column("Wins", latest.get("wins", []), "Nothing logged"),
        column("Concerns", latest.get("concerns", []), "Nothing logged"),
        column("Unexpected", latest.get("surprises", []), "Nothing logged"),
        column("Priorities", latest.get("priorities", []), "Not set yet"),
    ])

    history = ""
    if len(pat["weeks"]) > 1:
        blocks = []
        for week in pat["weeks"][1:]:
            def line(label, key):
                items = week.get(key) or []
                return (f'<div class="muted"><strong>{label}:</strong> '
                        f'{esc("; ".join(items)) or "nothing logged"}</div>')
            blocks.append(
                f'<div style="margin:12px 0"><strong>Week of '
                f'{esc(week.get("week_of", ""))}</strong>'
                f'{line("Wins", "wins")}{line("Concerns", "concerns")}'
                f'{line("Unexpected", "surprises")}{line("Priorities", "priorities")}</div>')
        history = (f'<details class="card" style="margin-top:14px">'
                   f'<summary>Earlier weeks ({len(pat["weeks"]) - 1})</summary>'
                   f'{"".join(blocks)}</details>')

    signals = (f'<div class="card" style="margin-top:14px"><h3>What the numbers say '
               f'about this week</h3><ul class="plain">{observed}</ul></div>'
               if observed else "")
    week_of = latest.get("week_of", "no week logged")
    return section("patterns", "Weekly patterns", f"Week of {week_of}",
                   f'<div class="grid cols-3">{columns}</div>{signals}{history}')


def render_agents(report):
    hq = report["agents"]
    if hq.get("empty"):
        return section("agents", "Agent HQ", "", empty("No agents recorded yet."))

    tiles = "".join([
        tile("Active agents", esc(hq["active_count"]),
             f'<span class="note">{esc(hq["paused_count"])} paused or retired</span>'),
        tile("Waiting on you", esc(len(hq["approvals"])),
             '<span class="note">outputs that cannot ship without a human</span>'),
        tile("Hours saved a week", f'{hq["hours_saved"]:g}',
             '<span class="note">your own estimate, summed across active agents</span>'),
        tile("Output quality",
             f'{hq["avg_quality"]:.1f} / {hq["quality_scale"]:g}' if hq["avg_quality"]
             else "n/a",
             '<span class="note">weighted by how many outputs you reviewed</span>'),
    ])

    approvals = ""
    if hq["approvals"]:
        rows = [[
            esc(a["item"]),
            esc(a["agent"]),
            f'<span class="pill{" warn" if a["urgency"] == "high" else ""}">'
            f'{esc(a["urgency"])}</span>',
            days(a["days_waiting"]),
        ] for a in hq["approvals"]]
        approvals = ('<h3 style="margin:20px 0 8px">Approvals needed</h3>'
                     + table(["Waiting for a decision", "Agent", "Urgency", "Waiting"], rows))

    cards = []
    for agent in hq["agents"]:
        activity = "".join(
            f'<li>{esc(fmt_date(a["date"]))}: {esc(a["summary"])} '
            f'<span class="muted">{esc(a["outcome"])}</span></li>'
            for a in agent["activity"][:4]) or '<li class="muted">No activity logged</li>'
        rework_tone = "warn" if agent["rework_rate"] > hq["rework_threshold"] else ""
        cards.append(
            f'<div class="card agent"><div class="rowline"><h3>{esc(agent["name"])}</h3>'
            f'<span class="pill{" good" if agent["status"] == "active" else ""}">'
            f'{esc(agent["status"])}</span></div>'
            f'<div class="muted">{esc(agent["current_assignment"] or "No current assignment")}</div>'
            f'<div class="muted" style="margin-top:8px">Owns: '
            f'{esc(", ".join(agent["responsibilities"]) or "nothing logged")}</div>'
            f'<div class="rowline" style="margin-top:10px"><span class="sub">Quality '
            f'{agent["rating"]:g} / {agent["scale"]:g} over {agent["reviews"]} reviews</span>'
            f'<span class="sub">{esc(pct(agent["rework_rate"]))} reworked</span></div>'
            f'{bar(agent["rework_rate"], rework_tone, width_cap=0.5)}'
            f'<div class="muted" style="margin-top:8px">'
            f'{agent["time_saved_hours_week"]:g}h saved a week · '
            f'{len(agent["approvals"])} waiting on you</div>'
            f'<div style="margin-top:8px"><strong class="sub">Recent activity</strong>'
            f'<ul class="plain">{activity}</ul></div></div>')

    return section("agents", "Agent HQ",
                   "What the AI agents own, what they are waiting on, and whether their "
                   "output holds up.",
                   f'<div class="grid tiles">{tiles}</div>{approvals}'
                   f'<div class="grid cols-3" style="margin-top:14px">{"".join(cards)}</div>')


# -------------------------------------------------------------------- output

def render_html(report, artifact=False):
    snap = report["snapshot"]
    month = snap.get("month_label", "no data")
    warnings = ""
    if report["warnings"]:
        warnings = ('<div class="warnbox">' + "<br>".join(esc(w) for w in report["warnings"])
                    + "</div>")
    if report.get("notes"):
        warnings += ('<div class="notebox">'
                     + "<br>".join(esc(n) for n in report["notes"]) + "</div>")

    body = "".join([
        f'<div class="masthead"><h1>CEO Command Center</h1>'
        f'<div class="meta">{esc(month)} · figures in {esc(report["currency"] or "your currency")} · '
        f'built {esc(fmt_date(report["as_of"]))}</div></div>',
        '<nav class="jump">' + "".join(
            f'<a href="#{anchor}">{esc(label)}</a>' for anchor, label in SECTIONS) + "</nav>",
        warnings,
        render_attention(report),
        render_snapshot(report),
        render_offers(report),
        render_pipeline(report),
        render_marketing(report),
        render_clients(report),
        render_team(report),
        render_decisions(report),
        render_patterns(report),
        render_agents(report),
    ])

    title = f"<title>CEO Command Center, {esc(month)}</title>"
    page = f'<div class="wrap">{body}</div>'
    if artifact:
        # The Artifact tool supplies the doctype, head and body wrapper itself.
        return f"{title}\n<style>{STYLE}</style>\n{page}\n"
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"{title}\n<style>{STYLE}</style>\n</head>\n<body>\n{page}\n</body>\n</html>\n")


def render_brief(report):
    """The short version, for the terminal or a weekly email."""
    lines = []
    snap = report["snapshot"]
    currency = report["currency"]
    lines.append(f"CEO Command Center, {snap.get('month_label', 'no data')} "
                 f"(built {fmt_date(report['as_of'])})")
    lines.append("=" * 64)
    if not snap.get("empty"):
        lines.append(
            f"Revenue {money(snap['revenue'], currency)} "
            f"({pct(snap['revenue_change'], signed=True)}), "
            f"profit {money(snap['profit'], currency)} at {pct(snap['margin'])} margin, "
            f"collected {money(snap['cash_collected'], currency)}.")
        lines.append(
            f"Recurring {money(snap['mrr'], currency)} "
            f"({pct(snap['mrr_share'])} of revenue). "
            f"Forecast for {snap['forecast_month_label']}: "
            f"{money(snap['forecast'], currency)}.")
    if report["flags"]:
        lines.append("")
        lines.append("What deserves attention next")
        for flag in report["flags"]:
            lines.append(f"  [{flag['severity']:<6}] {flag['section']}: {flag['title']}")
            if flag["detail"]:
                lines.append(f"           {flag['detail']}")
    else:
        lines.append("")
        lines.append("Nothing tripped a threshold this run.")
    priorities = (report["patterns"].get("latest") or {}).get("priorities") or []
    if priorities:
        lines.append("")
        lines.append("Priorities you set last week")
        lines.extend(f"  - {item}" for item in priorities)
    if report["warnings"]:
        lines.append("")
        lines.append("Data warnings")
        lines.extend(f"  ! {w}" for w in report["warnings"])
    if report.get("notes"):
        lines.append("")
        lines.extend(f"  note: {n}" for n in report["notes"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default=str(DEFAULT_DATA),
                        help=f"directory holding the nine JSON files (default: {DEFAULT_DATA})")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help=f"where to write the dashboard (default: {DEFAULT_OUT})")
    parser.add_argument("--as-of", default=None,
                        help="YYYY-MM-DD to treat as today, for ageing and forecasts")
    parser.add_argument("--artifact", action="store_true",
                        help="emit body-only HTML for the Artifact tool")
    parser.add_argument("--brief-out", default=None,
                        help="also write the plain-text brief to this path")
    parser.add_argument("--quiet", action="store_true", help="do not print the brief")
    args = parser.parse_args()

    as_of = None
    if args.as_of:
        try:
            as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
        except ValueError:
            parser.error("--as-of must be YYYY-MM-DD")

    data_dir = Path(args.data)
    if not data_dir.exists():
        parser.error(f"no data directory at {data_dir}. Copy the templates from "
                     f"{Path(__file__).resolve().parents[1] / 'templates'} into it.")

    report = build_report(data_dir, as_of)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(report, artifact=args.artifact))

    brief = render_brief(report)
    if args.brief_out:
        brief_path = Path(args.brief_out)
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(brief)
    if not args.quiet:
        print(brief)
    print(f"Dashboard written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
