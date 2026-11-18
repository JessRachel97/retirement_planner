# Pension Calculator — POC Spec

A single-page SA retirement planner. No accounts. Built to be read and edited by hand.

This document captures the design as shipped. The chronological reasoning — including
where the design changed in response to feedback — is in `DECISIONS.md`.

## Shape
- **Stack:** Django + SQLite, Tailwind + Chart.js via CDN (no build step).
- **Two modes:** *current outlook* (savings → pot + income) and *where to start*
  (target income → required saving, via a reverse solver).
- **Headline:** both the pot *and* a plain-English monthly income — no jargon.
- **Inputs:** a short stepped form — age, retirement age, savings across a few named
  sources (pension/RA, cash, investments, property), yearly income, the mode-specific
  field, and a plain-language risk choice (Cautious/Balanced/Ambitious).
- **Results:** a tap-through carousel — headline, growth chart, how-you-compare,
  year-by-year.
- **Look:** dusty-pastel, calm and approachable; softer modern type.
- **Context:** South African — Rand throughout.

## Assumptions (defensible; in README)
- Currency Rand; default retirement age 65.
- Growth scenarios (nominal): Cautious 7% / Balanced 10% / Ambitious 12%.
- Inflation 5%, applied in the backend to show "today's money" (not a user input).
- Contributions added end-of-year, flat (no escalation); annual compounding.
- Monthly income = 4%-of-pot-a-year rule of thumb (lasts ~25–30 yrs), explained plainly.
- Savings sources summed into one pot with one growth rate; property included as a rough
  cushion, caveated in the UI.
- Trends seeded with ~300 synthetic anonymous rows so the compare feature is alive on day one.

## Build
- `projections.py` — pure maths: `project()` plus `required_contribution()` (the reverse
  solver) and `pot_needed_for_income()`. **Unit tested.**
- `trends.py` — cohort medians by age and by income/contribution level.
- `models.py` — `Projection`: anonymous inputs + computed pot + timestamp.
- `forms.py` — `PensionForm`: validation and per-mode rules.
- `views.py` — one view: GET form / POST calc, save, query trends, render.
- `admin.py` — `Projection` registered for inspection.
- `seed_trends.py` — synthetic rows.
- one template (+ a tooltip partial), CDN front-end.

## Advanced mode (optional / stretch)
Default is **one blended pot, one growth rate** (POC simplification). Advanced mode
lets the user split savings across buckets — **property, retirement funds (RA/pension),
investments (discretionary/TFSA), cash** — each with its own growth rate, then sums the
projections. Rationale for keeping it *optional*: real buckets carry different tax (Reg 28,
TFSA limits, RA access rules), liquidity (property isn't drawdown-able), and risk — full
fidelity is a planning tool, not a 60-min POC. The pure `project()` function already works
per-bucket, so advanced mode = run it N times and total. Toggle hidden behind an
"Advanced" disclosure so the simple path stays clean. Likely a *"what I'd do next"* item
unless time allows a basic 2-bucket version.
