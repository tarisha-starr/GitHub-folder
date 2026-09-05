# Homepage audit, and the pre launch checklist

Audit of `site/index.html` as it stood before the rebuild, at 390px, 820px and
1440px, plus a full page pass and a code read. Ranked by visual impact first,
then by severity.

The page is competent. The tokens are correct, the voice check passes clean,
the copy is genuinely good, and it works with JavaScript off. What it is not is
cinematic, and the reasons are mostly compositional rather than technical.

Legend: **P0** rebuild level, **P1** significant, **P2** polish, **P3** hygiene.

---

## The one sentence version

There is not a single photograph on this website. Everything else on this list
matters less than that.

---

## P0. Rebuild level

### 1. No imagery at all
**Impact: highest.** The full page screenshot is nine screens of flat colour
bands. The brand guidelines open with "lead with photography" and name three
buckets: landscape, couples, founders. None of them appear. A retreat in Wanaka
is sold by the light on the mountains, and the site is currently selling it
with a paragraph.

**Fix.** Photographic plates at the hero, the trail section and the closing
invitation, plus a founder portrait and one couples image in the day sequence.
Every `<img>` gets explicit dimensions, `loading` and `decoding`, and a CSS
gradient behind it in the same colours so a missing file degrades to something
handsome instead of a hole. Wired to `images/site/`, ready for the 2026 photos.

### 2. The hero is the generic AI aesthetic
**Impact: highest.** A four stop radial mesh gradient, three blurred drifting
orbs at 72px blur, and a frosted glass card with a white top left sheen. This
exact combination is the most recognisable machine generated look on the web
right now, and it also fights the brand: glass is a cold material and this is a
warm brand.

There is a performance cost on top of the aesthetic one. Three continuously
animating 500px elements with a 72px blur run for as long as the tab is open,
including offscreen, on every phone that loads the page.

**Fix.** Full bleed photograph, house grade gradients, grain. The glass card's
content becomes a slim small caps strip along the bottom edge. Orbs and mesh
deleted entirely.

### 3. Colour proportion is inverted
**Impact: high.** Measured off the full page capture, the page is roughly 75
percent cream and ivory, with two dark bands. The brand names Pine Forest as
the anchor and cream as the background, and the skill notes explicitly that
cream plus a serif plus a terracotta accent is currently a very common
generated look. The way out is proportion.

**Fix.** Move to roughly half dark. Photographic plates count as dark. Target
45 to 55 percent pine and photograph, 40 to 50 percent cream family, under 6
percent terracotta.

### 4. Every section is the same shape
**Impact: high.** Eyebrow, headline, lead, content, in a centred 1180px column,
nine times. Same left edge, same max width, same vertical padding from the same
`--section` token. The eye never travels, so a long page reads as a long
document.

**Fix.** Three composition modes, never the same one twice running: full bleed
plate, asymmetric 7/5 split with vertical offset, and centred measure reserved
for the two moments that earn it. Vary section height deliberately: the quiet
line gets 70vh with one sentence on it, the pillars get more air than the
testimonials.

---

## P1. Significant

### 5. Nine outline icons in circles
The six pillars each have a 44px circle with a 1.4 stroke icon, and the three
streams have another three. That grid is the single clearest signal of a SaaS
template. Several of the icons are also illegible at 21px: the "desire off the
script" flame reads as a smudge, and the "touch before technique" fern reads as
a scribble.

**Fix.** Delete all nine. The six pillars become a numbered editorial list with
the numeral set large in Marcellus and hairline rules between rows. Numbers are
more premium than icons and they cannot be misread.

### 6. The 4.9 rating cannot be supported
The stats band claims a 4.9 average retreat rating while the hero card says
"dates and pricing to be confirmed". If the retreats have not run, there is no
average. `site/README.md` already flags this as unverified.

Beyond the integrity problem, it is a Fair Trading Act 1986 exposure: an
unsubstantiated representation about a service. The other three numbers (five
days, ten couples, two therapists) are facts and are fine.

**Fix.** Remove the rating. Three stats, not four, which also breaks the
four equal column template look. If Tarisha wants social proof in that
position, the honest version is a count of couples seen in the practice, which
she can substantiate.

### 7. Typography does not scale
The hero sits at 80px with `-.016em` tracking, which is loose for Marcellus at
that size, and the section heads at 48px have no tracking adjustment at all.
Marcellus is only available at 400, so the display voice has to come from size
and tracking or it does not come at all.

**Fix.** Tracking tightens as size grows: `-.022em` on the hero, `-.012em` on
section heads, 0 below 24px. Hero line height to 0.98. Keep the optical stroke.

