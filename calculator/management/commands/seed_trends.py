"""Seed ~300 synthetic ANONYMOUS projections so the 'how you compare' card is
alive on first run. POC only — documented in the README. No real people."""
import random

from django.core.management.base import BaseCommand

from calculator.models import Projection
from calculator.projections import SCENARIOS, project


class Command(BaseCommand):
    help = "Seed synthetic anonymous projections for the trends/compare card."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=300)
        parser.add_argument("--reset", action="store_true", help="delete existing rows first")

    def handle(self, *args, **opts):
        rng = random.Random(42)  # deterministic so seeds are reproducible
        if opts["reset"]:
            Projection.objects.all().delete()

        rows = []
        for _ in range(opts["count"]):
            age = rng.randint(22, 60)
            retire = 65
            # Savings loosely scale with age; contributions with a notional income.
            balance = max(0, rng.gauss(age * 15_000, age * 8_000))
            contribution = max(0, rng.gauss(55_000, 30_000))
            # Income loosely implies the contribution (~12% savings rate) + noise.
            income = max(120_000, contribution / 0.12 * rng.uniform(0.8, 1.2))
            growth = SCENARIOS["expected"]
            p = project(age, retire, balance, contribution, growth)
            rows.append(Projection(
                current_age=age, retirement_age=retire,
                current_balance=round(balance), annual_contribution=round(contribution),
                income=round(income), growth_rate=growth, projected_pot=p.pot,
            ))
        Projection.objects.bulk_create(rows)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(rows)} synthetic projections."))
