# The Love Adventure, cinematic creative direction

Direction, experience architecture, hero design, motion system and build
sequence for theloveadventure.com.

Constraints this works inside, from Notion (Assets & Ops → Website Build) and
the `website-build` skill: Soft Autumn palette with Pine Forest as the anchor,
Marcellus at weight 400 only, Lora for body, UK English, no dashes as
punctuation, terracotta held under 10 percent of any page, one self contained
HTML file per page because the destination is a Kadence block in WordPress.

---

## 1. The creative concept

### The idea: The Long Light

In the deep south of New Zealand the evening light does not fall, it lingers.
Six o'clock, eight o'clock, still gold on the tops. Anyone who has stood on a
ridge above Wanaka in February knows the feeling: the day is not ending, it is
opening out.

That is the whole brand argument in one image. A marriage at year twenty is not
a day ending. It is the long light. The deepest love is still ahead of you.

Everything on this site is built from that single visual idea, which gives the
work three things a generic luxury treatment cannot give it:

- **A reason for the palette.** Pine Forest is the shadow side of an alpine
  evening. Camel and Antique Gold are the light on the tussock. Terracotta is
  the sun itself, which is why it is rare and why it is always the thing you
  are meant to touch.
- **A reason for the pacing.** Long light means slow. Nothing on this site
  snaps, bounces or springs. Everything moves at walking pace.
- **A reason for the photography.** One hour of the day, shot again and again.
  That is what makes mixed source imagery read as a single production.

### The visual narrative, in five acts

The homepage is not a list of sections. It is a walk, and the reader should
feel the ground change under them.

| Act | Feeling | Ground | Where the reader is |
| --- | --- | --- | --- |
| 1. Arrival | Held, recognised | Photograph, dark | On the sand, before anything is asked of them |
| 2. Recognition | Seen, slightly winded | Cream, quiet | Sitting with the sentence they have not said out loud |
| 3. The work | Steadied, curious | Cream and ivory, structured | Being shown how it is done, plainly |
| 4. The people | Warm, trusting | Photograph, dark | Meeting Tarisha and Mark |
| 5. The invitation | Ready | Photograph into pine | Asked, once, gently |

The rhythm is **dark, light, light, dark, dark**. Photographic plates are the
punctuation. Cream sections are the breath between them. A reader scrolling
fast should still feel that shape.

### What this is not

Named, because these are the defaults that will creep back in:

- Not glassmorphism. No frosted cards, no blurred orbs drifting behind a mesh
  gradient. That is the current homepage and it is the most recognisable AI
  generated look on the web right now.
- Not a SaaS landing page. No three column feature grid with circle icons above
  each heading. No "trusted by" logo wall.
- Not a wellness template. No mandala motifs, no watercolour blobs, no lotus.
- Not luxury by way of emptiness. Enormous white space and a thin sans serif is
  the other cliché. This brand is warm, and warm needs material.

### Art direction

**Photography leads. Always.** The single biggest gap between the current site
and a studio build is that there is not one photograph on it. Nine screens of
flat colour is not cinematic, whatever the type is doing.

**What we actually have: the 2026 shoot.** Tarisha and Mark on the west
Auckland black sand coast, Piha, with Lion Rock and the conglomerate cliffs.
This is better raw material than the brief assumed, and it changes one thing:
the site's landscape is coastal, not alpine. Black sand, sea mist, hard rock,
warm light. So the retreat locations get named in words, in the strip and the
copy, and the photography carries mood and the founders rather than pretending
to be Wanaka. Lion Rock is recognisable to any New Zealander, so a Wanaka
caption over it would read as a mistake rather than as art direction.

The four frames the homepage uses, and why, are in `images/site/README.md`.

The buckets, per the brand guidelines, now read:

- **Coast and landscape.** Piha and the Auckland west coast for brand and mood.
  Wanaka and Queenstown when there is a retreat shot to use. Sea mist, long
  light, wide horizons.
