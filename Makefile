.PHONY: setup run test admin

# Install dependencies and run migrations.
setup:
	pip install -r requirements.txt && python3 manage.py migrate

# Run database migrations, seed synthetic projections, and start the dev server.
run:
	python3 manage.py migrate && python3 manage.py seed_trends --reset && python3 manage.py runserver

# Run the calculator app test suite.
test:
	python3 manage.py test calculator

# Create a dev-only superuser (admin/admin@example.com).
admin:
	DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser --noinput --username admin --email admin@example.com || true
