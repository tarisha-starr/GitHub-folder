---
name: money-brief
description: Weekly money review pulling cash position, unpaid invoices, upcoming obligations and receipt matching from Xero and Gmail. Use when the user says "money brief", "how's cash", "who owes me", "unpaid invoices", "what's my cash position", "chase payments", or wants a financial summary before making a spending or launch decision.
---

# Money Brief

Automations #44, #46 and #47 merged into one weekly review. Xero is
connected and currently used by nothing.

For a solo business these three are one job done once a week, not three
separate systems.

## Step 1: pull the numbers

Xero connector, in this order:

- `get_cash_position` — what's actually in the bank
- `get_contacts_and_receivables` — who owes money and how overdue
- `get_profit_and_loss` — the period, versus the one before it
- `get_top_customers_by_revenue` — which program is actually carrying the
  business
- `get_organisation_financial_year` — needed to frame the P&L period
  correctly, check it before comparing anything

Never estimate a number you can pull. If a call fails, say the figure is
unavailable rather than approximating it.

## Step 2: the brief

Four sections, in this order:

### 1. Cash position
Bank balance now. Change since last brief if known. Then the honest
question: how many months of runway does this represent at current
spending? Say if you can't tell.

### 2. Owed to her
Every unpaid invoice, sorted by how overdue. For each: who, how much, how
many days past due.

Flag anything over 30 days. For a business selling $97/mo memberships and
$8,500 retreats, an overdue retreat payment is a different order of
problem than a failed membership charge, so don't sort by date alone.
Sort by amount at risk.

### 3. Coming up
Known obligations: subscriptions, tax dates, contractor payments. Check
the `NZ Admin` Gmail label and `Receipts` for recurring charges. Flag
anything large enough to matter against the cash position in section 1.

### 4. Worth a look
Unmatched transactions, unusual charges, a subscription that's been
charging quietly, a payment that doesn't match an invoice. This is the
reconciliation half (#46). Exceptions only. Don't list normal
transactions.

## Step 3: payment reminders (#44)

For overdue invoices, **draft** the reminder in Gmail. Never send.

Tone matters here and gets this wrong easily. Her customers are women in
her programs, not corporate accounts payable. A firm dunning letter would
damage a relationship worth more than the invoice.

- warm, direct, brief, assume good faith
- assume it's an expired card or an oversight, because it usually is
- give the exact amount and a way to fix it in one step
- no threats, no late fees, no "final notice", no guilt
- follows `content/style_guide.md` like everything else

If someone is repeatedly overdue, flag it for her judgement rather than
escalating tone automatically. She may know something about that woman's
situation that the ledger doesn't.

## Rules

- **Read-only in Xero.** Never create, edit, void or reconcile anything.
  Report and draft, that's all.
- **Never send a payment email.** Draft only, always.
- **Don't give tax or accounting advice.** Flag things worth asking her
  accountant about. NZ tax treatment is not something to improvise.
- **Exact figures or none.** No rounding, no "roughly". If a number can't
  be retrieved, name the gap.
- **Financial data stays here.** Never write bank balances or customer
  payment problems into Notion pages, content files, or anywhere that
  could be published from. A customer's failed payment is private.

## Finish

Open with cash position and the largest amount at risk. Those are the two
numbers a decision actually turns on. Everything else is supporting
detail.

Worth scheduling weekly via a Routine once she's happy with the format.