- **Couples.** Backs to camera, walking, hands held. Never the stock "look how
  happy we are" shot. The backlit frame of the two of them walking out of the
  sea cave is exactly this and it is the best argument the site can make.
- **Founders.** Tarisha and Mark outdoors, unposed, laughing. Not studio, not
  against a white wall. There are several usable frames.

One note on the set: the teal and red dresses are outside the Soft Autumn
palette. The house grade below pulls them back into it, which is precisely what
the grade is for. Do not reshoot, and do not pre grade the exports.

**The grade.** Every photograph on the site passes through the same treatment
so a mixed shoot reads as one production:

```css
/* the house grade: pine in the shadows, gold in the highlights */
.plate img{ filter:saturate(.92) contrast(1.04) brightness(.97); }
.plate::after{
  content:"";position:absolute;inset:0;
  background:
    linear-gradient(180deg,rgba(31,44,31,.62) 0%,rgba(31,44,31,.12) 38%,rgba(31,44,31,.86) 100%),
    linear-gradient(94deg,rgba(31,44,31,.55) 0%,rgba(31,44,31,0) 62%);
  mix-blend-mode:normal;
}
```

Two gradients, not one. The vertical one buys legibility top and bottom. The
horizontal one anchors the type to the left edge and is what makes it look art
directed rather than captioned.

**Grain.** A very fine static grain over photographic plates, at 3 to 4 percent
opacity, as an inline SVG `feTurbulence` rasterised once into a repeating
background. Never animated. This is what separates a web photograph from a
printed one, and it costs nothing.

### Typography

Marcellus ships at 400 and nothing else, so weight has to come from size,
tracking and optical stroke rather than from a heavier file.

| Role | Font | Size | Tracking | Notes |
| --- | --- | --- | --- | --- |
| Hero | Marcellus 400 | `clamp(2.9rem, 7.2vw, 6.25rem)` | `-.022em` | line height 0.98, `-webkit-text-stroke:.4px` |
| Section head | Marcellus 400 | `clamp(2rem, 4.6vw, 3.25rem)` | `-.012em` | line height 1.08 |
| Sub head | Marcellus 400 | `clamp(1.25rem, 2.1vw, 1.6rem)` | `0` | |
| Lead | Lora 400 | `clamp(1.15rem, 1.7vw, 1.4rem)` | `0` | line height 1.55, max 46ch |
| Body | Lora 400 | 17px desktop, 16px mobile | `0` | line height 1.68, max 62ch |
| Pull quote | Lora **italic** 400 | `clamp(1.4rem, 2.6vw, 2rem)` | `.005em` | italic carries the emotion, never bold |
| Eyebrow | Lora 600 | 12px | `.18em` | uppercase, preceded by a 26px gold rule |

Three rules that do most of the work:

1. **Tighter as it gets bigger.** Marcellus at 100px with default tracking looks
   like a Word document. Every step up in size takes tracking down.
2. **Italic is the emphasis, never bold.** Lora italic in a lead paragraph is
   the brand's single most recognisable typographic move. Use it on the phrase
   that carries the feeling, not on keywords.
3. **One display face per screen.** If a section has a big Marcellus headline it
   does not also get a Marcellus sub head. Drop to Lora.

### Colour, in proportion

The palette is fixed. What is not fixed, and what decides whether this looks
branded or templated, is the proportion.

Target for the homepage as a whole:

- Pine Deep and photographic dark: **45 to 55 percent** of vertical surface
- Cream, Ivory, Paper: **40 to 50 percent**
- Terracotta: **under 6 percent**, and only on things you can click
- Camel and Antique Gold: hairlines, eyebrow rules, icon strokes, small caps

The current site is roughly 75 percent cream, which is why it reads light and
generic. Anchoring in pine and letting cream be the relief is the single
cheapest change with the biggest effect.

Terracotta discipline: primary buttons, one accent word per screen at most, and
nothing else. If terracotta appears in a heading and on a button in the same
viewport, remove it from the heading.

### Materials, lighting, depth

The material vocabulary is **paper, stone and light**. Not glass.

