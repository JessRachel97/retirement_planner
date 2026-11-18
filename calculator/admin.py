from django.contrib import admin

from calculator.models import Projection


@admin.register(Projection)
class ProjectionAdmin(admin.ModelAdmin):
    """Admin interface for anonymous pension projections.

    Lists the key numeric fields and created_at timestamp. Filterable by age
    and creation date, with hierarchical drill-down by date for quick navigation.
    """
    list_display = (
        "current_age",
        "retirement_age",
        "current_balance",
        "annual_contribution",
        "growth_rate",
        "projected_pot",
        "created_at",
    )
    list_filter = ("current_age", "created_at")
    date_hierarchy = "created_at"
