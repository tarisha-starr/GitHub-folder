# Wild Sky Coffee — SEO Pack

The site is almost invisible to search right now for one blunt reason: the
homepage title tag is `Wild Sky Coffee` and nothing else. Nobody is searching for
a brand they haven't heard of. Everything below is about being findable for what
people *are* searching for — titanium camping mugs, camping coffee gear, a
Timemore grinder in New Zealand.

No keyword volumes here on purpose. Pull the actual numbers from Google Keyword
Planner and Search Console rather than taking anyone's word for them, including
mine.

---

## 1. Title tags and meta descriptions — every page

Shopify: **Online Store → Pages / Products / Collections → Edit website SEO.**
Titles under about 60 characters, descriptions under about 155.

| Page | Title tag | Meta description |
|---|---|---|
| Home | `Titanium Camping Coffee Gear, Designed in New Zealand \| Wild Sky Coffee` | `Ultralight titanium coffee gear for hiking, biking and camping. Cups, presses, pots and kits from $14. Designed in NZ. Free shipping across New Zealand.` |
| Coffee Gear | `Titanium Camping Coffee Gear — Made for the Trail \| Wild Sky Coffee` | `Ultralight titanium coffee gear designed in the New Zealand backcountry. Cups, presses, pots and kits from $14. Free shipping across New Zealand.` |
| Cups (once filled) | `Titanium Camping Cups & Mugs — 45g to 85g \| Wild Sky Coffee` | `Single and double-wall titanium camping cups from 45g. Compare capacity, weight and warmth, and pick the one that suits your trips.` |
| Coffee makers | `Titanium Coffee Press & Camping Coffee Makers \| Wild Sky Coffee` | `A 750ml titanium coffee press built for the trail, plus the pot, scoop and storage to go with it. Designed in New Zealand, free NZ shipping.` |
| Kits (new) | `Camping Coffee Kits — Everything for a Brew on the Trail` | `Complete titanium coffee kits for the trail, the hut and slow mornings at the tent. Weighed, photographed and priced as a set.` |
| Gifts (new) | `Gifts for People Who Love Coffee and the Outdoors \| Wild Sky Coffee` | `Presents for trampers, bikers and campers who take their coffee seriously. Under $30, around $60, or the full kit. Free NZ shipping.` |
| Our Story | `Our Story — Mark and Tarisha, Wild Sky Coffee New Zealand` | `We're Mark and Tarisha, based in Auckland. We make titanium coffee gear we use ourselves, on our own trips. Here's why we started Wild Sky Coffee.` |
| Contact | `Contact Wild Sky Coffee — Auckland, New Zealand` | `Questions about gear, an order or shipping? We're in Auckland and we answer our own email. Get in touch.` |
| FAQ (new) | `FAQs — Titanium Coffee Gear, Shipping and Returns` | `Which cup to choose, why titanium, how to brew on a camp stove, shipping to NZ and Australia, and our 30-day returns.` |
| Brew guide (new) | `How to Make Good Coffee on a Camp Stove` | `The dose, grind, ratio and timing for a proper coffee outdoors — with a titanium press, a 15g scoop and four minutes.` |
| Blog index | `Coffee and Adventure — Trips, Routes and Brew Notes` | `Trips, routes and coffee from the New Zealand outdoors. Where we've been, what was in the pack, and how the brew turned out.` |

Product titles and descriptions are in `04-product-pages.md`.

Current state for comparison: the homepage has a decent meta description and a
useless title; **every other page has no meta description at all**.

---

## 2. Keyword map by page

Group by intent, not by volume. One page owns one intent.

**Transactional, product-level** (own these on product pages)
- titanium camping mug / titanium camping cup nz
- double wall titanium cup
- titanium french press / titanium coffee press
- titanium camping pot 1l
- titanium spork
- coffee scoop 15g
- timemore c3 esp pro nz ← easiest win on the whole site. People search this
  model by name, and you stock it in New Zealand.

**Transactional, category-level** (collection pages)
- camping coffee gear nz
- camping coffee maker
- ultralight coffee setup
- camp kitchen gear nz

**Comparison and advice** (FAQ, brew guide, comparison block — where Nic is)
- single wall vs double wall titanium cup
- titanium vs stainless steel camping mug
- how to make coffee while camping / on a camp stove
- best coffee setup for multi-day hiking
- coffee grind size for french press

**Gift intent, seasonal** (Gifts collection, from late October)
- gifts for hikers nz
- gift for coffee lover under $50
- camping gifts new zealand
- stocking fillers for trampers

