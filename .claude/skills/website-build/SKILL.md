---
name: website-build
description: Build, redesign, or improve web pages for Tarisha's sites, above all theloveadventure.com. Use this whenever the user asks for a website, landing page, sales page, homepage, hero section, or "make the site look better / more designed / higher converting", and also when they ask to clone a reference site, do a mobile pass, QA a page in a browser, or add conversion elements like sticky bars, guarantees, FAQs or urgency. Trigger it even when they only say "improve the site" or name a page like the services page, because the brand rules, the voice rules and the WordPress target all live here and a generic build will get them wrong.
---

# Website build

Pages for The Love Adventure and the older Radiant Woman properties. The point
of this skill is that a good-looking page is not enough: the brand has written
rules, the voice has banned words, and the finished page has to survive being
pasted into WordPress. Getting any of those wrong makes the work unusable even
when the design is strong.

## Read the brand before you design anything

The source of truth is Notion, not the repo and not the logo files. Fetch it
first, every time:

**Assets & Ops → Website Build, theloveadventure.com**
- `1. Brand Guidelines` — palette, typography, photography, voice
- `2. Site Architecture` — sitemap, nav, footer, redirects
- `3. Kadence Build Directions` — which starter template each page uses
- `Build Progress Checklist` — what is already done, and the milestone gates
- `The Love Adventure, Brand Story` — the three streams and the positioning

Search Notion for "Website Build theloveadventure.com" to find them.

This matters more than it sounds. The logo files in `images/brand/` are plum
and gold, left over from the old Sexual Empowerment for Women brand. The live
brand is Soft Autumn: Pine Forest anchor, Terracotta accent. Anyone who derives
a palette from the logo builds the wrong site convincingly.

### The palette, for reference

Pine Deep `#1F2C1F`, Pine Forest `#2D3E2C`, Moss `#5D6B3F`, Terracotta
`#C75D3D`, Rust `#9E4A2A`, Antique Gold `#B8945A`, Camel `#C9A579`, Warm Taupe
`#A89580`, Cream `#F5EFE3`, Soft Ivory `#FBF7EE`, Paper `#FDFBF5`, Warm
Charcoal `#2A2520`.

Terracotta is capped at 5 to 10 percent of any page's visual surface. Never
pure white, never pure black. Display font is Marcellus at weight 400 only, so
if a brief asks for a "bolder" headline, you cannot reach for a heavier weight:
go up in size, tighten the tracking, and add a hairline optical stroke. Body is
Lora, and italics carry emphasis in preference to bold.

Cream plus a serif display plus a terracotta accent is currently one of the
most recognisable AI-generated looks on the web. The brand legitimately owns
those ingredients, so the way out is proportion: anchor pages in Pine Deep and
let cream act as relief, rather than the other way round.

## The voice rules that will get the work rejected

From the brand guidelines and `content/style_guide.md`:

- UK and NZ spelling. Realise, colour, behaviour, programme.
- No em dashes, en dashes, or hyphens used as punctuation. Commas, full stops,
  ellipses, colons, brackets instead. Compound modifiers like "long-term" are
  fine.
- The word "real" is banned outright, in every form.
- No coachy hype, no clinical jargon, no performative empowerment, no "come as
  you are".
- Short sentences. Long sentences. Variation. Write like speech.

Run `scripts/check_voice.py` over the finished HTML before showing anyone. It
catches dashes, banned words and US spellings in the visible copy, and it will
find the one that slipped into a `<title>` tag.

## Build constraints

Every page is one self-contained HTML file, because the destination is a
Kadence block in WordPress and anything with a build step cannot be pasted in.

- The Google Fonts stylesheet is the only external resource. Everything else is
  inline: CSS, JS, SVG icons. No icon libraries, no CDN scripts.
- The page must render completely without JavaScript. Reveals, counters and
  draw-on effects are enhancements layered on top of a working page. The
  pattern: add a `js` class to `<html>` from an inline script in the head, and
  scope every hidden initial state to `.js`. Without JS nothing hides.
- Animate transforms and opacity only. No animated blur or turbulence filters,
  no auto-scrolling marquees, no heavy blend modes. A static `backdrop-filter`
  on a frosted card is fine, because it rasterises once.
- Honour `prefers-reduced-motion` and `prefers-color-scheme`.
- Mobile-first. Verify at 390px that nothing scrolls sideways.

## Workflow

Pick the depth the request deserves. A tweak to an existing page does not need
three variants; a new flagship sales page does.

### 1. Direction, when the direction is not settled

Build three genuinely different layouts rather than one, because layout is a
visual decision and nobody can choose from a description. Vary the structure,
not the palette: the palette is fixed by the brand. For example an editorial
split hero, a full-bleed image hero, and a quiet type-led hero. Publish each as
its own artifact and let the user click through before committing.

Load the `artifact-design` skill (or `/mnt/skills/public/frontend-design`)
before writing any CSS. It is the difference between a branded page and a
templated one.

