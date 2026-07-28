# Connecting GoPlus

Status: **not connected.** Nothing in this repo talks to GoPlus yet. This file
is the setup path and the reasoning, so the work can start the moment the
credentials exist.

## What was checked

- **No GoPlus connector exists in Claude.** Checked the installed connector
  list (17 connectors) and the connector registry. The similarly-named one in
  the installed list is **GoDaddy**, which is domains.
- **No native GoPlus app in Zapier.** Searched three times; each search
  returned the generic popular-apps list rather than a match. Caveat worth
  knowing: Zapier supports private/unlisted apps that don't appear in search,
  so GoPlus may have an invite-only integration. Check inside GoPlus first.
- **No GoPlus reference anywhere in this repo**, working tree or git history.
- `usegoplus.com` and `help.usegoplus.com` both return **403** to automated
  fetches, so the API docs couldn't be read. This is why no client is written
  yet: inventing endpoints would be guessing.

## Zapier or API? Use both, split by job

They solve different problems, and the split is clean:

| Job | Use | Why |
|---|---|---|
| Someone requests a lead magnet, buys, or fills a form | **Zapier** | Event-driven. Has to fire in seconds. Polling an API can't do that. |
| Nightly pull of subscribers, revenue, course progress | **API** | Free per run, version-controlled, editable here. |
| Newsletter source material, briefs, reporting | **API** | It's reading data, not reacting to it. |
| Onboarding sequence when someone joins | **Zapier** | Event-driven again. |

**If only one gets built first, build the API.** Three reasons, specific to
this repo:

1. The pattern already exists here. Sixteen workflows, secrets, Python
   scripts. A GoPlus puller is the seventeenth, not a new way of working.
2. Zapier bills per task. Daily pulls and per-post pushes add up; a cron job
   in Actions costs nothing.
3. The logic lives in git, so it's reviewable and fixable. A broken Zap is UI
   work in someone else's dashboard.

The one thing the API can't do is react instantly. So lead magnet delivery
(#16) and onboarding (#28) still want Zapier, even after the API exists.

## Setup, in order

### 1. Check GoPlus for a Zapier integration first

Settings → Integrations. If there's a Zapier connect button or invite link,
use it. That's the fastest path and it needs no code at all.

### 2. Get an API key

Settings → API, or Developers. Then add it as a GitHub Actions secret:

**https://github.com/tarisha-starr/GitHub-folder/settings/secrets/actions/new**

| Secret name | Value |
|---|---|
| `GOPLUS_API_KEY` | the key GoPlus gives you |
| `GOPLUS_API_BASE` | the base URL from their docs, if it isn't the default |
| `GOPLUS_ACCOUNT_ID` | only if their API needs it |

Add the same names to your local `automation/.env` if you want to run the
puller by hand. `.env` is gitignored; `.env.example` holds the placeholders.

**Never paste the key into a chat, an issue, or a commit.** The secrets page
above is the only place it goes.

### 3. Send the docs link

Once the key exists, the API docs URL is the last missing piece. With it, the
puller gets written to match the real endpoints rather than guessed ones.

### 4. If there's no API at all, fall back to webhooks

```
GoPlus event  →  GoPlus webhook  →  Zapier Catch Hook
              →  Zapier writes a row into Notion
              →  read natively via the Notion connector
```

This mirrors `automation/zapier_push.py`, which already posts to a Zapier
Catch Hook in the other direction. The pattern is proven here.

The GoPlus-side and Zapier-side steps need a login, so they're yours to do.
Everything downstream of the Catch Hook gets built here.

## Which events matter

Worth deciding before anything is wired, because it determines what gets
caught:

- new subscriber / lead magnet request
- purchase or failed payment
- form submission
- course or module completion
- membership cancellation

## Open question first

The Zapier account already has **ActiveCampaign** (54 actions), **Stripe**,
**TidyCal** and **Xperiencify** enabled and reachable today. These overlap
heavily with GoPlus. Building list automations against the wrong platform is
wasted work, so which one is the source of truth needs answering before any
of this gets built.