- **Paper.** Cards are Paper `#FDFBF5` on Cream, separated by a 1px gold
  hairline at 30 percent and a shadow that is almost entirely a long soft
  ambient, no hard edge: `0 1px 2px rgba(31,44,31,.05), 0 24px 48px -20px rgba(31,44,31,.20)`.
- **Stone.** Dark sections are flat Pine Deep with a barely visible vertical
  gradient, no texture. They are the wall the photographs hang on.
- **Light.** Depth comes from photographic depth of field, not from blur
  filters. A plate with a foreground subject and a soft background does more
  for perceived depth than any amount of CSS.

**Layer stack on a photographic section**, back to front: photograph, house
grade gradients, grain, type, then one element that **breaks the plate edge**
(a card overlapping the boundary between plate and cream by 40 to 80px). That
overlap is the most reliable trick in editorial layout for making a page feel
composed rather than stacked, and it costs one negative margin.

### Composition

Kill the single centred 1180px column. The page needs three composition modes
and should never use the same one twice in a row:

1. **Full bleed plate.** Edge to edge photograph, type on a 12 column grid
   placed at columns 1 to 6 or 2 to 7, sitting low.
2. **Asymmetric split.** 7 / 5 or 5 / 7, photograph on one side, text on the
   other, with the two at different vertical offsets so the eye travels.
3. **Centred measure.** Reserved for the one or two moments that deserve it:
   the recognition paragraph and the closing invitation. Max 62ch, generous
   space above and below, nothing else on screen.

Grid: 12 columns, 24px gutters, `clamp(1.25rem, 5vw, 3rem)` page margin, max
content width 1240px, plates full bleed.

### The emotional experience

If a woman in her fifties opens this on her phone at 11pm, in bed, next to a
husband who is already asleep, the page has about four seconds. In order:

1. **Recognition before persuasion.** The first thing she reads should describe
   her marriage, not the product. "You didn't fall out of love. You fell into
   logistics." is the strongest line on the current site and it is buried at
   screen three. It belongs much earlier.
2. **Relief, not shame.** Nothing on this page may imply she let it happen.
3. **Competence.** Two therapists, EFT, sex therapy, named. Warmth without
   credentials reads as a coach. Credentials without warmth reads as a clinic.
4. **A small, safe first step.** A twenty minute call is the ask. Not a
   NZ$15,000 intensive, not a five day retreat. Everything funnels to the call.

---

## 2. The experience, first second to final CTA

### Load, 0 to 1200ms

No loading screen. A luxury site is one that is already there. A percentage
counter on a therapy practice website is theatre and it costs a second of
attention for nothing.

What happens instead:

| Time | Event |
| --- | --- |
| 0ms | HTML paints. Pine Deep ground, hero gradient fallback, headline visible in fallback serif. No flash of white, ever. |
| ~100ms | Hero photograph decodes (`fetchpriority="high"`, `loading="eager"`) and cross fades in over 900ms from `opacity:.001` to `1`. |
| ~150ms | Fonts land. `font-display:swap` with Georgia as the metric fallback, so the reflow is small. |
| 200ms | Headline lines begin their mask reveal, staggered 90ms apart. |
| 620ms | Sub head fades up. |
| 780ms | Buttons fade up. |
| 1000ms | The facts strip and scroll cue arrive last. |

Total choreography under 1.3 seconds, and every single element is legible from
0ms if JavaScript never runs. The animation is a polish layer over a page that
already works.

### The scroll sequence

**1. Hero. `100svh`, capped at `900px` on tall screens.**
Full bleed Piha plate. Headline low left. One primary CTA plus a quiet arrow
link. Facts strip along the bottom edge. See section 3.
Goal: recognition plus one click on Book a call.

**2. The quiet line. Cream, `62vh`, one sentence.**
The transition out of the hero is a single centred sentence in Marcellus on
cream, with nothing else on screen:

> You didn't fall out of love. You fell into logistics.

This is the whole site's hinge. Giving it its own screen is the most confident
thing the page can do and it is free.

