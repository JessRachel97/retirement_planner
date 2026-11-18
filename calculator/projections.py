"""Pure pension-projection maths. No Django imports — easy to test and to read.

All money is South African Rand. See docs/DESIGN.md for the assumptions behind
every number here.
"""
from dataclasses import dataclass

# --- Tunable assumptions (documented in the README) ---------------------------
SCENARIOS = {"low": 0.07, "expected": 0.10, "high": 0.12}  # nominal growth presets
DEFAULT_INFLATION = 0.05           # SA long-run ballpark; drives "today's money"
SAFE_WITHDRAWAL_RATE = 0.04        # 4%-a-year rule of thumb for retirement income


@dataclass
class YearRow:
    age: int
    opening: float
    contribution: float
    growth: float
    closing: float


@dataclass
class Projection:
    rows: list          # list[YearRow], one per year until retirement
    pot: float          # nominal balance at retirement
    pot_today: float    # same pot in today's money (inflation-discounted)
    monthly_income: float        # nominal R/month from the 4% rule
    monthly_income_today: float  # that income in today's money


def project(
    current_age: int,
    retirement_age: int,
    current_balance: float,
    annual_contribution: float,
    growth_rate: float,
    inflation_rate: float = DEFAULT_INFLATION,
) -> Projection:
    """Project a pension pot to retirement.

    Model: each year the balance grows by `growth_rate`, then the year's
    contribution is added at year-end. Compounded annually.
    """
    if retirement_age <= current_age:
        raise ValueError("retirement age must be greater than current age")

    rows = []
    balance = float(current_balance)
    for age in range(current_age, retirement_age):
        opening = balance
        growth = opening * growth_rate
        contribution = float(annual_contribution)
        closing = opening + growth + contribution
        rows.append(YearRow(age + 1, opening, contribution, growth, closing))
        balance = closing

    years = retirement_age - current_age
    pot = balance
    pot_today = pot / ((1 + inflation_rate) ** years)

    annual_income = pot * SAFE_WITHDRAWAL_RATE
    monthly_income = annual_income / 12
    monthly_income_today = (annual_income / ((1 + inflation_rate) ** years)) / 12

    return Projection(
        rows=rows,
        pot=pot,
        pot_today=pot_today,
        monthly_income=monthly_income,
        monthly_income_today=monthly_income_today,
    )


def pot_needed_for_income(monthly_income_today, years, inflation_rate=DEFAULT_INFLATION):
    """How big a pot (in future Rand) is needed to draw `monthly_income_today`
    a month in today's money, using the 4% rule. Inflates today's target to the
    future value at retirement."""
    annual_today = monthly_income_today * 12
    annual_future = annual_today * ((1 + inflation_rate) ** years)
    return annual_future / SAFE_WITHDRAWAL_RATE


def required_contribution(
    current_age, retirement_age, current_balance, growth_rate, target_pot
):
    """The flat annual end-of-year contribution needed to reach `target_pot` by
    retirement, given a starting balance and growth rate. Returns 0 if the
    starting balance already grows past the target on its own.

    Inverts the future-value formula:
        pot = balance*(1+g)^n + C * ((1+g)^n - 1) / g
    solved for C.
    """
    if retirement_age <= current_age:
        raise ValueError("retirement age must be greater than current age")
    n = retirement_age - current_age
    grown_balance = current_balance * ((1 + growth_rate) ** n)
    shortfall = target_pot - grown_balance
    if shortfall <= 0:
        return 0.0
    if growth_rate == 0:
        return shortfall / n
    annuity_factor = (((1 + growth_rate) ** n) - 1) / growth_rate
    return shortfall / annuity_factor
