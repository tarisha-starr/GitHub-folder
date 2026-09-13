# Wild Sky Coffee — Site Audit

Audited 13 September 2026 against the live site. Theme: Symmetry 8.3.2 on
Shopify. 10 products live, $14–$168 NZD, shipping NZ (free) and AU (flat A$15).

Everything below is something I checked on the live site, not a guess. Fixes are
ordered by money-per-hour, not by severity.

---

## What is already good, and don't let anyone talk you out of it

- **The voice.** "Transforms tired grumpy hikers into perfectly nice human
  beings" is worth more than any agency could sell you. The product descriptions
  have a point of view. Almost no gear store does.
- **The Brew Table section.** The "while your friends balance their coffee on the
  nearest rock" paragraph is the best piece of selling on the site.
- **Free NZ shipping.** A genuine advantage, currently buried in a policy page.
- **Two founders who actually use the gear**, with photos and named locations.
  That is the trust asset competitors buy influencers to fake.
- **The blog has the right instinct** — Wānaka, the Marlborough Sounds. It just
  isn't structured to be found.

---

## P0 — do these first (highest return, all doable this week)

### 1. The homepage title tag is just "Wild Sky Coffee"
Google's single strongest on-page signal is currently a brand nobody is
searching for yet. Every other page (collections, contact, products) has no meta
description either. Fix list in `05-seo-pack.md`.
**Impact: high. Effort: one hour.**

### 2. Nothing tells a buyer which cup to choose
You sell three drinking vessels and give her no way to compare them:

| | Summit Mug | Camp Cup | Kea Mountain Cup |
|---|---|---|---|
| Price | $25 | $35 | $59 |
| Capacity | 225ml | 500ml | 225ml |
| Weight | 45g | 70g | 85g |
| Wall | Single | Single | Double |

That table does not exist anywhere on the site. It should be on all three
product pages and on the Coffee Gear collection page. Add a fourth row —
"on the stove?" — and a one-line "pick this if…" for each. Copy in
`04-product-pages.md`.
**Impact: high. Effort: two hours.**

### 3. No trust elements at the point of decision
The product page has a price, a quantity box and an Add to cart. Below that:
nothing until the footer. No shipping promise, no returns line, no guarantee, no
stock status, no reviews. Add a four-icon trust bar directly under Add to cart:

> Free NZ shipping · Dispatched in 1–3 days from Auckland · 30-day returns ·
> Tested in the Kaimanawas, not in an office

All four are already true. You are just not saying them where she is deciding.
**Impact: high. Effort: two hours of theme work.**

### 4. Zero reviews, and no mechanism to collect them
A new store selling $59 cups without a single review is asking for a lot of
faith. Install Judge.me (free tier is enough) or Shopify's own product reviews,
and email every existing customer once asking for a photo and two sentences. Ten
reviews with a mug on a trig station will outperform anything else in this
document.
**Impact: high. Effort: one hour to install, then patience.**

### 5. The announcement bar is competing with your own checkout
"Sign up for our 20% off launch special" sits above every page, including
product pages. You are telling a ready buyer to stop, not buy, and go find a
discount first. Two problems: she abandons the cart to hunt for the code, and
the only site-wide message is about price rather than about you.