**3. Recognition. Cream, indented measure.**
Four short paragraphs, Lora, 62ch, the italic doing the emotional work. Indented
from the left rather than centred, because the quiet line above it is already
centred and two centred blocks running together read as a brochure. The first
paragraph steps up in size and takes the Pine headline colour, so the section
has a top note. Ends on "So we walk," which hands straight to the next section.
Goal: she thinks, that is us.

**4. Plate: the trail. Full bleed photograph, dark.**
The two of them walking hand in hand out of the sea cave, backlit. Type at left,
low. Three streams named: EFT, sex therapy, adventure, as hairline ruled columns
rather than icon cards. This is the "why we are different" moment and it should
land as an image first and words second.
Goal: differentiation.

**5. Two doors. Ivory, asymmetric.**
Together and For Her. Two cards, but not twins: Together is the larger card and
leads, For Her sits lower and narrower. Equal weight signals a menu. Unequal
weight signals a recommendation with an alternative.
Goal: route without losing anyone.

**6. What shifts. Cream, editorial list, sticky heading.**
The six pillars, but not as a three by two icon grid. The heading sticks in the
left column while the numbered list travels past it on the right. Numerals set
in Marcellus in Antique Gold, hairline rules between rows, icons removed
entirely. Six circle icons is the SaaS tell. On mobile the heading unsticks and
the list stacks under it.
Goal: substance.

**7. Tarisha and Mark. Pine Deep, asymmetric split, photograph.**
Portrait at 5 columns, offset low. Text at 7 columns. The pull quote in Lora
italic, oversized, breaking out of the text column to the left by 3.5rem on wide
screens. Dark ground, because it is the only way to stop the middle of the page
running four light sections together.
Goal: trust in the people.

**8. In their words. Ivory, three cards.**
Testimonials. Keep them plain. Fancy testimonial treatments read as marketing
and reduce believability.
Goal: proof.

**9. The invitation. Plate, `78vh`.**
Closing photograph, the two of them on the black sand. One button, Book a call.
The secondary is a quiet arrow link, not a second button.
Goal: the one conversion that matters.

**10. Footer. Pine Deep.**
Four columns per the site architecture. Newsletter line, socials, legal.

**Band rhythm.** Dark, light, light, dark, light, light, dark, light, dark,
dark. No more than two light sections ever run together, which is the rule that
keeps a long page feeling composed. Check it on a zoomed out full page capture
before shipping any change to section order.

### Persistent elements

- **Header.** Transparent over the hero, no border. On scroll past 70vh it
  gains a Pine Deep background at 92 percent and a gold hairline, in a 240ms
  fade. Never a hard swap.
- **Book a call** stays in the header from the moment the header solidifies.
- **Mobile sticky bar.** Below 900px, once past the hero, a slim bottom bar
  with Book a call. Tier 3 pages like the homepage get this and nothing more
  aggressive: no countdown, no exit nudge. That is in the conversion reference
  and it is right.
- **Scroll progress.** A 2px terracotta line at the top of the viewport. Cheap,
  and it makes a long page feel navigable.

### Responsiveness

Three real breakpoints, not five:

- **Under 720px.** Single column. Plates go to 4:5 portrait crops with the
  focal point held by `object-position`. Pinned sections unpin and stack.
  Horizontal scrollers become vertical.
- **720 to 1080px.** Two columns where it helps. Splits stay stacked but gain
  offsets.
- **Over 1080px.** Full 12 column grid, asymmetric splits, pinning enabled.

Test at 390px every pass. Nothing scrolls sideways, ever.

### Accessibility, non negotiable

- Every plate has a text alternative, and decorative grain is `aria-hidden`.
- Contrast: body text on cream is Warm Charcoal, which passes. Cream on
  photographs is only safe because of the grade gradients, so every type on
  photo case is checked against the darkest gradient stop, not against the
  photograph.
- Focus rings visible everywhere, 2px terracotta with 3px offset.
- The page is fully readable and fully navigable with JavaScript off.
- `prefers-reduced-motion` removes all transforms and parallax and leaves a
  clean, static, complete page.
