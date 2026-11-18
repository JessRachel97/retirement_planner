from django.shortcuts import render

from calculator.models import Projection
from calculator import trends
from calculator.forms import PensionForm, MODE_START
from calculator.projections import (
    DEFAULT_INFLATION,
    SCENARIOS,
    project,
    pot_needed_for_income,
    required_contribution,
)

TARGET_REPLACEMENT = 0.75  # experts suggest aiming for ~75% of pre-retirement income


def _recommendation(income, monthly_income_today):
    """Compare projected retirement income to a 75%-of-current-income target.
    Returns None when no income was given."""
    if not income:
        return None
    current_monthly = income / 12
    target_monthly = current_monthly * TARGET_REPLACEMENT
    ratio = monthly_income_today / current_monthly if current_monthly else 0
    return {
        "current_monthly": current_monthly,
        "target_monthly": target_monthly,
        "ratio_pct": ratio * 100,
        "on_track": monthly_income_today >= target_monthly,
    }


def index(request):
    form = PensionForm(request.POST or None)
    result = None
    error = None

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        balance = form.total_savings()
        growth = SCENARIOS[cd["scenario"]]
        inflation = DEFAULT_INFLATION   # fixed backend assumption, not a user input
        years = cd["retirement_age"] - cd["current_age"]

        # In "start" mode we first solve for the contribution needed to hit the
        # user's target income, then project that forward like normal.
        required_monthly = None
        if cd["mode"] == MODE_START:
            target_pot = pot_needed_for_income(cd["target_monthly_income"], years, inflation)
            annual_contribution = required_contribution(
                cd["current_age"], cd["retirement_age"], balance, growth, target_pot
            )
            required_monthly = annual_contribution / 12
        else:
            annual_contribution = cd["annual_contribution"]

        p = project(
            cd["current_age"], cd["retirement_age"], balance,
            annual_contribution, growth, inflation_rate=inflation,
        )

        # Store the run anonymously so we can show aggregate trends.
        Projection.objects.create(
            current_age=cd["current_age"], retirement_age=cd["retirement_age"],
            current_balance=balance, annual_contribution=annual_contribution,
            income=cd.get("income"), growth_rate=growth, projected_pot=p.pot,
        )

        # Chart: cumulative contributions vs the pot — the gap is growth.
        contributed, running = [], balance
        for r in p.rows:
            running += r.contribution
            contributed.append(round(running))

        result = {
            "mode": cd["mode"],
            "p": p,
            "balance": balance,
            "annual_contribution": annual_contribution,
            "required_monthly": required_monthly,
            "growth_pct": growth * 100,
            "chart_labels": [r.age for r in p.rows],
            "chart_pot": [round(r.closing) for r in p.rows],
            "chart_contributed": contributed,
            "recommendation": _recommendation(cd.get("income"), p.monthly_income_today),
            "comparison": trends.compare(
                cd["current_age"], annual_contribution, balance, p.pot,
                income=cd.get("income"),
            ),
        }
    elif request.method == "POST":
        error = "Hmm — a couple of entries need a second look: " + "; ".join(
            msg for field_errors in form.errors.values() for msg in field_errors
        )

    # Current value of each field, for re-rendering the inputs (submitted value
    # on POST, field initial on GET).
    form_values = {name: form[name].value() for name in form.fields}

    return render(request, "index.html", {
        "form": form_values,
        "result": result,
        "error": error,
        # Scenario rates -> friendly labels for the plain-language chooser.
        "scenarios": [
            {"key": "low", "label": "Cautious", "pct": 7,
             "blurb": "Lower risk, steadier — more cash and bonds."},
            {"key": "expected", "label": "Balanced", "pct": 10,
             "blurb": "A typical mix of shares and bonds."},
            {"key": "high", "label": "Ambitious", "pct": 12,
             "blurb": "Higher risk, mostly shares — bigger swings."},
        ],
    })
