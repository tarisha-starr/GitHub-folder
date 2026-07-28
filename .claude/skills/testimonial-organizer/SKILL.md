---
name: testimonial-organizer
description: Collect, categorise and retrieve testimonials and social proof by program, buyer type and problem solved. Use when the user says "find me a testimonial about", "I need social proof for", "which testimonials should go on this sales page", "organise my testimonials", or is building a sales page, launch email or ad and needs the right proof.
---

# Testimonial Organizer

Automation #19. `content/testimonials.json` currently has every testimonial
tagged with the same seven generic hashtags and no attribution. That means
there's no way to answer "which testimonial proves this objection for this
buyer", so launches use whichever one comes first.

## The problem this fixes

A testimonial's value depends on matching it to the objection it defeats
and the buyer it defeats it for. A quote from a single woman in her
thirties doesn't reassure a married woman of 52 worried about her husband.
Right now they're interchangeable in the file, so they get used
interchangeably.

## Step 1: gather

**Already in the repo:** `content/testimonials.json`.

**New sources to sweep:**
- Gmail: `search_threads` on `label:clients`, and searches like
  "thank you", "wanted to tell you", "since the workshop"
- Zoom: closing rounds of workshop recordings, where women say what
  changed. Often the strongest material and almost never captured.
- Notion: workshop feedback and program pages
- Any screenshots in `images/testimonials/`

## Step 2: enrich each one

Keep the original `id`, `image` and `text` fields untouched. Add:

```json
{
  "id": 1,
  "image": "images/testimonials/testimonial-1.png",
  "text": "unchanged, exactly as she wrote it",
  "program": "SERW | Radiant Woman Circle | Roommates to Lovers | workshop | retreat",
  "buyer": "married 40s | married 50s+ | single | post-divorce | unknown",
  "problem_solved": ["disconnection", "shame", "low desire", "not being met"],
  "objection_answered": "is it too late for me",
  "outcome_named": "what actually changed for her, in her words",
  "strength": "strong | medium | weak",
  "consent": "public | private | unknown",
  "hashtags": ["existing tags stay"]
}
```

**Strength** is a real judgement, use it:
- **strong** — names a specific before/after change
- **medium** — warm but general praise
- **weak** — praises Tarisha rather than describing a result

Weak testimonials still have a use as warmth, but they don't sell. Don't
inflate the rating to make the library look better.

## Step 3: retrieval

When she asks for proof for a page or an email, return the two or three
best matches on **objection first**, buyer second, program third. Explain
in one line why each one fits. Don't return the whole library.

If nothing in the library answers the objection she's writing against, say
that plainly. That's a gap worth knowing about, and it tells her what to
ask for in the next round of feedback.

## Rules that are not negotiable

- **Never edit a testimonial's words.** Not for voice, not for grammar,
  not for length, not for em-dashes. `automation/brand_check.py`
  deliberately skips this file for that reason. A trimmed quote is a
  misquote.
- **Never fabricate one.** Obvious, and worth stating.
- **Consent before publication.** Mark `consent` honestly. Feedback given
  privately in a client email is not automatically a public testimonial.
  If it's `unknown` or `private`, flag that she needs to ask before it
  goes on a sales page. Publishing a private message from a woman
  discussing her intimate life would be a serious breach.
- **Attribution as given.** If a woman gave only a first initial, that's
  what's used. Never add a surname, a location or a photo she didn't
  agree to.

## Finish

After a sweep, report: how many added, the distribution across programs
and buyer types, and where the gaps are. The gaps matter most, they tell
her which proof to go collect.
