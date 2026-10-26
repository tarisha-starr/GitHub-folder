# site/, The Love Adventure page designs

Self-contained page designs for theloveadventure.com, built to the brand
guidelines held in Notion under **Assets & Ops → Website Build →
1. Brand Guidelines**.

These are design references to port into WordPress + Kadence. This folder is
not a deployment target and nothing here is wired to WordPress.

For what is actually published on the live site today, see
[`content/live/`](../content/live/index.md), pulled read only from the
WordPress REST API. [`content/live/FINDINGS.md`](../content/live/FINDINGS.md)
lists where the live site and these designs disagree.

## What it follows

- Palette, type and voice rules taken verbatim from the Notion brand docs
  (Pine Forest anchor, Terracotta held under 10 percent of surface, Marcellus
  display, Lora body, UK English, no dashes as punctuation).
- Structure follows **2. Site Architecture**: five header items plus a
  persistent Book a Call CTA, the Together and For Her split, and the four
  column footer.

## Constraints it was built under

- One file. The only external resource is the Google Fonts stylesheet.
- Renders completely without JavaScript. Scroll reveals and the headline swash
  are progressive enhancements only.
- Animation is limited to transforms and opacity, plus one one-shot stroke
  draw on the headline swash. No marquees, no animated filters.
- Honours `prefers-reduced-motion` and `prefers-color-scheme`.

## Still to confirm

- **The stats band conflicts with the live site.** It states five days, ten
  couples per retreat and two therapists. The published site says six couples
  on every page that states it, never mentions two therapists, and splits
  between five and six days depending on the page. See
  `content/live/FINDINGS.md`. This needs settling before the page ships.
- Testimonials are Tarisha's own couples testimonials, attributed as "Couples
  client" because no names were supplied. Add names or initials if consent
  allows.
- All three testimonials are women speaking about their husbands. One from a
  male partner, or from a couple jointly, would do more for the both-partners
  problem than any copy change.
- Founder photography is a styled placeholder block. The photos live in
  Dropbox. `automation/fetch_dropbox_images.py` can pull them now that Dropbox
  is reachable, once a token is set.

The unverified 4.9 average retreat rating was removed from the stats band on
Tarisha's instruction, and the grid rebalanced to three columns. Nothing on
either page now claims a rating or a review count.

## therapy.html

The `/together/therapy` page, rebuilt from the copy on deeplyinloveagain.com
with Tier 1 conversion treatment. Positioned toward couples who want more
intimacy and passion rather than couples in conflict.

Copy is Tarisha's own, kept as written. Edits were limited to what the
repositioning forced:

- Two conflict-led bullets were dropped from the "This is for you if" list and
  the remaining four reordered desire-first
- "2 spaces open all month" became "3 spaces before the end of the year"

The session keeps its own name, Get the Love You Desire. "The real problem
underneath the conflict" and "It really is possible" both stand as written:
"real" is discouraged as filler, not banned, and in both of those sentences it
is carrying the weight.

New copy that Tarisha has not written or approved, safe to delete:
the five FAQ answers, the three How It Works step descriptions, and the
stats band labels.

Needs doing before publication:

- embed the Fluent Forms block in the `#form` slot
- supply `images/therapy-hero.jpg` and `images/tarisha.jpg`
- settle the contact address. This page uses tarisha@theloveadventure.com. The
  live site uses hello@theloveadventure.com on all 24 pages, including in the
  privacy policy as the address for Privacy Act requests.
- settle how the free session works. This page describes an application with a
  reply in 1 to 3 business days. The live site books the same session instantly
  through TidyCal as a 20 minute discovery call. Both cannot be true.
