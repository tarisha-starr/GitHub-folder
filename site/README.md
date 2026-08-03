# site/ — The Love Adventure homepage

A single self-contained homepage design for theloveadventure.com, built to the
brand guidelines held in Notion under **Assets & Ops → Website Build →
1. Brand Guidelines**.

This is a design reference to port into WordPress + Kadence. It is not a
deployment target and nothing here is wired to WordPress.

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

- The stats band uses two figures that need checking before publication:
  the 4.9 average rating, and whether every retreat is capped at six couples.
- Testimonials are genuine quotes from `content/testimonials.json`, which came
  from women's workshops. Attribution needs settling before they sit on a
  couples page.
- Founder photography is a styled placeholder block.

## therapy.html

The `/together/therapy` page, rebuilt from the copy on deeplyinloveagain.com
with Tier 1 conversion treatment. Positioned toward couples who want more
intimacy and passion rather than couples in conflict.

Copy is Tarisha's own, kept as written. Edits were limited to what the brand
rules or the repositioning forced:

- "the real problem underneath the conflict" became "the problem underneath the
  conflict", since the word "real" is banned in the voice guide
- "It really is possible" became "It is possible", same rule
- Two conflict-led bullets were dropped from the "This is for you if" list and
  the remaining four reordered desire-first
- "2 spaces open all month" became "3 spaces before the end of the year"
- The session was renamed from "Get the Love You Desire" to "The Second Spring
  Session"

New copy that Tarisha has not written or approved, safe to delete:
the five FAQ answers, the three How It Works step descriptions, and the
stats band labels.

Needs doing before publication: embed the Fluent Forms block in the `#form`
slot, supply `images/therapy-hero.jpg` and `images/tarisha.jpg`, and decide
whether the contact address should move off deeplyinloveagain.com.