Swap the permanent bar to the trust line ("Free NZ shipping · Designed and
tested in New Zealand") and move the 20% offer into a timed pop-up and the
footer only. Also: a "launch special" with no end date trains people to wait,
and an open-ended discount claim is the kind of thing the Fair Trading Act 1986
takes a dim view of. Give it a date and honour it.
**Impact: high. Effort: thirty minutes.**

### 6. Five of ten product URLs don't match the product
| Product | Current URL | Should be |
|---|---|---|
| Summit Mug | `/products/sumit-mug` | `/products/summit-mug` (typo, live) |
| The Trail Spork | `/products/spooky-spork` | `/products/titanium-trail-spork` |
| Wild Coffee Scooper | `/products/round-camp-cup` | `/products/wild-coffee-scooper` |
| Camp Cup | `/products/summit-brew-cup` | `/products/titanium-camp-cup-500ml` |
| Brew Table | `/products/camp-kitchen-table` | `/products/titanium-brew-table` |

These are leftovers from whatever the product was called first. They cost you
keyword relevance and they look careless to anyone who reads a URL. Shopify
offers to create a redirect when you change a handle — leave that box ticked.
**Impact: medium-high. Effort: twenty minutes.**

### 7. Three empty collections are live and crawlable
`/collections/cups` (0 products), `/collections/coffee-makers-1` "Wild Kitchen"
(0), `/collections/frontpage` (0). Anyone who lands there sees an empty shop.

The cause is upstream: **none of your products have a product type or tags
set** — seven are blank, three say "Other". That means no automated collections,
no filtering, no "shop by weight", no cross-sell logic. Set type and tags on all
ten products (suggested values in `05-seo-pack.md`), then fill or delete the
empty collections.
**Impact: medium-high. Effort: one hour.**

### 8. Typos on live pages
| Where | Now | Fix |
|---|---|---|
| Homepage, Brew Table | "your pack and and only weighs 410 gms" | "your pack, and weighs just 410g" |
| Homepage, hero section heading | "the best part of the hike is the&nbsp; coffee" (double space) | single space |
| Traverse Coffee Press | "it's bigger enough to make coffee for two" | "it's big enough to make coffee for two" |
| Camp Cup | "when the temperatrue drops" | "temperature" |
| Blog post title and body | "Malborough Sounds" | "Marlborough Sounds" (also a search term you're currently misspelling) |
| Homepage, Why we love our work | "The answer is simple we're outdoor people" | "The answer is simple — we're outdoor people" |
| Our Story | "the ritual of brewing coffee a place where adventure" | "…brewing coffee — a place where adventure" |
| Our Story, last line | "There's a bit of magic being outside we just reckon" | "There's a bit of magic in being outside, and we reckon" |
**Impact: medium (trust). Effort: twenty minutes.**

---

## P1 — next two weeks (this is where the revenue is)

### 9. There are no bundles, and your best customer wants one
Average order value is currently capped by the fact that every visitor has to
assemble a kit out of ten loose objects. Sarah (avatar 2) will buy a named,
photographed kit at $150 and will buy one $35 cup if you make her do the work.

Three bundles, priced to save her roughly 10% against buying separately, in
`06-offer-bundles-email.md`:
- **The Summit Kit** — Alpine Pot, Summit Mug, Scooper, Spork
- **The Slow Morning Kit** — Brew Table, Traverse Press, two Kea Cups
- **The Hut Kit** — Traverse Press, Bean Vault, Scooper, two Camp Cups

Before you publish the weights and the "it all nests" claim, put the pot on a
bench and check what actually fits inside it, then publish the numbers you
measured. Verified nesting is one of the most persuasive things an ultralight
brand can say, and one of the worst things to get wrong.
**Impact: high. Effort: half a day including photography.**

### 10. Nothing on the site is aimed at a gift buyer, and it's mid-September
Christmas is the biggest single opportunity this store will have this year, and
the range is almost perfectly shaped for it — $14 to $168, with obvious price
bands. Today it is invisible to anyone shopping for a present.

Add before the end of October: a **Gifts** nav item with under-$30 /
around-$60 / the-full-kit bands, a gift note field at checkout, and a visible
"order by [date] for Christmas delivery" line once NZ Post publish their cut-offs.
**Impact: high, and time-limited. Effort: half a day.**

### 11. Free NZ shipping is your best offer and it appears on one policy page
It should be in the announcement bar, on every product page under the button, in
the cart, and in the footer. Also consider **free AU shipping over $120** — your
AU customers currently pay A$15 flat, which kills the small order and barely
dents the big one. Free over $120 turns a $65 press into a $130 kit.
**Impact: medium-high. Effort: one hour.**

### 12. No FAQ page, so every objection goes unanswered
The questions from `01-customer-avatars.md`, answered plainly, on one page that
will also pick up search traffic. Draft in `04-product-pages.md`. The two that
matter most: **single wall vs double wall**, and **can it go on a flame**.

On the flame question — a sealed double-wall vessel should not be put over
direct heat. Confirm the specifics with your supplier and then state it plainly
on the Kea Mountain Cup page. It is both a safety line and a buying-decision
line, and right now the page is silent on it.
**Impact: medium-high. Effort: two hours.**

### 13. No brew guide, which is the one piece of content that earns search traffic
"How to make good coffee on a camp stove" with your dose, your grind, your ratio
and your press. It answers avatar 4, it gives avatar 1 a reason to trust the
press, and it is the only page on the site with a shot at ranking for
non-brand searches this year. Dose is easy — your own Scooper is 15g for 250ml,
so the ratio is already decided for you.
**Impact: medium-high, compounding. Effort: half a day.**

### 14. The founders' quote is unattributed
The "Making coffee outside is special" quote on the homepage has no name and no
face. It is the single most human thing on the page. Put Mark's or Tarisha's
name and a photo on it, and link to Our Story.
**Impact: medium. Effort: fifteen minutes.**

---

## P2 — when the above is done

15. **The hero says nothing about what you sell or what it costs.** "Coffee gear
    for your next adventure / Designed in the backcountry of New Zealand" is
    pleasant but generic, and "Show me" is a vague CTA. Options in
    `03-homepage-copy.md`.
16. **11 of 29 homepage images have missing or empty alt text.** Free SEO and an
    accessibility obligation. Alt text written for you in `05-seo-pack.md`.
17. **Brew Table is featured on the homepage with no price** ($84). Price
    reduces friction; hiding it adds a click and a suspicion.
18. **"Regular price" labels on every product** (theme default) imply a sale
    price that doesn't exist. Turn the label off in theme settings.
19. **og:image is served over `http://`** while the site is https. Some
    platforms will drop the preview image. Change it to `https://`.
20. **No analytics or ad pixel visible in the page source.** It may be installed
    as a Shopify web pixel, which wouldn't show up — but verify in Settings →
    Customer events that GA4 and the Meta pixel are both firing. Without them
    none of the work in this document can be measured.
21. **No cross-sells.** "Goes well with" on each product page: press → scooper
    and bean vault; pot → mug and spork; grinder → press. Free AOV.
22. **No stock indicator.** "In stock, dispatched from Auckland in 1–3 days"
    beats silence.
23. **Blog posts have no internal links to products.** The Wānaka post should
    link to the kit that was in the pack.

---

## Suggested order of work

**This week** — 1, 5, 6, 8 (an afternoon of small fixes, mostly in Shopify
admin, no theme code), then 2 and 3.

**Next week** — 4 and 7, then start collecting reviews. Write the bundles (9) and
shoot them.

**Weeks 3–4** — Gifts navigation and Christmas cut-off dates (10), free AU
shipping threshold (11), FAQ (12).

**Weeks 5–6** — Brew guide (13), email welcome sequence
(`06-offer-bundles-email.md`), then the P2 list as time allows.

The pattern: everything in P0 is words and settings, not design. You do not need
a redesign. You need the site to answer the four questions a buyer is already
asking — which one, will it fit, can I trust you, what does delivery cost — and
then get out of the way.
