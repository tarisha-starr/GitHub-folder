---
name: post-relevance
description: Run Tarisha's eight-pass relevance workflow over a draft social post, from content brief to red-teamed publishing package. Use this whenever she pastes a draft caption or post and wants it audited, scored, sharpened or made worth saving, and whenever she says any of "relevance pass", "relevance score", "why should I care test", "hook stress test", "stress test these hooks", "confusion remover", "value multiplier", "make this saveable", "humanise this", "stop sounding like AI", "de-AI this post", "save and share engine", "publishing package", "pinned comments" or "red team this". Trigger it even on a vague "is this post any good?" or "can you improve this caption?", because the passes are gated and ordered and a single-pass rewrite skips the scoring, the hook ranking, the fact check and the red-team gate that make the output publishable.
---

# Post relevance pass

A content brief, then eight passes that take a draft social post from "probably
fine" to a red-teamed publishing package. The whole point is the ordering and
the gates. A single-pass rewrite produces something that reads better and still
gets scrolled past, because nobody asked why a stranger would stop, nobody
ranked the hooks against each other, and nobody tried to reject the post before
the audience did.

Run every pass in one conversation. Each pass eats the previous pass's output,
so a skipped pass silently corrupts the ones after it.

**Never ask for "make this viral".** Give the audience, problem, result and
format, then make every creative decision defend itself. That is the whole
method, and it is why the brief is not optional.

## The workflow

| # | Pass | Gate before moving on |
|---|---|---|
| — | Content brief | all six fields answered, no placeholders |
| 1 | Confirm the idea matters, the "why should I care?" test | relevance score of 8 or higher |
| 2 | Find the strongest hook, the stress test | 15 hooks generated, top 5 ranked, one chosen |
| 3 | Remove confusion | no sentence needs a second read, post no longer |
| 4 | Increase the value | numbered sections, each complete on its own |
| 5 | Make the language human, the stop-sounding-like-AI edit | humanised version plus the 5 patterns removed |
| 6 | Add reasons to save, share and comment | 5 specific questions, one selected |
| 7 | Build the publishing package | A to E returned, fact check non-empty or explicitly clear |
| 8 | Red-team the final result | all eight scores at 8 or higher |

The verbatim prompts live in `references/prompt-pack.md`, numbered to match this
table. Her original notes numbered the brief as 1 and ran to 9; the pack and
this skill use the workflow numbering above, where the brief is setup and the
red team is 8.

## The content brief

Nothing runs before this. Collect six things, asking only for what is missing:

- **My audience** — exactly who should care
- **Their current problem** — what they are struggling with
- **The result I am promising** — what they will know, save or achieve
- **The content format** — text post, visual post, carousel, reel
- **The action I want** — comment, share, save, click
- **My draft** — the complete post

Infer the first two from `content/style_guide.md` and the personas in the repo
when she says "you know my audience": women over 40, busy careers, teenagers,
long marriages, either single after a divorce or coupled and lonely. Confirm the
inference in one line rather than asking her to retype it. Never invent the
draft or the promise.

## The gates that actually matter

**Pass 1 does not rewrite.** It diagnoses and scores. Resist finishing the pass
with an improved post, because the hook work in pass 2 has to happen against the
original promise, not against a rewrite that already drifted.

**A score below 8 stops the workflow.** Name the single highest-leverage
strategic change, make that change, re-score. Only move to pass 2 at 8 or above.
Scoring a weak post 8 to keep things moving wastes the next seven passes.

**Pass 2 picks exactly one hook.** Fifteen hooks, five ranked, one winner with
the reason it should beat the original. Passes 3 onward use the winner and no
other.

**Pass 3 must not lengthen the post.** It returns the improved version, every
sentence removed, and why each removal helped. If the post got longer, the pass
failed.

**Pass 7 needs 4, 5 and 6 done.** It assembles the caption from 3 and 5, the
pinned comments from 4, and the engagement question from 6. Run it early and it
packages a post that has not been sharpened.

**Pass 8 can send work backwards, and that is the point.** Eight scores: hook,
clarity, originality, usefulness, credibility, saveability, shareability,
comment potential. Nothing publishes until every one is at 8. Fix only the
weakness named, then re-emit the affected part of the package rather than the
whole thing, and re-score. A red team that approves everything on the first look
is not doing its job, so if it returns eight 9s immediately, run it again harder.

## The voice layer