**Local and brand** (home, Our Story)
- wild sky coffee
- nz made camping coffee gear (careful: "designed in New Zealand" is what you can
  say truthfully unless the gear is manufactured here — don't let an SEO keyword
  push you into a claim the Fair Trading Act won't support)

---

## 3. Product types and tags (fixes the empty collections too)

Right now seven products have **no product type** and three say **"Other"**. No
types and no tags means no automated collections, no filtering, and no cross-sell
logic. Set these:

| Product | Type | Tags |
|---|---|---|
| Summit Mug | Cups | cups, single-wall, titanium, ultralight, 225ml, gift-under-30 |
| Camp Cup | Cups | cups, single-wall, titanium, 500ml, gift-under-60 |
| Kea Mountain Cup | Cups | cups, double-wall, titanium, 225ml, gift-under-60 |
| Alpine Pot | Cookware | cookware, pots, titanium, 1000ml, stove-safe |
| Traverse Coffee Press | Coffee makers | coffee-makers, press, titanium, 750ml, for-two |
| Backcountry Bean Vault | Storage | storage, titanium, 220ml, gift-under-30 |
| Wild Coffee Scooper | Accessories | accessories, titanium, ultralight, gift-under-30 |
| The Trail Spork | Accessories | accessories, titanium, ultralight, gift-under-30 |
| Brew Table | Camp kitchen | camp-kitchen, titanium, folding, brew-table |
| Timemore C3 ESP Pro | Grinders | grinders, timemore, brew-gear |

Then: make `/collections/cups` an automated collection on `tag = cups`, rebuild
Wild Kitchen on `type = Camp kitchen OR Cookware OR Accessories`, and either fill
or delete `/collections/frontpage`. Three empty collections are crawlable right
now.

The `gift-under-30` / `gift-under-60` tags are what make the Gifts collection
build itself in ten minutes in November.

---

## 4. Alt text — 11 homepage images have none

These are the files with missing or empty alt attributes. Alt text should say
what is in the picture, with a location where you know it:

| File | Alt text |
|---|---|
| `Wildskycoffeein_the_mountains.png` | `Titanium coffee press and cup set up on a rock in the New Zealand mountains` |
| `Brew_Table_6925868d….png` | `Folding titanium Brew Table set up outside a tent with a coffee press on top` |
| `20260710_170836.jpg` | `Coffee brewing in the Kaimanawa Ranges looking across to Mount Ruapehu` |
| `20241129_113929.jpg` | `[describe the photo — where, what gear is in frame]` |
| `20191229_125804….jpg` | `[describe the photo — where, what gear is in frame]` |
| `20201129_094854.jpg` | `[describe the photo — where, what gear is in frame]` |
| Instagram feed thumbnails (4) | Set by the app; if it allows a template, use `Wild Sky Coffee on Instagram — coffee outdoors in New Zealand` |
| Transparent logo | Leave empty — it's decorative and marked `aria-hidden`, which is correct |

While you're in there: **rename the image files before you re-upload them.**
`20260710_170836.jpg` tells Google nothing; `kaimanawa-ranges-titanium-coffee-press.jpg`
tells it everything. Do this for product photos especially.

---

## 5. Technical checklist

- [ ] **Google Search Console** — verify the domain, submit
      `https://www.wildskycoffee.com/sitemap.xml`. Without this you are guessing.
      Do the same in Bing Webmaster Tools, which also feeds some AI answers.
- [ ] **Google Merchant Center** — free product listings put your ten products
      into Google Shopping at no cost. For a new store with no domain authority,
      this is usually the fastest source of qualified traffic. Needs the product
      data tidy first, which is §3 above.
- [ ] **Confirm GA4 and the Meta pixel are firing.** Neither appears in the page
      source. They may be installed as Shopify web pixels, which wouldn't show —
      check Settings → Customer events. Nothing in this document can be measured
      until they are.
- [ ] **og:image is served over `http://`** on an https site. Some platforms will
      drop the preview image when the link is shared. Change to `https://`.
- [ ] **Fix the five mismatched product handles** (listed in `02-site-audit.md`).
      Keep the automatic redirect Shopify offers.
- [ ] **"Malborough" → "Marlborough"** in the blog post title, body and handle.
      You are currently misspelling a place people search for.
- [ ] **Structured data** — Shopify emits Product schema from the theme; confirm
      in the Rich Results Test that price, availability and brand all pass.
      Add Organization markup with your Auckland location, and FAQ markup on the
      FAQ page.
- [ ] **Internal links** — every blog post should link to the gear that was in
      the pack; every product page should link to the comparison block and the
      brew guide. You currently have almost no internal linking, which is free
      and you're not using it.
- [ ] **Page speed** — run PageSpeed Insights on mobile. Symmetry is a decent
      theme; the usual culprits are oversized hero images and the Instagram feed
      app. Compress anything over 300KB.

---

## 6. Content plan — six posts that do a job

Each one aimed at a specific avatar and a specific search, each one linking to
products. Not "content marketing" — five of these answer a question a buyer is
holding with her credit card out.

1. **How to make good coffee on a camp stove** (Nic, avatar 4) — dose, grind,
   ratio, timing, with the press and the 15g scoop. The single highest-value page
   you could write this month.
2. **Single wall or double wall? Choosing a titanium camping cup** (Nic) — the
   comparison, honestly, including when the cheaper one is the right answer.
3. **What's in our pack: a two-day coffee kit, weighed** (Nic, Sarah) — every
   item, every gram, total weight. Links to everything. Turns into the Summit Kit
   bundle page.
4. **Four mornings worth getting up for** (Sarah) — Tarawera, the Kaimanawas,
   the Marlborough Sounds, Wānaka. Your existing trip content, organised, with
   the gear linked.
5. **A present for someone who loves getting outside** (gift buyer, publish by
   1 November) — by price band, with the Christmas cut-off date at the top.
6. **Why titanium, and how to look after it** (everyone) — first wash, cleaning,
   what the colours on the metal mean after heating, what not to put over a
   flame. Answers the maintenance question the site currently ignores.

Publish two a month. Each one gets a line in the email newsletter, a carousel on
Instagram and a short video. One piece of work, four places.

---

## 7. What to measure, monthly

Four numbers, not forty:

1. **Search Console** — impressions and clicks for non-brand terms. This is the
   number that tells you whether any of the above worked.
2. **Conversion rate** by landing page, before and after the trust bar and
   comparison table.
3. **Average order value**, before and after bundles. This is what the Slow
   Morning Kit is for.
4. **Email list size and revenue per email.** You are collecting addresses with
   no sequence behind them — the list is the only asset here that compounds.
