# برنج رودی — Django Shop

Unified Django project for **storefront**, **user panel**, and **staff admin** with SQLite.

## Setup

```bash
cd roudi
pip install -r requirements-django.txt
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser   # staff access (set is_staff=True)
python manage.py runserver
```

## URLs

| Area | Path |
|------|------|
| Storefront home | `/` |
| Products | `/products/` |
| Login / Signup | `/auth/login/` `/auth/signup/` |
| User panel | `/user/` |
| User cart & orders | `/user/cart/` `/user/orders/` |
| Staff admin UI | `/staff/` |
| Django admin | `/django-admin/` |

## Tests

```bash
python manage.py test
```

All tests use an in-memory SQLite database.

## Apps

- `catalog` — products
- `accounts` — profiles, phone login
- `orders` — cart, checkout, order cancel

Static assets from the original HTML UIs live under `static/storefront`, `static/user`, and `static/staff`.
