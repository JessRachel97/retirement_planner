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

## In my own words - this is a verbatim transcript of me describing my process

I'm quite familiar with retirement calculators online, and before I started I looked
quickly at a Sanlam retirement calculator. What I don't like about it is that half the
time I don't understand what everything on the form is. To remedy that, I tried to add
explanation fields and keep the text quite colloquial.

The other thing I don't like is that I don't know what other people are really doing — so
I added a comparison feature. It currently uses fictitious data, but in a real scenario
it would save what people enter so it could do anonymised comparisons.

What I do like about the online calculators is that they tell you how much you need to
save right now if you want to retire by a certain age, rather than just asking what you
already have. So I added that in as an option.

I elected to keep the views quite simple: I didn't want the form to be overwhelming, so
I included just a few sections per view and you go next, next, next, rather than one
giant form.

How the app works: it does two things — a retirement projection and a comparison. The
projection is year-by-year compound growth. It starts from what you have saved, and every
year you grow the balance by the expected return (depending on whether they chose an
aggressive or a conservative strategy). I also used the 4% rule — drawing 4% a year, which
typically lasts 25 to 30 years. The "where to start" mode does the same thing backwards:
given what someone wants as their income, it works out the pot they need and then how much
to contribute every year.

For the comparison, every run on the system is saved to the database anonymously, and each
time there's a run the median savings and projected pots for people in the same age and
income band are pulled in — so you can see where you stand against your peers.

That's my basic, human-certified description of the app.

## How it fits together
Standard Django split: a **project** (config) plus one **app** (the feature).

- **`pension/`** — the project: settings and URL routing. The front door, not logic.
- **`calculator/`** — the app: all the real code.

A request flows through the app in one line:

```
request → urls.py → views.index() → forms.PensionForm (validate)
                                   → projections.project() (the maths)
                                   → models.Projection (save an anonymous row)
                                   → trends.compare() (how you compare)
                                   → templates/index.html (render)
```

Rule of thumb: a wrong **number** lives in `projections.py`; wrong **data on the page**
in `views.py`; wrong **look** in `templates/index.html`.

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
