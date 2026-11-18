from django.test import TestCase, Client

from calculator.models import Projection
from calculator.projections import project, required_contribution
from calculator.trends import compare


class ProjectionMathTests(TestCase):
    def test_no_growth_no_contribution_keeps_balance(self):
        p = project(30, 31, 100_000, 0, 0.0, inflation_rate=0.0)
        self.assertAlmostEqual(p.pot, 100_000)

    def test_single_year_growth_then_contribution(self):
        # 100k grows 10% -> 110k, then +12k contribution = 122k
        p = project(30, 31, 100_000, 12_000, 0.10, inflation_rate=0.0)
        self.assertAlmostEqual(p.pot, 122_000)
        self.assertEqual(len(p.rows), 1)

    def test_two_years_compounds(self):
        # yr1: 100k*1.1 = 110k ; yr2: 110k*1.1 = 121k
        p = project(30, 32, 100_000, 0, 0.10, inflation_rate=0.0)
        self.assertAlmostEqual(p.pot, 121_000)

    def test_todays_money_discounts_by_inflation(self):
        p = project(30, 32, 100_000, 0, 0.0, inflation_rate=0.05)
        self.assertAlmostEqual(p.pot_today, 100_000 / (1.05 ** 2))

    def test_monthly_income_uses_4pct_rule(self):
        p = project(30, 31, 0, 120_000, 0.0, inflation_rate=0.0)
        # pot 120k -> 4% = 4800/yr -> 400/month
        self.assertAlmostEqual(p.monthly_income, 400)

    def test_retirement_before_current_age_raises(self):
        with self.assertRaises(ValueError):
            project(60, 50, 0, 0, 0.1)

    def test_required_contribution_no_growth(self):
        # Need 100k in 10 years from 0, no growth -> 10k/yr.
        c = required_contribution(30, 40, 0, 0.0, target_pot=100_000)
        self.assertAlmostEqual(c, 10_000)

    def test_required_contribution_zero_when_balance_already_grows_past(self):
        # Starting balance grows past the target on its own -> save nothing.
        c = required_contribution(30, 40, 1_000_000, 0.10, target_pot=500_000)
        self.assertEqual(c, 0.0)

    def test_required_contribution_inverts_project(self):
        # Solving for C and projecting it forward should reproduce the target pot.
        target = project(30, 50, 100_000, 40_000, 0.08).pot
        c = required_contribution(30, 50, 100_000, 0.08, target_pot=target)
        self.assertAlmostEqual(c, 40_000, places=2)


class TrendsTests(TestCase):
    """Tests for the compare() trends aggregation function."""

    def test_compare_returns_dict_with_by_age_and_by_income_keys(self):
        """Verify that compare() returns a dict with the expected structure."""
        # Seed a few synthetic projections.
        Projection.objects.create(
            current_age=35, retirement_age=65, current_balance=200_000,
            annual_contribution=60_000, growth_rate=0.10, projected_pot=1_200_000,
        )
        Projection.objects.create(
            current_age=36, retirement_age=65, current_balance=210_000,
            annual_contribution=62_000, growth_rate=0.10, projected_pot=1_250_000,
        )
        Projection.objects.create(
            current_age=35, retirement_age=65, current_balance=190_000,
            annual_contribution=58_000, growth_rate=0.10, projected_pot=1_150_000,
        )

        result = compare(
            current_age=35,
            annual_contribution=60_000,
            you_balance=200_000,
            you_pot=1_200_000,
        )

        # Verify structure: both keys present, both return valid dicts.
        self.assertIn("by_age", result)
        self.assertIn("by_income", result)
        self.assertIsNotNone(result["by_age"])
        self.assertIsNotNone(result["by_income"])

    def test_compare_by_age_has_sane_medians(self):
        """Verify that by_age cohort returns median balance and pot."""
        Projection.objects.create(
            current_age=33, retirement_age=65, current_balance=100_000,
            annual_contribution=50_000, growth_rate=0.10, projected_pot=800_000,
        )
        Projection.objects.create(
            current_age=35, retirement_age=65, current_balance=200_000,
            annual_contribution=60_000, growth_rate=0.10, projected_pot=1_200_000,
        )
        Projection.objects.create(
            current_age=37, retirement_age=65, current_balance=300_000,
            annual_contribution=70_000, growth_rate=0.10, projected_pot=1_600_000,
        )

        result = compare(
            current_age=35,
            annual_contribution=60_000,
            you_balance=200_000,
            you_pot=1_200_000,
        )

        by_age = result["by_age"]
        self.assertEqual(by_age["count"], 3)
        self.assertEqual(by_age["median_balance"], 200_000)
        self.assertEqual(by_age["median_pot"], 1_200_000)

    def test_compare_by_income_has_sane_medians(self):
        """Verify that by_income cohort returns median balance and pot."""
        Projection.objects.create(
            current_age=25, retirement_age=65, current_balance=50_000,
            annual_contribution=58_000, growth_rate=0.10, projected_pot=600_000,
        )
        Projection.objects.create(
            current_age=35, retirement_age=65, current_balance=200_000,
            annual_contribution=60_000, growth_rate=0.10, projected_pot=1_200_000,
        )
        Projection.objects.create(
            current_age=45, retirement_age=65, current_balance=350_000,
            annual_contribution=62_000, growth_rate=0.10, projected_pot=1_400_000,
        )

        result = compare(
            current_age=35,
            annual_contribution=60_000,
            you_balance=200_000,
            you_pot=1_200_000,
        )

        by_income = result["by_income"]
        self.assertEqual(by_income["count"], 3)
        self.assertEqual(by_income["median_balance"], 200_000)
        self.assertEqual(by_income["median_pot"], 1_200_000)


class ViewSmokeTests(TestCase):
    """Smoke tests for the calculator view."""

    def setUp(self):
        self.client = Client()

    def test_get_root_returns_200(self):
        """Verify that GET / returns a 200 response."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def _valid_payload(self, **overrides):
        data = {
            "mode": "outlook",
            "current_age": 30,
            "retirement_age": 65,
            "savings_pension": 200_000,
            "savings_cash": 50_000,
            "savings_investments": 0,
            "income": 600_000,
            "annual_contribution": 60_000,
            "scenario": "expected",
            "inflation_pct": 5,
            "show_today": "on",
        }
        data.update(overrides)
        return data

    def test_post_outlook_returns_200_and_contains_output(self):
        """Outlook mode: POST renders the pot and monthly income."""
        response = self.client.post("/", self._valid_payload())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Projected pot", response.content)
        self.assertIn(b"/ month", response.content)

    def test_post_start_mode_shows_required_saving(self):
        """Start mode: POST a target income and get a 'how much to save' answer."""
        response = self.client.post(
            "/", self._valid_payload(mode="start", target_monthly_income=25_000)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"to save", response.content)
