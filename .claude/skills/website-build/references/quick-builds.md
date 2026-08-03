# Quick builds, standalone sites

These are for small sites that stand on their own: a personal homepage, a site
for another business, a rebuild of a layout you admire. They are **not** for
theloveadventure.com. That site is WordPress and its pages get pasted into
Kadence, so the rules in `SKILL.md` apply there instead.

What changes for these is the brand: a personal site or another business does
not inherit the Pine Forest palette or Tarisha's voice rules, so the design
direction is open. What does not change is how the work is delivered, which is
covered at the bottom of this page.

## 1. One-page personal site, about 15 minutes

> Build me a one-page personal website for [NAME]. Include a hero with my name
> and a one-line bio, an about section, and links to [LINKS]. Make it look
> designed rather than generic, pick a bold modern style.

Load `artifact-design` or `/mnt/skills/public/frontend-design` first. For a
personal site the brand is the person, so ask for or infer one concrete thing
about them and let the design come from that, rather than reaching for a
default. Publish an artifact preview so she can look at it on a phone.

## 2. Site for a local business, about 20 minutes

> Build a modern website for a [TYPE] called [NAME]. Include hero, services,
> testimonials, and a contact section. Make it convert with clear calls to
> action.

Two cautions worth raising before building:

- If the business is a **client of Tarisha's**, or any organisation that
  exists, do not invent testimonials, ratings, prices or credentials. Mark
  every placeholder plainly so it cannot reach production by accident. This is
  the same rule as the main site and it matters more here, because a stranger's
  business carries the consequences.
- If the business is imagined, say so somewhere on the page or in the handoff,
  so a practice piece is never mistaken for a live trading site.

`references/conversion.md` covers which conversion elements earn their place.
A local business page usually wants the Tier 2 set: hero, clear calls to
action, guarantee, FAQ. It rarely wants a countdown.

## 3. Rebuild a layout you admire, about 15 minutes

> Here is a screenshot of a website I love: [SCREENSHOT]. Rebuild this layout
> and feel as my own site for [PURPOSE]. Match the quality, not the content.

Screenshots get you a good way there. Pasted HTML and CSS get you the rest,
so ask for the source if the result needs to be close. This environment's
proxy blocks most domains, so fetching the reference site directly usually
fails and the user has to paste it in.

What to carry over: layout, spacing rhythm, type scale, density, the way the
hero is composed. What not to carry over: their copy, photography, logo, icon
set, or illustrations. Those belong to someone else, and swapping in the
user's own branding is the point of the exercise anyway.

## Delivering these

No Vercel, no Netlify, no static hosting. Tarisha has ruled it out for every
build, not only the WordPress ones, so do not offer it as a shortcut.

Deliver the same way as everything else: an artifact preview link she can open
on a phone, plus the single HTML file committed to the repo. If a site
genuinely needs to be live at its own address, that is a decision for her, and
the next step is a conversation rather than a deploy command.
