# Retirement Planner — POC

A small Django web app that projects a pension pot to retirement and translates it
into plain-English monthly income. South African context (Rand). No accounts.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_trends --reset                 # ~300 synthetic rows for the compare card
python manage.py runserver
```

Open http://127.0.0.1:8000/ and press **Calculate**. The form is pre-filled with
sensible defaults so it works on first click.

Run the tests (the projection maths):

```bash
python manage.py test calculator
```

## What it does
- Takes the 5 brief inputs + a growth **scenario** (Low/Expected/High) and an
  adjustable **inflation** rate.
- Shows: projected pot, the same pot in **today's money**, and — in plain terms —
  roughly **how much per month** that pot could pay you in retirement.
- A growth chart and a year-by-year table (so the maths is visible and checkable).
- A **"how you compare"** card: vs people your **age**, and vs people at a similar
  **contribution level**, drawn from anonymous rows stored in the DB.

## Assumptions (and why)
- **Currency: Rand; retirement age default 65** — SA context.
- **Growth presets (nominal): Low 7% / Expected 10% / High 12%** — SA balanced-fund
  long-run ballpark. A toggle, not a single fragile number.
- **Inflation 5%** drives the "today's money" figure (SA long-run ballpark); adjustable.
- **Contributions added end-of-year, flat (no escalation), compounded annually** —
  simplest defensible model.
- **Monthly income = 4% of the pot per year** ("safe withdrawal" rule of thumb, which
  also tends to make a pot last ~25–30 years). Chosen because users shouldn't need to
  understand "drawdown" or "years in retirement" — one number, explained in one line.
- **One blended pot, one growth rate.** No split across property / RA / TFSA / cash —
  those carry different tax, liquidity and risk and are out of POC scope (see *Next*).
- **"Income level" is proxied by contribution size** — the brief collects no salary.
- **Trends are seeded with ~300 synthetic, anonymous rows** so the compare card is
  alive on first run. No real people; real usage adds to it. Rows store only numbers —
  no identity, nothing to log in to.

## How I used AI
- **Tool:** Claude Code (Opus) — used to brainstorm scope, write the spec
  (`docs/DESIGN.md`), scaffold the Django app, and draft the code/template.
- **Kept:** the overall architecture (pure `project()` function + thin view), the
  SA framing, the plain-English income translation, the trends/compare idea, and the
  test-first approach on the maths.
- **Rejected / overrode:** keeping it Flask (chose Django — the stack I can edit by
  hand); over-building asset-bucket fidelity up front (deferred to an optional advanced
  mode); a single-number-only output (added income + compare to make it genuinely useful).
- I reviewed and understand every file — the maths and the view are deliberately plain
  so I can change them live.

## What I'd do next (with more time)
- **Advanced mode:** split savings into property / retirement funds / investments / cash,
  each with its own growth rate (the `project()` function already works per-bucket — it's
  run-N-times-and-sum). Spec is in `docs/DESIGN.md`.
- **Escalating contributions** (grow with inflation / salary).
- **Real drawdown modelling** instead of the 4% rule of thumb (longevity, depletion age).
- **A proper percentile** in the compare card ("you're in the top 30% for your age").
- Tax realism (Reg 28, TFSA limits, RA access rules) and input validation/UX hardening.
- Move Tailwind/Chart.js off CDN to pinned local assets for production.

## Layout
```
calculator/
  projections.py   pure maths — project(inputs) -> year series + pot + income   (tested)
  trends.py        cohort medians, by age and by contribution level
  models.py        Projection — one anonymous run
  views.py         single view: GET form / POST calculate + save + compare
  management/commands/seed_trends.py
  templates/index.html
  tests.py
docs/DESIGN.md     the short spec + logged decisions
```
