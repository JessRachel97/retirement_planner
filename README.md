# Retirement Planner — POC

A small Django web app that helps someone see what their pension could be worth at
retirement, and — in plain language — what it could pay them each month. South
African context (Rand). No accounts.

Two modes:
- **My current outlook** — enter what you've saved and what you save each year, see
  your projected pot and monthly income.
- **Show me where to start** — enter the monthly income you'd like in retirement, and
  it works out how much you'd need to save to get there.

## Run it

One command (migrates, seeds sample data, starts the server):

```bash
make run
```

Or the steps by hand:

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_trends --reset                 # ~300 anonymous sample rows for the compare feature
python manage.py runserver
```

Open http://127.0.0.1:8000/ and work through the three steps. The form is pre-filled
with sensible defaults so it works on the first run.

Run the tests:

```bash
make test        # or: python manage.py test calculator
```

Optional — browse the stored rows in the Django admin:

```bash
make admin       # creates a dev-only superuser  admin / admin
```
Then open http://127.0.0.1:8000/admin/ → Projections.

## What it does
- A short, **stepped form** collects: age, retirement age, what you've saved (across
  pension/RA, cash, investments and property), yearly income, and either what you save
  each year (outlook mode) or your target monthly income (start mode), plus how your
  savings are invested.
- Results appear as a **tap-through carousel**: the headline figure, a chart of where
  the pot comes from, how you compare, and a year-by-year breakdown.
- The headline gives both the **projected pot** and a plain-English **monthly income**,
  and the pot **in today's money** so it's relatable.
- If you give an income, a **recommendation** shows how much of it you're on track to
  replace (against a ~75% target).
- A **"how you compare"** view shows medians for people your age and people at a similar
  income level, drawn from anonymous rows stored in the DB.

## Assumptions (and why)
- **Currency: Rand; default retirement age 65** — SA context.
- **Growth scenarios (nominal): Cautious 7% / Balanced 10% / Ambitious 12%** — SA
  balanced-fund long-run ballpark, framed in plain words rather than a single fragile
  number.
- **Inflation 5%**, applied in the backend to show "today's money". It's a fixed
  assumption rather than a user input, to keep the form approachable.
- **Contributions added end-of-year, flat (no escalation), compounded annually** — the
  simplest defensible model.
- **Monthly income = 4% of the pot per year** ("safe withdrawal" rule of thumb, which
  also tends to make a pot last ~25–30 years). Chosen so users don't need to understand
  "drawdown" or "years in retirement" — one number, explained in one line.
- **Savings sources are summed into one pot with one growth rate.** Property is included
  as a rough cushion (the UI notes a home isn't easily turned into monthly income).
  Per-source growth and tax/liquidity differences are out of POC scope (see *Next*).
- **"Income level" uses the income you enter** (falling back to contribution size when
  it's left blank), to group you with similar people for the comparison.
- **Trends are seeded with ~300 synthetic, anonymous rows** so the compare feature is
  alive on first run. No real people; real usage adds to it. Rows store only numbers —
  no identity, nothing to log in to.

## How I used AI
- **Tool:** Claude Code — used to brainstorm scope and assumptions, draft the Django
  app and template, and run small sub-agents for a code-quality review and for the
  tooling (Makefile, CI, admin).
- **Kept:** the architecture (a pure, unit-tested `project()` function with a thin
  view), the SA framing, the plain-English income translation, the two-mode design, and
  the trends/compare idea.
- **Rejected / overrode:** Flask (chose Django — the stack I can edit by hand); storing
  money as `DecimalField` (float is fine for low-stakes advisory estimates); over-building
  per-bucket asset modelling up front (deferred); a single-number-only output (added the
  income framing and comparison to make it genuinely useful).
- I reviewed every file and kept the maths and view deliberately plain so I can change
  them by hand.

## What I'd do next (with more time)
- **Advanced mode:** split savings into property / retirement funds / investments / cash,
  each with its own growth rate (the `project()` function already works per-bucket — it's
  run-N-times-and-sum). Spec is in `docs/DESIGN.md`. I mean owning my house has to count for something right?
- **Escalating contributions** (grow with inflation / salary). Family planning, etc.
- **Real drawdown modelling** instead of the 4% rule of thumb (longevity, depletion age).
- **A proper percentile** in the compare card ("you're in the top 30% for your age").
- Tax realism specifically surrounding tax free savings accounts and the likes.
- De-AI-ify the user interface and make it a bit more unique to use.

## Project layout
```
calculator/
  projections.py   pure maths — project() + reverse solver (required_contribution)   (tested)
  trends.py        cohort medians, by age and by income/contribution level
  models.py        Projection — one anonymous run
  forms.py         PensionForm — validates inputs, handles both modes
  views.py         single view: GET form / POST calculate + save + compare
  admin.py         Projection registered for browsing stored rows
  management/commands/seed_trends.py
  templates/
    index.html     the UI (Tailwind + Chart.js via CDN)
    tip.html       small reusable tooltip partial
  tests.py
docs/
  DESIGN.md        the design spec
  DECISIONS.md     running log of decisions and why
Makefile           setup / run / test / admin
.github/workflows/ci.yml   runs the test suite on push
```
