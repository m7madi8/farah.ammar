# Nana's Bites Backend — Testing

## Run all tests

```bash
cd backend
python manage.py test
```

## Run by app

```bash
python manage.py test accounts
python manage.py test products
python manage.py test orders
```

## Coverage (optional)

```bash
pip install coverage
coverage run --source=accounts,products,orders,config manage.py test
coverage report
coverage html
```

## What's tested

- **accounts:** User model (create, unique email, __str__); register/login/me API (success and validation).
- **products:** Category and Product models; product list (paginated) and detail by slug.
- **orders:** Coupon model; order create (valid payload, insufficient stock, empty items); checkout with empty cart and with session cart; coupon apply (valid and invalid code); payment webhook returns 200; order transaction (items created, stock deducted).

## Notes

- Tests use the default test database (SQLite by default for Django tests unless overridden).
- Webhook test does not verify Stripe signature; it only checks that the endpoint returns 200 to avoid provider retries.
- Checkout test may patch Stripe client secret to avoid external calls.