- Headings are a true hierarchy, one `h1`, no skipped levels.
- Tap targets 44px minimum on the things people tap.

### Performance budget

| Metric | Budget |
| --- | --- |
| LCP (hero photograph) | under 2.0s on 4G |
| CLS | under 0.02, so every image gets explicit `width`, `height` or `aspect-ratio` |
| INP | under 150ms |
| Hero image weight | under 220KB, AVIF with a WebP fallback, `srcset` at 800 / 1400 / 2000 |
| Total page weight | under 1.2MB including all photography |
| JavaScript | under 8KB, no libraries |

The performance rule that matters most here: **the hero photograph is the only
thing that loads eagerly.** Everything below the fold is `loading="lazy"` and
`decoding="async"`.

---

## 3. The signature hero

### The scene

`hero-piha.jpg`. Tarisha standing on the wet rock shelf at Piha, Mark behind
her with his arms around her, both looking out to sea. Surf breaking on the
left, sea mist rolling in, Lion Rock behind. They occupy maybe eight percent of
the frame.

That scale is the whole point. A big smiling couple is a stock photograph. Two
small figures in a large landscape is a feeling, and the feeling is exactly the
one the brand sells: the thing in front of you is bigger than the thing behind
you. The frame already has the type space built into it, on the left, over the
water.

It also means the founders are the hero image, which for a therapy practice is
the strongest possible opening. You are not selling a venue. You are selling
two people who know what they are doing.

Never a couch, never indoors, never a white background.

### Composition

Desktop, 12 column grid:

```
┌─────────────────────────────────────────────────────────┐
│  [transparent header, logo left, nav right, CTA]        │
│                                                          │
│                                                          │
│                        (sky, negative space, the light)  │
│                                                          │
│                                                          │
│  ── COUPLES RETREATS AND THERAPY                        │  cols 1-6
│                                                          │
│  The deepest love is                                     │  cols 1-7
│  still ahead of you.                                     │
│                                                          │
│  Therapy that walks. Five days in alpine country,        │  cols 1-5
│  with the depth work most retreats keep indoors.         │
│                                                          │
│  [ Book a call ]   See the Wanaka retreat →              │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│  FIVE DAYS · TEN COUPLES · WANAKA & QUEENSTOWN  ↓ scroll │  full width strip
└─────────────────────────────────────────────────────────┘
```

Type sits in the **bottom 45 percent**. The top half is sky and light and
nothing else. Resisting the urge to fill it is what makes it look expensive.

The floating glass card in the current hero goes. In its place, the retreat
facts become a slim full width strip along the bottom edge, in small caps with
gold dividers. Same information, one tenth of the visual noise, and it doubles
as the boundary between the hero and the next section.

Mobile: same structure, headline drops to `clamp(2.6rem, 11vw, 3.4rem)`, sub
head to two lines maximum, one button (Book a call) with the secondary as a
text link beneath, strip wraps to two lines.

### Copy

**Eyebrow:** COUPLES RETREATS AND THERAPY

Short on purpose. It wrapped to two lines at 390px at any greater length,
which weakens the opening. The locations live in the strip instead.

**Headline:** The deepest love is *still ahead* of you.

Keep it. It is the brand tagline, it is plain, and a woman would say it out
loud. "Still ahead" in Lora italic Camel, with the hand drawn terracotta swash
beneath. The swash is the one decorative flourish the site gets, which is why
it works.

**Sub head:** Therapy that walks. Five days in alpine country with two
therapists, doing the depth work most retreats keep indoors.

One sentence tighter than the current version, and it puts the number of days
and the number of therapists into the first screen where they do the most work.

**Primary CTA:** Book a call
**Secondary:** See the Wanaka retreat, as a text link with an arrow, not a
bordered button. Two buttons of near equal weight in a hero splits the click.

**Strip:** FIVE DAYS · TEN COUPLES, NEVER MORE · WANAKA AND QUEENSTOWN

The locations belong here rather than in the eyebrow, because the hero
photograph is Piha and a Wanaka label directly over it would read as a caption
on the image.