### 8. The navigation is not honest
Every header link points at an on page anchor. `#podcast` is the testimonials
section. `#blog` is the footer element. `#together` and `#for-her` are the two
door cards. Anyone clicking Podcast lands on testimonials.

This is a draft artefact rather than a design decision, but it will reach
WordPress if nobody writes it down.

**Fix.** Point at the real URLs from the site architecture: `/together`,
`/for-her`, `/about`, `/podcast`, `/blog`. They will 404 until those pages
exist, which is the correct behaviour and is visible to whoever is building.

### 9. The founder block is a placeholder that says so
The portrait is a gradient box containing the words "Founder photography to be
supplied". That is fine in a working file and fatal if it reaches production.
It is also the most important trust moment on the page.

**Fix.** Wire to `images/site/tarisha-mark.jpg` with the gradient as the
fallback and no placeholder text. Flag it in the handoff instead.

---

## P2. Polish

### 10. Motion has no choreography
Every revealed element uses the same 20px rise over 800ms with no stagger, so a
six card grid arrives as one slab. There is no header state change on scroll,
no scroll progress, no image treatment, and the only bespoke moment is the
headline swash, which is good and is carrying the whole page on its own.

**Fix.** Distance down to 14px, duration to 760ms, 70ms stagger capped at four
steps, header solidifies past 70vh, 2px terracotta scroll progress line,
photographic drift at 0.18 on desktop only.

### 11. Two competing buttons in the hero
"Book a call" and "See the Wanaka retreat" are near equal weight, and on mobile
they stack as two full width blocks. Two equal choices split the click.

**Fix.** One button. The secondary becomes a quiet arrow link.

### 12. Mobile detail
- The eyebrow wraps to two lines at 390px, which weakens the hero opening.
- One element renders under 12px: the "Wanaka & Queenstown" line under the
  wordmark, at 9px. Too small to read, and it is doing no work.
- There is no sticky Book a call on mobile once the hero is gone.

**Fix.** Shorten the eyebrow to "Couples retreats, Wanaka" on small screens,
lift the brand sub label to 10px or drop it, add the slim sticky bar.

### 13. Vertical rhythm is uniform
Every section uses `--section: clamp(5rem,10vw,9rem)` top and bottom. Nothing
is given more room and nothing is compressed, so nothing feels important.

**Fix.** Three section heights: tight, standard, and a generous variant for the
quiet line and the closing invitation.

### 14. Five links point at `#`
Instagram, TikTok, YouTube, Privacy, Terms. Reported by `shoot.py --qa`.

**Fix.** Real social URLs, `/privacy`, `/terms`.

---

## P3. Hygiene and correctness

### 15. No social or structured metadata
No Open Graph, no Twitter card, no canonical, no JSON-LD. The page will share
to Instagram and Facebook as a bare link with no image, which for a business
that runs on Instagram is a meaningful loss.

**Fix.** OG and Twitter tags with a 1200x630 image, canonical URL, and JSON-LD
for `LocalBusiness` plus `Person` for Tarisha.

### 16. `overflow-x:hidden` on body
This hides horizontal overflow rather than preventing it, so a future layout
bug will be invisible in testing and will still cause a rubber band on iOS.

**Fix.** Remove it and fix any overflow at the source. The screenshot script
checks for this on every run.

### 17. The skip link uses inline event handlers
`onfocus` and `onblur` attributes moving the element with inline styles. It
works, but it fails with JavaScript off, which is the one situation where a
skip link matters most.

**Fix.** Pure CSS, `:focus` moves it into view.

### 18. No `scroll-margin-top` on anchor targets
With a 66px sticky header, every in page jump lands with the heading hidden
behind the header.

**Fix.** `scroll-margin-top: 5.5rem` on all section ids.

### 19. Menu accessibility depends on JavaScript
The mobile menu is a checkbox and label, which is the right pattern for working
without JavaScript, but `aria-expanded` is only ever set from the script, and
the label carries `role="button"` with a manual keydown handler. With
JavaScript off the control has no state exposed to assistive technology.

**Fix.** Keep the checkbox mechanism, drop `role="button"`, and let the CSS
sibling selector do the visual work so the native checkbox semantics remain.

### 20. Dark mode is only partly considered
`.hero`, `.dark` and `.footer` hardcode Pine Deep, so they are correct in dark
mode by accident. `.stats` uses `--ground-alt`, so it flips. The result is
coherent, but it is not deliberate and the next section added will break it.

**Fix.** Route every surface through semantic tokens, including the ones that
happen to be dark in both themes.

---

## Final experience audit, by dimension

