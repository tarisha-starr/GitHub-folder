# site/ — The Love Adventure homepage

A single self-contained homepage design for theloveadventure.com, built to the
brand guidelines held in Notion under **Assets & Ops → Website Build →
1. Brand Guidelines**.

This is a design reference to port into WordPress + Kadence. It is not a
deployment target and nothing here is wired to WordPress.

Two companion documents:

- **`CREATIVE-DIRECTION.md`** — the concept, art direction, typography, colour
  proportion, the section by section experience, the hero spec, the motion
  system, and the build sequence. Read this before changing the design.
- **`AUDIT.md`** — the ranked audit of the previous version and the pre launch
  checklist. Every P0 and P1 in it has been actioned in this build.

## What it follows

- Palette, type and voice rules taken verbatim from the Notion brand docs
  (Pine Forest anchor, Terracotta held under 10 percent of surface, Marcellus
  display, Lora body, UK English, no dashes as punctuation).
- Structure follows **2. Site Architecture**: five header items plus a
  persistent Book a Call CTA, the Together and For Her split, and the four
  column footer.

## What changed in the cinematic rebuild

- **Photography led.** Four plates wired to `images/site/`, each with a colour
  gradient fallback so a missing file still composes. See
  `images/site/README.md` for which frame goes where.
- **The mesh gradient, the three blurred orbs and the frosted glass card are
  gone.** That combination is the most recognisable machine generated look on
  the web, and the orbs animated a 72px blur for as long as the tab was open.
- **Colour proportion inverted.** Roughly half the page is now Pine Deep or
  photograph, where before it was three quarters cream. No more than two light
  sections ever run together.
- **Nine outline icons removed.** The six pillars are a numbered editorial list
  with a sticky heading. The three streams are hairline ruled columns.
- **The 4.9 rating and the four column stats band are gone.** The retreats have
  not run, so there is no average, and an unsubstantiated rating is a Fair
  Trading Act 1986 exposure. The three facts that are true live in the hero
  strip instead.
- **Navigation points at the actual URLs** from the site architecture rather
  than at on page anchors. They will 404 until those pages exist, which is the
  correct behaviour and is visible to whoever is building.
- **Metadata added.** Open Graph, Twitter card, canonical, JSON-LD.
- **Motion system.** Two easing curves, 14px reveals with a 70ms stagger, a
  header that solidifies past the hero, a scroll progress line, photographic
  drift on desktop, and a mobile sticky Book a call bar. All of it off under
  `prefers-reduced-motion`, and none of it required for the page to work.

## Constraints it was built under

- One file. The only external resource is the Google Fonts stylesheet.
- Renders completely without JavaScript. Scroll reveals and the headline swash
  are progressive enhancements only.
- Animation is limited to transforms and opacity, plus one one-shot stroke
  draw on the headline swash. No marquees, no animated filters.
- Honours `prefers-reduced-motion` and `prefers-color-scheme`.

## Still to confirm

- **The four photographs.** `images/site/` has a README naming exactly which
  frame goes where. Nothing else is blocking.
- Testimonials are Tarisha's own couples testimonials, attributed as "Couples
  client" because no names were supplied. Add names or initials if consent
  allows.
- Retreat dates and pricing. The page deliberately makes no claim about either.
- The newsletter line in the footer has no form behind it yet. Fluent Forms.

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
nothing else. The contact address is now tarisha@theloveadventure.com,
which needs to exist before the page goes live.
