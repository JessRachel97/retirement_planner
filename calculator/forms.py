from django import forms

from calculator.projections import SCENARIOS

MODE_OUTLOOK = "outlook"      # "My current outlook": savings in -> pot + income out
MODE_START = "start"          # "Show me where to start": target income -> how much to save


class PensionForm(forms.Form):
    """Inputs for the retirement calculator.

    Two modes share the same form. `outlook` needs an annual contribution;
    `start` needs a target monthly income instead. clean() enforces the right
    one per mode so the rest of the view can trust the data.

    Inflation ('today's money') is handled in the backend at a fixed rate —
    it's not a user input, to keep the form approachable.
    """

    mode = forms.ChoiceField(
        choices=[(MODE_OUTLOOK, MODE_OUTLOOK), (MODE_START, MODE_START)],
        initial=MODE_OUTLOOK,
        widget=forms.HiddenInput,   # set by the tab buttons in the template
    )

    current_age = forms.IntegerField(min_value=18, max_value=80, initial=29)
    retirement_age = forms.IntegerField(min_value=40, max_value=90, initial=65)

    # Savings split across a few sources; we sum them into one starting pot.
    savings_pension = forms.FloatField(min_value=0, required=False, initial=0)
    savings_cash = forms.FloatField(min_value=0, required=False, initial=0)
    savings_investments = forms.FloatField(min_value=0, required=False, initial=0)
    savings_property = forms.FloatField(min_value=0, required=False, initial=0)

    income = forms.FloatField(min_value=0, required=False, initial=400_000)

    # Mode-specific (each required only in its own mode — see clean()).
    annual_contribution = forms.FloatField(min_value=0, required=False, initial=120_000)
    target_monthly_income = forms.FloatField(min_value=0, required=False, initial=25_000)

    scenario = forms.ChoiceField(choices=[(k, k) for k in SCENARIOS], initial="expected")

    def clean(self):
        cleaned = super().clean()
        current_age = cleaned.get("current_age")
        retirement_age = cleaned.get("retirement_age")
        if current_age and retirement_age and retirement_age <= current_age:
            raise forms.ValidationError("Retirement age must be greater than current age.")

        mode = cleaned.get("mode")
        if mode == MODE_OUTLOOK and cleaned.get("annual_contribution") is None:
            self.add_error("annual_contribution", "Tell us how much you save each year.")
        if mode == MODE_START and cleaned.get("target_monthly_income") is None:
            self.add_error("target_monthly_income", "Tell us the monthly income you want.")
        return cleaned

    def total_savings(self):
        """Sum of the savings sources (treats blank as 0), including home equity."""
        cd = self.cleaned_data
        return sum(
            cd.get(k) or 0
            for k in ("savings_pension", "savings_cash", "savings_investments", "savings_property")
        )
