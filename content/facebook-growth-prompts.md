# Facebook Growth Prompts

Seven prompts for growing a Facebook page from zero, transcribed from a
Facebook thread by Thedigitalkinggg, with a version of each one rewritten so
the brackets are already filled in for this business.

Two small gaps remain where the screenshots cut mid sentence, in prompts 3 and
5. They're marked `[...]` and the surrounding text is verbatim.

## Read this before you paste anything

Two of these will damage the brand if you run them as written.

**Prompt 3** ships a list of hook formulas: BREAKING, R.I.P, STOP, NOO WAYYY,
YOU + tool = outcome, I CAN'T BELIEVE THIS IS FREE, 99% of people don't know
this. That's AI tool review voice. It's built for a page selling software to
people scrolling fast, and it's the exact opposite of a woman whispering
something to herself at 11pm. Pasted straight in, it gives you seven posts that
read like somebody else's page. The rewritten version swaps that list for the
patterns in `content/hooks.md`.

Prompt 3 also assumes a keyword comment funnel: hook, then "comment X and I'll
send it", then a first comment with the actual content. That mechanic does work
on Facebook, and it fits the comment CTAs already in `content/style_guide.md`
(Comment 'connection', Comment 'me', Comment 'enough'). Worth keeping.

**Prompt 5** asks Claude to "research what is currently getting attention". With
no search tool switched on, Claude will invent trends that sound right. Add the
sourcing line in the rewritten version, or run `automation/fetch_outliers.py`
first and hand it `content/outliers.csv`.

The author's own advice on prompt 1 is the best line in the thread: pick one
angle, commit, don't switch for 90 days.

## The standing context block

Every one of these needs the same three facts. Paste this above whichever
prompt you're using, then you don't have to fill in a single bracket.

```
My niche: sex and intimacy after 40, for women in long term relationships
and for the couples inside them.

My audience: women roughly 45 to 65, married or partnered ten years or
more. Most aren't in crisis. They aren't fighting. They're lonely inside a
relationship that looks fine from the outside, and they've quietly decided
the problem is them. Many are in perimenopause or menopause and have been
told low desire is just their hormones now.

Me: Tarisha Starr, sex and relationship therapist, theloveadventure.com. I
work with couples to get the closeness back, and with women on their own
desire.

Voice rules, follow these exactly:
- UK and NZ spelling. Realise, colour, behaviour, programme.
- No em dashes or en dashes anywhere. Commas, full stops, ellipses.
- Always contractions. Can't, don't, you've, it's.
- Short sentences. Fragments are fine. Write like speech, not prose.
- Never poetic. Use the words a woman in her fifties would actually say
  out loud to a friend over coffee.
- Banned: queen energy, boss babe, "I see you", research shows, studies
  suggest, come as you are, furthermore, moreover.
- First person from clinical work is good: "I hear this every week",
  "a client said to me last month".
```

## 1. Find your niche and audience in 5 minutes

The problem it solves: you want to start a page and have no idea what to post
about, so you never start. Or you pick something random and quit in two weeks
because nobody engages.

### Original

> You are a Facebook growth strategist who has helped pages go from zero to
> 100K+ followers. I want to start a Facebook page that grows fast and attracts
> an engaged audience. My interests are [LIST 3-5 INTERESTS]. For each interest
> find me a specific content angle that would work on Facebook in 2026. Give
> me: the exact niche angle not just a broad category, who the target audience
> is and their age range, why this audience is active on Facebook specifically,
> 5 content topics I could post about daily without running out of ideas, and
> 10 viral post ideas with hooks already written. Rank everything by growth
> potential for a complete beginner. Be honest about which ones are too
> competitive.

### Filled in

```
You are a Facebook growth strategist who has helped pages go from zero to
100K+ followers. I want to start a Facebook page that grows fast and
attracts an engaged audience.

My interests are: desire and libido in midlife, couples who've stopped
reaching for each other, the body and somatic work, perimenopause and
menopause, and the exhaustion of being the one who holds everything
together.

For each interest find me a specific content angle that would work on
Facebook in 2026. Give me: the exact niche angle not just a broad category,
who the target audience is and their age range, why this audience is active
on Facebook specifically, 5 content topics I could post about daily without
running out of ideas, and 10 viral post ideas with hooks already written.

Rank everything by growth potential for a complete beginner. Be honest
about which ones are too competitive.
```

Then pick one. Commit. Don't switch for 90 days.

## 2. Set up your page so people actually follow you

The problem it solves: someone sees your content, clicks your page, and it
looks empty. No photo, no bio, no cover. They leave in two seconds and never
come back. Your page is your storefront. If it looks abandoned nobody walks in.

### Original

