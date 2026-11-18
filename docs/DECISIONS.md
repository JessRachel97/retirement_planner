# Decisions log

Running record of choices made and why — for review. Newest at top.

## Round 3 — UX redesign + two modes (in progress)
Triggered by: your look/feel + usability feedback.

| # | Decision | Why | Status |
|---|----------|-----|--------|
| 1 | **Two modes via a segmented toggle** — "My current outlook" (savings → pot/income) and "Show me where to start" (target income → how much to save) | Mirrors how real retirement tools work; the reverse-solve answers the question most people actually have ("what should I be saving?"). Reuses the same maths/projection. | building |
| 2 | **Dusty-pastel palette + softer modern type** (grey-lilac/dusty blue/blush, plum-ink, indigo hero; drop the serif) | Your call: pastel, retro, still professional. The navy+serif read cold/dated; the pastel set feels calmer and more approachable for non-expert users. | building |
| 3 | **Savings as a few named sources that sum** (pension / cash / investments) + **plain-language tooltips** on every field | One "balance" box didn't match how people actually hold money; summing named sources is clearer without the full tax/liquidity model (that stays the advanced-mode stretch). | building |
| 4 | **Add optional income → a recommendation** ("replace ~75% of your income") | Lets the tool say something *useful*, not just a number — a target to aim at. Income also makes the "people at your income level" comparison honest (real income, not a contribution proxy). | building |
| 5 | **Reframe jargon in plain words** — scenario → Cautious/Balanced/Ambitious with blurbs; explain "today's money"; add "why this matters" to the chart | The inputs confused a non-financial user; plain language + a one-line "why" on the chart makes it usable by the public, which is the brief's audience. | building |
| 6 | **Auto-scroll to results + clearer compare-card copy** | You couldn't tell results were below the fold, and "on track for R9m" read as meaningless; both are comprehension fixes. | building |

## Round 2 — tooling, admin, code quality (done)
Triggered by: reviewer feedback + your four notes.

| # | Decision | Why | Status |
|---|----------|-----|--------|
| 1 | **One-command run via `Makefile`** (`make run` = migrate → seed → serve; also `make setup`, `make test`, `make admin`) | Collapses multi-step setup into one reproducible command, so the app comes up the same way for anyone (and for CI) with no room for a missed step. | done |
| 2 | **CI pipeline** — GitHub Actions runs the test suite on push/PR | Running the tests automatically on every change catches regressions before they land and keeps the suite honest — the default for any project meant to be maintained. | done |
| 3 | **Register `Projection` in Django admin** (`list_display`, `list_filter`, `date_hierarchy`) | The trends feature depends on stored rows; the admin is the quickest way to inspect, filter and sanity-check that data without writing queries. | done |
| 4 | **Refactor view → Django `Form`** (`calculator/forms.py`) | Removes the hand-synced dual-dict + `_f` parser (a real foot-gun when adding a field) and gives validation/error messages for free — the idiomatic Django approach. | done |
| 5 | **Chart data via `json_script`** (not `\|safe`) + clarifying comments | `\|safe` injects data straight into `<script>`; `json_script` encodes it safely and is the documented Django pattern — correct even though current data is just ints. | done |
| 6 | **Widen tests** — add a trends test + a view smoke test (GET/POST 200) | Locks the user-facing contract (page renders, calc works) and the aggregation logic, not just the pure maths, so the pipeline guards the whole request path. | done |
| 7 | **Admin superuser: dev-only `admin`/`admin`** via `make admin` (non-interactive) | A known local login makes the admin usable immediately; credentials are dev-only and documented, never shipped to a real environment. | done |

### Deliberately deferred / not doing (documented)
- **Keep money as `FloatField`, not `DecimalField` — decided, not doing.** Decimal is the right call for transactional money (billing, ledgers) where exact cents and rounding rules matter. This is a low-stakes *advisory* projection: outputs are rounded to whole Rand and shown as estimates, growth/inflation are themselves assumptions, so float precision is far finer than the inputs' real accuracy. Decimal would add type friction for zero practical gain here.
- **Persist `inflation_rate`** on `Projection` — minor model-completeness gap; low value for POC.
- **Advanced asset-bucket mode** (property / RA / investments / cash) — specced in `DESIGN.md`, deferred as the headline "what I'd do next."
- **Real percentile** in the compare card (vs the current ahead/behind read).

## Round 1 — initial build
See `docs/DESIGN.md` for the full locked spec. Headlines:
- **Stack:** Django + SQLite, Tailwind + Chart.js via CDN (no build step) — a stack you can edit by hand without AI.
- **Context:** South African — Rand, retirement age 65, growth presets 7/10/12%, inflation 5%.
- **Output:** both the pot *and* a plain-English monthly income (4%-rule, explained — no jargon).
- **Inputs:** the brief's 5 + scenario toggle + inflation toggle.
- **Trends:** anonymous rows in the DB → "how you compare" by age and by contribution level; seeded with ~300 synthetic rows so it's alive on first run.
- **Look:** trustworthy institutional (navy/slate, serif headings).