| Dimension | State | Severity | Fix |
| --- | --- | --- | --- |
| Visual quality | Clean but templated, no imagery | P0 | Items 1 to 4 |
| Storytelling | Copy is strong, the best line is buried at screen three | P1 | Give "You didn't fall out of love. You fell into logistics." its own screen, high |
| UX | Navigation goes nowhere real | P1 | Item 8 |
| Animation | Present, uniform, uncoreographed | P2 | Item 10 |
| Scroll smoothness | Native and fine. No library, correctly | Pass | Keep it that way, do not add Lenis |
| Responsiveness | No horizontal scroll at any viewport | Pass | Minor items in 12 |
| Accessibility | Skip link, focus rings, reduced motion, works without JS. Better than most | P3 | Items 17 to 19 |
| SEO | Title and description only | P3 | Item 15 |
| Loading speed | No images, so fast. Three animated 72px blurs cost battery | P0 | Removed with item 2 |
| Browser compatibility | `@supports` guards on `backdrop-filter`, sensible fallbacks | Pass | Retest after image work |
| Conversion | Correct Tier 3 restraint. Split hero CTA, no mobile sticky | P2 | Items 11 and 12 |
| Integrity | An unverifiable rating | P1 | Item 6, remove |

---

## Pre launch checklist

Nothing here is optional before the page goes on theloveadventure.com.

### Assets
- [ ] 2026 photography in `images/site/`, exported at 800 / 1400 / 2000 wide
- [ ] Hero image under 220KB at 1400 wide, AVIF with WebP fallback
- [ ] Every image has `alt`, `width`, `height`, `loading`, `decoding`
- [ ] Every image has a gradient fallback that survives a 404
- [ ] Open Graph image at 1200x630
- [ ] Favicon and touch icon from the new brand, not the plum and gold logo in
      `images/brand/`, which is the previous brand

### Copy and claims
- [ ] `check_voice.py` clean: no dashes, no US spellings, "real" only where it
      is carrying weight
- [ ] No unverifiable statistic anywhere. The 4.9 rating is out until it exists
- [ ] Testimonial attribution settled. The ones in `content/testimonials.json`
      came from women's workshops, so they need consent and correct attribution
      before they appear on a couples page
- [ ] No invented scarcity. Genuine numbers only: ten couples, fixed dates
- [ ] Session and offer names pass the say it out loud test. "The Second Spring
      Session" on `therapy.html` does not; "Get the Love You Desire" did

### CTAs and conversion
- [ ] Every CTA resolves to a working URL or booking link
- [ ] The twenty minute call is the single primary action on the homepage
- [ ] Mobile sticky Book a call appears after the hero and not before
- [ ] Homepage stays Tier 3: no countdown, no discount band, no exit nudge

### Performance
- [ ] LCP under 2.0s on 4G, and the LCP element is the hero photograph
- [ ] CLS under 0.02
- [ ] Total page weight under 1.2MB
- [ ] JavaScript under 8KB, no libraries, no CDN scripts
- [ ] No animated blur or filter anywhere
- [ ] Below fold images lazy loaded

### Accessibility
- [ ] Keyboard through the entire page, focus visible at every stop
- [ ] Contrast checked against the darkest gradient stop for all type on photos
- [ ] One `h1`, no skipped heading levels
- [ ] `prefers-reduced-motion` gives a complete static page, with the scroll
      effects never starting rather than starting and being overridden
- [ ] Page fully readable and navigable with JavaScript disabled
- [ ] Tap targets 44px on everything people tap

### Cross browser
- [ ] Safari on iOS, including the sticky header and `100vh` behaviour with the
      address bar, using `100svh`
- [ ] Chrome on Android, mid range device, checking scroll smoothness
- [ ] Safari and Chrome on desktop
- [ ] Firefox, which handles `backdrop-filter` and `text-stroke` differently
- [ ] Dark mode and light mode in each

### SEO
- [ ] Title under 60 characters, description under 155
- [ ] Canonical URL set
- [ ] Open Graph and Twitter cards, verified in a preview tool
- [ ] JSON-LD for `LocalBusiness` and `Person`
- [ ] `lang="en-NZ"`
- [ ] Yoast configured on the WordPress page after pasting

### Analytics
- [ ] Analytics installed and firing on the live page
- [ ] Book a call tracked as a conversion event
- [ ] Scroll depth on the homepage, so the drop off point is known
- [ ] Consent handling appropriate for NZ and any EU traffic

### Deployment
- [ ] Pasted into the matching Kadence page. Not Vercel, not Netlify
- [ ] Fonts loading on the live site, not falling back to Times
- [ ] 301 redirects from both old domains active and tested
- [ ] Forms wired to Fluent Forms and tested end to end, including the
      confirmation email
- [ ] `tarisha@theloveadventure.com` exists and receives mail
- [ ] Tested on the live URL, not just locally