### 2. Build section by section for anything large

Hero first, approved, then the next section. Building ten sections in one pass
means losing track of which change broke what, and the user cannot give useful
feedback on a wall of new page.

### 3. Look at what you built

You can see. Use it. `scripts/shoot.py` drives the Chromium that is already
installed here and writes screenshots at three viewports, while checking for
horizontal overflow:

```bash
python3 .claude/skills/website-build/scripts/shoot.py site/index.html
```

Read the PNGs, compare against the intent, fix, repeat. Two or three passes
before showing the user produces a far better first version than one blind
attempt. Skip screenshotting sections whose whole point is motion; judge those
in code.

### 4. QA it in a browser before claiming it works

`scripts/shoot.py --qa` clicks every in-page link, opens the mobile menu, tabs
for focus states, and reports anything broken. Fix and re-run until clean.

### 5. Preview, then ship

The preview and the deliverable are two different files, for one specific
reason: the artifact host blocks font CDNs, so a page relying on the Google
Fonts link silently falls back to Times in the preview and the user reviews a
design nobody built.

```bash
python3 .claude/skills/website-build/scripts/embed_fonts.py site/index.html preview.html
```

That inlines the fonts as data URIs under the `Fallback` family aliases the
stylesheet already lists, leaving the deliverable untouched. Publish
`preview.html` as the artifact. Commit `site/index.html`.

Then: commit to the working branch, push, open a draft PR, and hand the file
over for pasting into Kadence.

**Do not deploy theloveadventure.com pages to Vercel or Netlify.** That site is
WordPress on DreamHost behind Cloudflare, and the whole documented plan depends
on WordPress: the blog migration from two old domains, Fluent Forms, the
membership, Stripe, the quiz, Yoast, and Tarisha editing pages herself. A static
deploy creates a second site at a different URL and does not touch
theloveadventure.com. If someone asks for it, say so plainly rather than
building the wrong thing.

This applies to the WordPress site only. A standalone one-pager, a personal
site, or a site for a different business has no WordPress to respect, and a
static host is the right answer there. See `references/quick-builds.md`.

## Editing the live WordPress site

Two things have to be true, and the first is usually the blocker:

1. **Network.** This environment's egress proxy denies unknown hosts. If
   `curl https://theloveadventure.com` returns `CONNECT tunnel failed, 403`,
   the domain is not on the allowlist and no credential will help. The user
   adds it in the environment's settings in Claude Code on the web. Confirm
   with `curl -sS "$HTTPS_PROXY/__agentproxy/status"`, which lists recent
   denials by host.
2. **Credentials.** A WordPress application password, then the REST API at
   `/wp-json/wp/v2/pages`. The Notion checklist tracks whether one exists.

Read before you write, and never bulk-update published pages without showing
the diff first. Do not pull credential pages into context unless a task
actually needs them.

## Conversion work

When asked to make a page convert, these carry the weight: a hero image with a
gradient fallback so a missing file never breaks the layout, a sticky booking
bar, a guarantee, an FAQ that answers the top objections, and a single
dismissible nudge after the pricing.

Two things to push back on, once, before building them:

- **Invented scarcity.** A hardcoded "only 3 slots left this week" on a therapy
  service is a misleading claim under the Fair Trading Act 1986 if it is not
  true. The good news is the genuine version converts better: six couples per
  retreat, fixed dates. "Six places, two remaining for March" is both honest
  and more specific.
- **Small discounts on premium services.** Twenty dollars off a NZ$15,000
  intensive reads as cheapening, and the brand guidelines ban coachy hype.
  Offer early-booking terms, deposit terms, or the free twenty minute call.

State the concern in a sentence or two. If the user still wants it, build what
they asked for.

`references/conversion.md` has the page-by-page tiering, since the full
treatment suits a sales page and would damage a blog or a contact page.

## Never invent proof

Stats, ratings, client counts and testimonials are claims about a therapy
practice. Do not generate them. Use figures from Notion or the repo, and where
a placeholder is genuinely needed, mark it clearly in the handoff so it cannot
reach production by accident. Testimonials in `content/testimonials.json` are
genuine but came from women's workshops, so attribution needs settling before
they appear on a couples page.

## Bundled files

- `scripts/shoot.py` — screenshots at three viewports, overflow check, and a
  `--qa` mode that exercises links, the mobile menu and focus states
- `scripts/check_voice.py` — dashes, banned words, US spellings, plus balance
  and external-resource checks
- `scripts/embed_fonts.py` — inlines Google Fonts as data URIs for previews
- `references/conversion.md` — which pages get which conversion treatment
- `references/quick-builds.md` — standalone sites: a personal one-pager, a site
  for another business, rebuilding a layout from a screenshot. Different rules,
  including deployment
- `references/prompt-pack.md` — the ten founder prompts this skill came from,
  with what changed and why