### Entrance

```
0ms     photograph at opacity .001, scale 1.06
100ms   photograph cross fades and settles to scale 1 over 1400ms
        (the settle is the cinematic beat: the image arrives already moving
         and comes to rest, it does not slide in)
200ms   eyebrow rule draws left to right, 320ms
280ms   headline line 1, mask reveal upward, 720ms
370ms   headline line 2, same, 720ms
620ms   swash draws under "still ahead", 1050ms, once, then stays
700ms   sub head fades and rises 12px
820ms   buttons fade and rise 10px, together
1000ms  bottom strip fades, scroll cue begins its slow pulse
```

Everything uses `cubic-bezier(.22,.61,.36,1)`. Nothing overshoots.

### Cursor interactions, desktop only

Restrained to two, both cheap:

1. **Plate parallax.** The photograph translates up to 10px against pointer
   position, on a `transform` only, `will-change:transform`, rAF throttled.
   Ten pixels. Anything more and it reads as a gimmick.
2. **Button warmth.** The primary button's shadow deepens and the label letter
   spacing opens by `.01em` over 300ms on hover. Very small, felt more than
   seen.

No custom cursor. No magnetic buttons. No trailing dot. These are the 2021
agency reel signatures and they now read as dated, plus they break for anyone
using a trackpad with reduced pointer precision. Skipped on touch devices and
under `prefers-reduced-motion` and when `(hover:none)`.

### Scroll behaviour out of the hero

As the hero leaves, three things happen on one timeline driven by scroll
position from 0 to 70vh:

- The photograph translates up at 0.18 of scroll speed, so the ridge line
  drifts slowly. Not a full parallax, a drift.
- Hero type translates up at 1.0 and fades from 1 to 0 between 25 and 60vh, so
  the words dissolve into the landscape rather than scrolling off it.
- The header background fades in from 60 to 75vh.

On mobile the drift is disabled. Scroll linked transforms on a phone cost more
than they give.

### Performance guard

The hero must hold LCP under 2 seconds. That means: the photograph is the LCP
element and is preloaded in the head, `fetchpriority="high"`; a gradient in the
same colours paints instantly behind it so there is never a white or empty
frame; the headline is in the HTML, not injected. If the image 404s, the
gradient alone is a complete and handsome hero. That fallback is a hard
requirement, not a nicety, because the photography is not in the repo yet.

---

## 4. The motion system

### Principles

1. **Walking pace.** Every duration between 300 and 900ms. Nothing snaps.
2. **Two curves, not eight.**
   - `--ease: cubic-bezier(.22,.61,.36,1)` for entrances and anything that
     arrives. Fast out, long settle.
   - `--ease-soft: cubic-bezier(.4,0,.2,1)` for state changes, hovers, colour.
   - No bounce, no elastic, no `back` curves anywhere on this site.
3. **Transform and opacity only.** No animated blur, no filter animation, no
   turbulence, no blend mode animation, no marquees. This is a rule from the
   build constraints and it is also just correct: everything else drops frames
   on the mid range Android a lot of the audience is holding.
4. **Motion is a layer, never a dependency.** Every element is fully visible
   and correctly positioned before any script runs.
5. **Once.** Reveals fire once and unobserve. Elements that re animate every
   time you scroll past them feel cheap and make a page tiring.

### The timing table

| Movement | Distance | Duration | Delay / stagger | Curve |
| --- | --- | --- | --- | --- |
| Section reveal | 14px up | 760ms | 0 | `--ease` |
| Grouped items | 14px up | 700ms | 70ms stagger, max 4 steps | `--ease` |
| Headline line mask | 100% up | 720ms | 90ms per line | `--ease` |
| Rule draw | scaleX 0 to 1 | 420ms | 0 | `--ease` |
| Swash draw | dashoffset | 1050ms | 400ms, once | `--ease` |
| Image cross fade | opacity + scale 1.05 to 1 | 1200ms | 0 | `--ease` |
| Card hover lift | 4px up | 340ms | 0 | `--ease-soft` |
| Button hover | shadow + 2px | 300ms | 0 | `--ease-soft` |
| Header solidify | opacity | 240ms | 0 | `--ease-soft` |
| Nav underline | scaleX | 300ms | 0 | `--ease-soft` |
| Mobile menu | opacity + 8px | 280ms | 40ms per item | `--ease` |