> You are a Facebook page optimization expert. My niche is [YOUR NICHE]. I help
> [WHO] with [WHAT]. I'm starting from zero followers. Build me a complete page
> setup: 5 page name options that are clean, memorable, and easy to search, a
> one-line bio that makes someone follow within 3 seconds of reading it, a full
> about section that builds instant credibility, what my profile photo should
> look like and a Nano Banana prompt to generate it, what my cover photo should
> include and a Nano Banana prompt to generate it, and my first pinned post, a
> short introduction telling people exactly what they'll get from following me.
> Give me 3 options for everything so I can pick the best.

### Filled in

```
You are a Facebook page optimisation expert. My niche is sex and intimacy
after 40. I help women in long term relationships, and the couples inside
them, get the closeness and the wanting back. I'm starting from zero
followers.

Build me a complete page setup: 5 page name options that are clean,
memorable, and easy to search, a one line bio that makes someone follow
within 3 seconds of reading it, a full about section that builds instant
credibility, what my profile photo should look like and an image prompt to
generate it, what my cover photo should include and an image prompt to
generate it, and my first pinned post, a short introduction telling people
exactly what they'll get from following me. Give me 3 options for
everything so I can pick the best.

Two constraints on top.

Name test: would a woman in her fifties say this name out loud to her
husband, or to a friend over coffee? If it would only ever appear in a
brochure, throw it out and write another one.

The profile photo is a real photograph of me, not a generated one. Give me
a shot list and a direction for the photographer instead of an image
prompt. The cover can be generated. Palette for anything generated: Pine
Deep #1F2C1F, Pine Forest #2D3E2C, Moss #5D6B3F, Terracotta #C75D3D, Cream
#F5EFE3. Terracotta stays under 10 percent of the frame. Never pure white,
never pure black.
```

Note on Nano Banana: that's Google's image model, reachable through Gemini. A
generated portrait as a therapist's profile photo is a bad trade, so the
rewrite asks for a shot list instead. The cover image is fine to generate.

## 3. Create a week of content in one morning

The problem it solves: you spend an hour writing one post and by the time
you're done you're exhausted. Meanwhile the pages growing fastest are posting
three to five times a day.

### Original

> You are my personal Facebook content engine. My niche is [YOUR NICHE]. My
> audience is [DESCRIBE THEM]. Create 7 complete Facebook posts for this week.
> Each post must have: a viral hook under 8 words on line 1 using a different
> hook formula each time (BREAKING, R.I.P, STOP, NOO WAYYY, YOU + tool =
> outcome, I CAN'T BELIEVE THIS IS FREE, 99% of people don't know this), 3-5
> lines of body copy with every line under 10 words, nat[...] comment should
> have a title, the problem, the solution, and an actionable tip. The tone must
> be casual and direct. Every sentence must sound like a real person sharing a
> secret with a friend. No corporate language.

The gap swallows the natural CTA instruction and the start of the first comment
instruction. From what's on either side, it's asking for a natural CTA telling
people to comment a keyword, and then a first comment carrying the actual
content.

### Filled in

```
You are my personal Facebook content engine. My niche is sex and intimacy
after 40. My audience is women 45 to 65 in long term relationships who feel
lonely inside a marriage that isn't in crisis.

Create 7 complete Facebook posts for this week. Each post must have:

- A hook on line 1, under 10 words, using a different pattern each time.
  One per post, from this list: "You're not broken...", "No one told
  you...", "You can love him and still feel lonely", "Maybe it's not sex
  you're avoiding...", "The part no one talks about...", "There's a reason
  you shut down...", "Before you blame your body...". The hook names the
  pain she's been carrying quietly. It never promises something the post
  can't pay off.
- 3 to 5 lines of body copy. Every line short enough to read on a phone
  without hitting More.
- One emotional truth that reframes the pain instead of diagnosing it.
- A natural CTA telling people to comment one keyword. Use 'connection',
  'me', or 'enough'.
- A first comment to post underneath, with a title, the problem, the
  solution, and one thing she can actually do tonight.
- A note on what image should sit with it.

The tone must be casual and direct. Every sentence must sound like a
person sharing something honest with a friend. No corporate language, no
advice voice, no clinical voice, no performative empathy.

Give me all 7 numbered, ready to paste.
```

One prompt, seven days of content. Batch it Monday morning and schedule through
Meta Business Suite.

## 4. Turn one idea into 10 Facebook posts

The problem it solves: you finally get a good idea, post it once, then move on.
So you keep forcing yourself to find new ideas every day instead of getting
more out of the ones that already work.

### Original

> You are my Facebook content repurposing strategist. My niche is [YOUR NICHE].
> My audience is [DESCRIBE THEM]. I will give you one content idea, topic, or
> post. Turn it into 10 completely different Facebook posts using different
> angles, hooks, formats, and emotions. Include educational posts, opinion
> posts, list posts, story-based posts, mistakes to avoid, quick tips, and
> discussion posts. Keep every post easy to read, conversational, and designed
> to get comments and shares. Here is the original idea: [PASTE YOUR IDEA]

### Filled in

