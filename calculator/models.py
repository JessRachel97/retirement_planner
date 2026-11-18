from django.db import models


class Projection(models.Model):
    """One anonymous calculator run. No identity is stored — just the numbers,
    so we can show aggregate trends ('people your age / income typically...')."""

    current_age = models.PositiveIntegerField()
    retirement_age = models.PositiveIntegerField()
    current_balance = models.FloatField()          # total across all savings sources
    annual_contribution = models.FloatField()
    income = models.FloatField(null=True, blank=True)  # optional; powers 'people at your income level'
    growth_rate = models.FloatField()
    projected_pot = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"age {self.current_age} -> pot R{self.projected_pot:,.0f}"
