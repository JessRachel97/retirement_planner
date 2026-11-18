# Pension Calculator — POC Spec

A single-page SA retirement planner. No accounts. Built to be read and edited by hand.

## Your decisions (locked)
- **Stack:** Django + SQLite, Tailwind + Chart.js via CDN (no build step).
- **Headline:** both the pot *and* a plain-English monthly income — no jargon.
- **Inputs:** the 5 from the brief + a Low/Expected/High scenario toggle + an
  adjustable "today's money" (inflation) toggle.
- **Look:** trustworthy institutional — navy/slate, serif headings, clean cards.
- **Compare card (compact):** where you stand now vs peers + where your cohort lands.
- **Context:** South African — Rand throughout.

## Assumptions (defensible; in README)
- Currency Rand; default retirement age 65.
- Growth presets (nominal): Low 7% / Expected 10% / High 12%.
- Inflation 5% drives "today's money".
- Contributions added end-of-year, flat (no escalation); annual compounding.
- Monthly income = 4%-of-pot-a-year rule of thumb (lasts ~25–30 yrs), explained plainly.
- Trends seeded with ~300 synthetic anonymous rows so the compare card is alive on day one.

## Build
- `projections.py` — pure `project(inputs)` → year series + summary. **Unit tested.**
- `trends.py` — cohort medians + your percentile, by age ±5.
- `models.py` — `Projection`: anonymous inputs + computed pot + timestamp.
- `views.py` — one view: GET form / POST calc, save, query trends, render.
- `seed_trends.py` — synthetic rows.
- one template, CDN front-end.

Order: math+test → view → template → trends/seed → README. Degrades gracefully if time runs short.

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