The stagger cap at four steps matters. A six item stagger at 70ms means the
last item arrives 420ms after the first, and by then the reader has moved on.
Group into fours and reset.

### Smooth scrolling

**Do not add a smooth scroll library.** Lenis, Locomotive and their relatives
hijack the scroll thread, break `Ctrl+F`, fight iOS momentum, add 15 to 30KB,
and are the single most common reason a "cinematic" site feels worse to use
than a plain one. Native scrolling on a modern browser is already smooth.

What we use instead:

- `scroll-behavior:smooth` on `html` for in page anchors only, disabled under
  reduced motion.
- `scroll-margin-top` on every anchor target so the sticky header does not
  cover the heading it just jumped to.
- Scroll driven effects read from a single rAF loop that batches all reads then
  all writes, so nothing thrashes layout.

### Scroll choreography

Three techniques, used sparingly:

**Reveal on enter.** IntersectionObserver at `rootMargin: 0px 0px -10% 0px`.
Adds `.in`. Unobserves. This is 90 percent of the motion on the site.

**Drift.** Photographic plates translate against scroll at 0.15 to 0.2, capped
at 60px total travel. Desktop only. This gives depth without the seasick
feeling of a true 0.5 parallax.

**Stick.** Exactly one sticky section: the "six things that shift" heading,
which holds in the left column while the numbered list travels past it.
`position:sticky` on a grid child, no scroll hijack, so the scrollbar stays
honest and the user can flick past it. It unsticks below 1000px.

The first draft of this direction called for a pinned, horizontally scrolling
five days sequence. It was cut, for two reasons. There is no approved copy for a
day by day itinerary, and inventing one would be inventing product detail about
a retreat that has not run. And a sticky column delivers the same feeling of a
scene holding while content moves through it, with none of the risk that a
pinned section fights the user on a trackpad. A pinned section that fights the
user is worse than no pinned section.

**What we do not do:** scroll snapping on a long page, scroll jacked full page
sections, horizontal scroll for anything other than the day sequence, or text
that animates letter by letter. Letter by letter reveals on a paragraph are
unreadable and they hurt anyone using a screen reader on a live region.

### Scene transitions

Between a cream section and a photographic plate, the transition is the
composition, not an effect: the card that breaks the plate edge, or a hairline
rule that runs from the last section into the first, or the plate's top
gradient starting in exactly the cream the section above ends in. Cross fading
whole sections into each other is the thing that makes sites feel slow.

### Hover and micro interactions

- **Cards.** 4px lift, shadow deepens. That is all. No border colour flash, no
  scale, no icon spin.
- **Links.** Underline draws from the left over 300ms.
- **Arrow links.** The arrow translates 4px right. Keep it.
- **Buttons.** Shadow deepens, 2px lift, letter spacing opens `.01em`.
- **Images in a split.** 1.03 scale over 700ms inside a fixed overflow hidden
  frame. Slow enough to be a mood, not a zoom.
- **Nav.** Camel underline scales in from the left.

Every one of these is under 350ms and none of them moves anything the user is
trying to click.

### Reduced motion

The reduced motion build is not a degraded site, it is the same site standing
still:

```css
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{
    animation-duration:.001ms !important;
    animation-iteration-count:1 !important;
    transition-duration:.001ms !important;
  }
  .reveal{opacity:1 !important;transform:none !important}
  .plate img{transform:none !important}
}
```

And in JavaScript, the drift loop, the pin and the pointer parallax all check
`matchMedia('(prefers-reduced-motion: reduce)')` and simply never start. Not
"run and then get overridden", never start.

---

## 5. The build sequence