```
You are my Facebook content repurposing strategist. My niche is sex and
intimacy after 40. My audience is women 45 to 65 in long term
relationships.

I will give you one content idea, topic, or post. Turn it into 10
completely different Facebook posts using different angles, hooks, formats,
and emotions. Include educational posts, opinion posts, list posts, story
based posts, mistakes to avoid, quick tips, and discussion posts. Keep
every post easy to read, conversational, and designed to get comments and
shares.

No two posts should open the same way or land on the same emotion. Story
based posts come from clinical work, in first person, with the client
details changed.

Here is the original idea: [PASTE YOUR IDEA]
```

## 5. Find viral Facebook posts before you create

The problem it solves: you keep creating content without knowing what people
actually want to see. Other pages in your niche already have posts getting
thousands of shares, comments and reactions. Use them as your research.

### Original

> You are my Facebook viral content researcher. My niche is [YOUR NICHE] and my
> audience is [DESCRIBE THEM]. Research what is currently getting attention in
> my niche and give me 20 Facebook content ideas based on topics, questions,
> problems, and conversations people already care about. For each idea, give me
> a strong hook, the [...] people would want to share or comment on it. Do not
> copy other creators. Use the research to help me create original content with
> better angles.

The gap covers what else each idea should carry alongside the hook. Angle and
format, most likely, given the shape of the other prompts.

### Filled in

```
You are my Facebook viral content researcher. My niche is sex and intimacy
after 40 and my audience is women 45 to 65 in long term relationships.

Research what is currently getting attention in my niche and give me 20
Facebook content ideas based on topics, questions, problems, and
conversations people already care about. For each idea, give me a strong
hook, the angle to take, the format, and why people would want to share or
comment on it.

Do not copy other creators. Use the research to help me create original
content with better angles.

Cite a source for every claim about what's currently getting attention.
Where you don't have a source, say so plainly instead of filling the gap.
```

## 6. Make people stop scrolling and read your posts

The problem it solves: you can have the best information in the world, but if
your first line is boring nobody reads the rest. On Facebook your hook has one
job. Make people stop scrolling.

### Original

> You are a Facebook copywriter who specializes in writing high-retention
> hooks. My niche is [YOUR NICHE] and my audience is [DESCRIBE THEM]. I will
> give you a Facebook post idea. Write 20 different hooks for it using
> curiosity, strong opinions, surprising facts, mistakes, questions, personal
> experiences, and useful promises. Keep each hook short, natural, and easy to
> understand. Avoid clickbait that the actual post cannot deliver on. Rank the
> 5 strongest hooks and explain briefly why each one should make someone want
> to keep reading. Here is my post idea: [PASTE YOUR IDEA]

### Filled in

```
You are a Facebook copywriter who specialises in writing high retention
hooks. My niche is sex and intimacy after 40 and my audience is women 45 to
65 in long term relationships.

I will give you a Facebook post idea. Write 20 different hooks for it using
curiosity, strong opinions, surprising facts, mistakes, questions, personal
experiences, and useful promises. Keep each hook short, natural, and easy
to understand. Avoid clickbait that the actual post cannot deliver on.

Rank the 5 strongest hooks and explain briefly why each one should make
someone want to keep reading.

Two extra rules. No hook that diagnoses her. And every hook has to be
something she'd think about herself, not something a coach would say at
her.

Here is my post idea: [PASTE YOUR IDEA]
```

## 7. Turn your best posts into more posts that can go viral

The problem it solves: one of your posts finally takes off, then you never use
what made it work again. If people already proved they like a topic, give them
more of what they came for.

### Original

> You are my Facebook growth strategist. I will give you one of my
> best-performing Facebook posts along with its views, reactions, comments, and
> shares. Analyze why the post worked, including the topic, hook, angle,
> structure, emotion, and reason people engaged with it. Then create 10 new
> post ideas that use the same winning patterns without copying the original
> post. Give me a hook and angle for each one. Rank them from strongest to
> weakest based on their potential to get reach, comments, and shares. Here is
> my post and its performance: [PASTE YOUR POST + STATS]

### Filled in

```
You are my Facebook growth strategist. I will give you one of my best
performing Facebook posts along with its views, reactions, comments, and
shares.

Analyse why the post worked, including the topic, hook, angle, structure,
emotion, and reason people engaged with it. Then create 10 new post ideas
that use the same winning patterns without copying the original post. Give
me a hook and angle for each one. Rank them from strongest to weakest based
on their potential to get reach, comments, and shares.

Separate what you can actually tell from the numbers from what you're
guessing. If the sample is one post, say so.

Here is my post and its performance:
[PASTE YOUR POST]
Views: [ ]  Reactions: [ ]  Comments: [ ]  Shares: [ ]
```

Numbers come from your page, under Professional dashboard, then Content. Don't
run this from memory.

## The order to run them in

Once, at the start: 1, then 2.

Every week: 5, then 3, then 6 on whichever post from 3 matters most.

Every time something takes off: 7 on the winner, then 4 on the winner.

`content/facebook-growth-plan.md` has what came back when these were run
against this niche.
