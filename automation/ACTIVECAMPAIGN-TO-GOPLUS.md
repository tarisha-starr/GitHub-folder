# Migrating off ActiveCampaign to GoPlus

Status: **planning only.** Nothing has been built or moved.

## What I can and can't do here

**Can't:** build anything inside GoPlus. There's no connector, no Zapier app,
no readable API docs, and no login. Every automation, form and sequence in
GoPlus has to be created by Tarisha in their UI.

**Can:** read what's currently in ActiveCampaign through Zapier (54 actions
are enabled) and turn it into a complete rebuild checklist, so nothing is
discovered missing three weeks after the switch. That read is pending
approval.

**Can:** once GoPlus has an API key and docs, build the repo-side integration
so content, briefs and reporting keep working after the move.

## The rule that matters

**Don't turn ActiveCampaign off until every item below is ticked and tested.**
Keep paying for one more month than feels necessary. The failure mode isn't a
broken automation, it's a silent one: a buyer who joins and never receives the
welcome sequence, and you find out when she emails asking where her login is.

## What has to be inventoried before anything moves

This is the checklist the pending Zapier read fills in automatically. Doing it
by hand in the ActiveCampaign UI works too, it's just slower.

### 1. Lists and audiences
- [ ] Every list, with subscriber count
- [ ] Which lists are actually in use vs abandoned
- [ ] Subscriber export, CSV, including unsubscribes

**Export unsubscribes and honour them in GoPlus.** Emailing someone who
opted out is the one migration mistake with legal weight, and it's the
easiest one to make, because a fresh import arrives with everyone "active".

### 2. Tags
- [ ] Full tag list
- [ ] What each tag means and what sets it
- [ ] Which tags trigger automations

Tags are usually where the real logic hides. A tag like `serw-buyer-2025`
may be the only thing separating a paying member from a cold lead.

### 3. Automations and sequences
For each one:
- [ ] Name and what it's for
- [ ] The trigger, form submit, tag added, purchase, date
- [ ] Every email in it, subject and body
- [ ] Wait times between emails
- [ ] Branching, if any
- [ ] Whether it's currently on

### 4. Forms and landing pages
- [ ] Every opt-in form and where it's embedded
- [ ] What each form tags or triggers
- [ ] Which lead magnet each one delivers

**Any form embedded on the website keeps posting to ActiveCampaign until the
embed code is replaced.** This is the most common way a migration leaks
leads for months.

### 5. Campaigns worth keeping
- [ ] Broadcasts with strong open or click rates, as templates
- [ ] The current newsletter template

### 6. Integrations pointing at ActiveCampaign
- [ ] Stripe, purchase triggers
- [ ] Xperiencify, course enrolment
- [ ] TidyCal, booking follow-ups
- [ ] Facebook Lead Ads
- [ ] Any Zap with ActiveCampaign as trigger or action
- [ ] WordPress plugins or embeds

Each of these is a separate rewire, and each fails silently if missed.

## Rebuild order in GoPlus

Do it in this order so nothing is live and broken at the same time.

| Step | What | Why this order |
|---|---|---|
| 1 | Import contacts, with unsubscribe status | Nothing works without the list |
| 2 | Recreate tags | Automations depend on them |
| 3 | Rebuild the buyer sequences first | Money path. Highest cost if broken |
| 4 | Rebuild lead magnet delivery | Second highest, it's the front door |
| 5 | Rebuild nurture and newsletter | Lower stakes, more forgiving |
| 6 | Repoint forms on the site | Only now, once the receiving end exists |
| 7 | Repoint Stripe, Xperiencify, TidyCal, FB Lead Ads | Same reason |
| 8 | Run both in parallel for two weeks | Catches what the checklist missed |
| 9 | Turn ActiveCampaign off | Last, and not before |

## Test before switching off

For each rebuilt automation, use a real address you control:

- [ ] Opt in through the live form, does the magnet arrive
- [ ] Buy something at the lowest price point, does the welcome sequence fire
- [ ] Check the tag actually got applied
- [ ] Unsubscribe, does it stick
- [ ] Book via TidyCal, does the follow-up fire

An automation that looks correct in the builder and never fires is the normal
outcome, not the unusual one. Test every path.

## What changes in this repo

Little, and that's deliberate. The repo talks to Buffer, Zapier and SMTP, not
ActiveCampaign. After the move:

- `automation/zapier_push*.py` keeps working, it posts to a Catch Hook and
  doesn't care what's downstream
- The daily content pipeline is unaffected
- `automation/goplus_check.py` verifies the API credentials once they exist
- The GoPlus puller gets written once the API docs are available

## Open items

1. **Approve the Zapier read** so the inventory above fills in with real
   lists, tags and automations rather than being a blank checklist.
2. **GoPlus API docs URL**, so the puller targets real endpoints.
3. **Is Xperiencify being replaced too?** GoPlus overlaps it as well. If both
   are going, course enrolment needs rebuilding in the same pass rather than
   twice.