Adapted to this project's actual pipeline. There is no npm, no bundler and no
Vercel: every page is one self contained HTML file with inline CSS and inline
JavaScript, because the destination is a Kadence block in WordPress on
DreamHost. The Google Fonts stylesheet is the only external resource.

Work in this order, and screenshot and QA between every stage.

**Stage 0. Look at what exists.**
Read `site/index.html` end to end. Screenshot it at 390, 820 and 1440. Do not
start from a blank file: the token block, the voice, the copy and the
accessibility scaffolding in the current page are sound and should survive.
What changes is composition, imagery and motion.

**Stage 1. Foundations.**
Token block: palette, semantic tokens, type scale, spacing scale, two easing
curves, radii, shadows. Grid primitives. Reset. Light and dark themes and the
reduced motion block, written now rather than bolted on later.
*Test:* the page renders with correct colour in light, dark and system themes.

**Stage 2. Asset pipeline.**
Create `images/site/`. Define the filenames the page will reference before the
photographs exist, so dropping them in is a copy and nothing else. Every
`<img>` gets `width`, `height`, `loading`, `decoding`, `alt`, and a CSS
gradient behind it in the same colours so a missing file never breaks a layout.
*Test:* delete every image file. The page still looks deliberate.

**Stage 3. Header and footer.**
Transparent to solid header, mobile menu that works without JavaScript, skip
link, footer per the site architecture.
*Test:* `shoot.py --qa`. Menu opens, focus is visible, no dead links.

**Stage 4. The hero.**
Section 3 of this document, in full. Build the static version first and confirm
it is beautiful before adding a single frame of animation.
*Test:* screenshot at three viewports, check with the image file removed, check
LCP element is the photograph.

**Stage 5. Sections, one at a time, in scroll order.**
Quiet line, recognition, two doors, what shifts, the trail plate, the five
days, the founders, testimonials, the invitation. Build, screenshot, fix, then
move on. Never build three sections before looking at any of them.
*Test after each:* 390px has no horizontal scroll, the section reads correctly
with JavaScript off.

**Stage 6. Motion.**
Add the reveal observer, then drift, then the pin, in that order, checking
performance after each. Reduced motion checked at every step, not at the end.
*Test:* toggle `prefers-reduced-motion` and confirm a complete static page.

**Stage 7. Conversion layer.**
Homepage is Tier 3 in the conversion reference: hero image and motion only,
plus the mobile sticky Book a call bar. No countdown, no discount band, no exit
nudge. Those belong on the Wanaka sales page.
*Test:* every CTA resolves. No invented scarcity anywhere.

**Stage 8. SEO and metadata.**
Title under 60 characters, description under 155, Open Graph and Twitter cards
with a real image, canonical URL, `lang="en-NZ"`, and JSON-LD for
`LocalBusiness` plus `Person` for Tarisha. Heading hierarchy verified.
*Test:* one `h1`, no skipped levels, structured data validates.

**Stage 9. Voice gate.**
`python3 .claude/skills/website-build/scripts/check_voice.py site/index.html`.
Dashes, banned words, US spellings, including inside the `<title>`.
*Test:* clean, or every flag consciously accepted and noted.

**Stage 10. Full QA.**
`shoot.py --qa` clean. Keyboard through the whole page. JavaScript off. Dark
mode. 390px. Then the preview: `embed_fonts.py` into `preview.html`, publish
that as the artifact, because the artifact host blocks font CDNs and an
un inlined preview silently falls back to Times.

**Stage 11. Ship.**
Commit `site/index.html`, push the branch, open a draft PR, then paste the file
into the matching Kadence page in WordPress. Not Vercel, not Netlify. The
documented plan depends on WordPress for the blog migration, Fluent Forms, the
membership, Stripe, the quiz, Yoast, and for Tarisha to edit her own pages.

**Stage 12. Roll out.**
Once the homepage is approved, the tokens, header, footer and motion system
become the kit for `/together`, `/together/therapy`, `/about` and the Wanaka
sales page. Those pages should take a fraction of the time, because the system
already exists.
