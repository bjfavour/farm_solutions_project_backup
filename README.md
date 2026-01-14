# Farm Solutions - Django backend (skeleton)

This is a minimal Django + Django REST Framework project skeleton for the **Farm Solutions** app.
It includes models, serializers, views, router urls, admin, and a small test file.

**Important:** This repository is a code scaffold. Install dependencies and run migrations locally.

## Quick start (on your machine)

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   pip install --upgrade pip
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations and create superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Run development server:
   ```bash
   python manage.py runserver
   ```

5. API root will be at: `http://127.0.0.1:8000/api/`

## Notes
- Settings use SQLite by default for convenience. Swap to PostgreSQL in `core/settings.py` for production.
- TIME_ZONE is set to `Africa/Lagos`.
- JWT is referenced in comments; this scaffold uses DRF Token authentication (you can enable SimpleJWT if preferred).
- See `farm/` for models, views, serializers, admin and tests.

