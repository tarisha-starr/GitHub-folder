# Command Center data

The nine JSON files that feed the CEO Command Center dashboard live in this
directory. **They are gitignored on purpose.** This repository is public, and
these files hold revenue, client names, deal values and team workload. Nothing
in here except this README should ever be committed.

## Set it up

```bash
cp .claude/skills/ceo-command-center/templates/*.json business/command-center/
```

Then fill them in. Every field is documented inside the template itself, under
`_help`, and in full in
`.claude/skills/ceo-command-center/references/data-model.md`.

## Render the dashboard

```bash
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py
```

Writes `dashboards/command-center.html` (also gitignored) and prints a short
brief to the terminal.

## See it working first

```bash
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py \
    --data .claude/skills/ceo-command-center/example \
    --out dashboards/example.html --as-of 2026-08-26
```

That runs on a fictional business, so you can see what a filled-in dashboard
looks like before typing a single real number.

## If you want the numbers versioned

Keep them in a private repository, or anywhere outside this one, and point the
renderer at it:

```bash
python3 .claude/skills/ceo-command-center/scripts/render_dashboard.py \
    --data ~/business-data/command-center
```
