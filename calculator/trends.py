"""Aggregate 'how you compare' stats over anonymous Projection rows.

Two cohorts:
  - people your AGE (within +/- 5 years)
  - people at your INCOME LEVEL (+/- 30%). Uses real income when the user gave
    one and matching rows have it; otherwise falls back to annual contribution
    as a proxy.
Each cohort returns a median 'saved now' and median 'projected pot', plus a
plain 'ahead / behind' read on the current user.
"""
from statistics import median

from calculator.models import Projection

AGE_BAND = 5
BAND = 0.30  # +/- 30% for the income / contribution cohort


def _summarise(qs, you_balance):
    balances = list(qs.values_list("current_balance", flat=True))
    pots = list(qs.values_list("projected_pot", flat=True))
    if len(balances) < 3:  # too few to be meaningful
        return None
    med_balance = median(balances)
    return {
        "count": len(balances),
        "median_balance": med_balance,
        "median_pot": median(pots),
        "ahead": you_balance >= med_balance,
        "delta_balance": you_balance - med_balance,
    }


def compare(current_age, annual_contribution, you_balance, you_pot, income=None):
    """Return {'by_age': {...}|None, 'by_income': {...}|None}."""
    by_age_qs = Projection.objects.filter(
        current_age__gte=current_age - AGE_BAND,
        current_age__lte=current_age + AGE_BAND,
    )

    if income:
        # Compare against others who also reported an income, by income band.
        by_income_qs = Projection.objects.filter(
            income__isnull=False,
            income__gte=income * (1 - BAND),
            income__lte=income * (1 + BAND),
        )
    else:
        # Fall back to contribution as a proxy for income level.
        by_income_qs = Projection.objects.filter(
            annual_contribution__gte=annual_contribution * (1 - BAND),
            annual_contribution__lte=annual_contribution * (1 + BAND),
        )

    return {
        "by_age": _summarise(by_age_qs, you_balance),
        "by_income": _summarise(by_income_qs, you_balance),
    }
