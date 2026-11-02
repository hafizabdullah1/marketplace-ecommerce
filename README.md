# Marketplace E-Commerce

Multi-role Django marketplace — buyers, sellers, and admins with cart, orders, and Stripe checkout.

## Live demo

[https://ecommerce-marketplace-r88g.onrender.com](https://ecommerce-marketplace-r88g.onrender.com)

## Screenshots

| Storefront | Cart / checkout | Admin / seller |
| --- | --- | --- |
| ![Store](docs/screenshots/store.png) | ![Checkout](docs/screenshots/checkout.png) | ![Admin](docs/screenshots/admin.png) |

## Key features

- Role-based accounts: admin, seller (buyer role in code for store owners), and shoppers
- Product catalog with categories, images (Pillow), and session cart
- Order pipeline with pending/delivered flows
- Stripe payments (`Charge`) + webhook endpoint
- Admin dashboard: sellers, orders, bans
- Seller dashboards for products and order visibility
- Deploy config: `Procfile`, `.render.yaml`, Gunicorn

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend | Django 5.1 |
| Payments | Stripe (`stripe` Python SDK) |
| Config | django-environ |
| Server | Gunicorn on Render |
| DB (current) | SQLite (`db.sqlite3` in repo) |

## Architecture (brief)

```
Browser templates (Django + sessions)
    │
    ├─ user_accounts / products / admin_dashboard apps
    ├─ Stripe checkout + webhook
    └─ SQLite (migrate to Postgres for production hardening)
```

## Getting started

### Prerequisites

- Python 3.10+
- Stripe test keys

### Install

```bash
git clone https://github.com/hafizabdullah1/marketplace-ecommerce.git
cd marketplace-ecommerce
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment

Create `marketplace/.env` (do **not** commit real secrets):

```bash
DEBUG=True
SECRET_KEY=replace-with-long-random-string
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

| Variable | Required | Description |
| --- | --- | --- |
| `DEBUG` | Yes | Django debug flag |
| `SECRET_KEY` | Yes | Django secret key |
| `STRIPE_PUBLIC_KEY` | Yes | Stripe publishable key |
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Yes (webhooks) | Stripe webhook signing secret |

> **Security note:** Move SMTP credentials out of `settings.py` into env vars and rotate any keys that were ever committed.

### Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# production-style:
gunicorn marketplace.wsgi:application
```

## Deployment

- Render: uses `.render.yaml` / `Procfile` (`web: gunicorn marketplace.wsgi:application`).
- Set env vars in the host dashboard; collectstatic + migrate on release.
- Prefer Postgres + object storage for media in production (replace SQLite/local `media/`).

## Roadmap

- [ ] Remove committed `marketplace/.env` and `db.sqlite3` from git history if sensitive
- [ ] Rotate Stripe + email credentials; load email settings from env only
- [ ] Add README on GitHub, topics, MIT license, OG image
- [ ] Pytest suite + CI
- [ ] Postgres + WhiteNoise/S3 for static/media

## Author

**Hafiz Abdullah** — [GitHub](https://github.com/hafizabdullah1) · [hafizabdullah.site](https://hafizabdullah.site)