The prompts are generic. Tarisha's voice is not. Apply `content/style_guide.md`
over every pass output, and fix these specific collisions, which is where the
generic prompts will otherwise produce work she rejects.

**"Unlock" is a product name, not a banned word.** Pass 5 bans it. Her flagship
funnel is the Unlock Your Desire Challenge and the 5 Keys to Unlock Your Desire
webinar. Strip it as a lazy verb, "unlock your potential", and keep it every
time it names an actual offer. Same logic for "real": discouraged as filler,
kept when it carries the sentence, flagged rather than silently removed. Note
that pass 4's own instruction says "increase the real value", so the word is
in the workflow's own wording. Judgement, not search and replace.

**The prompts are written in US English.** Analyze, organize, favorite,
humanized, prioritize. Her rule is UK and NZ spelling. The prompt pack carries
a preamble that forces UK spelling in the output, so paste from there rather
than retyping the prompts from memory.

**Pass 5's source text contains an em dash.** So does the workflow summary she
supplied. Em dashes and en dashes are a hard never in her copy. The pack has
them normalised already.

**Eighth-grade reading level does not mean flatten the rhythm.** Pass 3 asks for
short sentences and a confident conversational tone, which is compatible with
her voice. Fragments, run-ons, trailing ellipses and repeated short questions
are the voice, not errors. Sand those off and the post reads like everyone
else's.

**Uppercase mini-headlines are structural, not emphasis.** Passes 4 and 7 want
uppercase headers on the pinned comments. Fine. Her rule about using caps
sparingly governs emphasis inside a sentence, where the limit stays one word.

**Pass 6's banned generic questions map onto her working CTAs.** "What do you
think?" is out. Her comment-driven forms are in: `Comment 'connection'`,
`Say with me "I choose me"`, `Ask your body "how are you doing, darling?"`, and
direct invitations like `Are you ready?`. Prefer one of those shapes when
selecting the final question.

**Pass 8's credibility score is where her voice helps.** First-person
observation from her practice, "I hear this every week", is more believable than
any statistic, and it never needs a fact check. Reach for it before reaching for
a number.

Run `scripts/check_post.py` over the final caption and the pinned comments
before handing anything over. It catches the dashes, the AI tells from pass 5,
the generic questions from pass 6 and the US spellings.

## Two ways to run this

**Claude runs the passes.** The default. Work through the brief and passes 1 to 8
in the conversation, one pass per message, pausing at each gate for her call. Do
not batch three passes into one reply: the gates exist so she can redirect at
the cheap points, and a single wall of eight passes gives her nothing to steer.

**Hand over the prompt pack.** When she wants to run it herself in ChatGPT or a
separate Claude conversation, give her `references/prompt-pack.md`. It is
copy-paste ready, in order, with the voice preamble at the top. Remind her to
keep one conversation for all eight.

## What "done" looks like

- A final caption with the winning hook, three short paragraphs at most, value
  withheld, pointing to the comments.
- Pinned comments that each stand alone, uppercase mini-headline, carrying every
  prompt, step, example and link. No comment holding one thin tip.
- Five visual title options, eight words maximum, legible on a phone.
- A 1:1 visual direction with one obvious visual story and room for the title.
- A fact check listing every claim, number, feature and link needing
  verification, or an explicit statement that there are none.
- Red-team scores of 8 or higher on all eight dimensions, with the fixes applied.
- `scripts/check_post.py` passing on the caption and comments.

## What not to do

- Do not skip the brief because the draft "explains itself". The promise is what
  passes 1, 4, 7 and 8 are measured against.
- Do not ask for virality. Ask for a defended decision.
- Do not rewrite during pass 1, and do not soften the diagnosis. The pass is
  worth nothing if it cannot say a sentence is generic.
- Do not carry more than one hook out of pass 2.
- Do not let pass 4 pad the post. Usefulness over quantity is the instruction,
  and a fifth thin section is worse than four strong ones.
- Do not invent sources, statistics, product features or links at any pass, and
  never at pass 7. Anything unverified goes in the fact check list, not the
  caption.
- Do not fabricate a personal story to satisfy pass 5. Her stories come from her
  own practice, so ask her for one or use an "I hear this every week"
  observation instead.
- Do not let pass 8 rewrite the whole package to fix one weak score. Fix the
  named weakness only, or the passes before it get quietly undone.
- Do not hand over a package that still has an em dash in it.
