# Nana's Bites — Django Backend

Production-ready Django + DRF backend for the Nana's Bites store. Uses PostgreSQL and aligns with the ER diagram and `react-app/docs/database-schema.sql`.

## Setup

1. **Create a virtualenv and install dependencies**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Environment variables**

   Create a `.env` or set:

   - `DJANGO_SECRET_KEY` — required in production
   - `DJANGO_DEBUG=1` — optional, for local dev
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL (defaults: `nanas_bites`, `postgres`, …, `127.0.0.1`, `5432`)
   - `ALLOWED_HOSTS` — comma-separated (default: `localhost,127.0.0.1`)
   - `CORS_ORIGINS` — comma-separated (default: `http://localhost:3000`)

3. **Database and migrations**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## API Overview

**Auth (Token + JWT; rate limited)**  
- `POST /api/auth/register/` — Register; returns user + token  
- `POST /api/auth/login/` — Login; returns user + token  
- `POST /api/auth/logout/` — Invalidate token (authenticated)  
- `GET|PATCH /api/auth/me/` — Profile (authenticated)  
- `POST /api/auth/jwt/token/` — JWT obtain (body: `email`, `password`); returns `access`, `refresh`  
- `POST /api/auth/jwt/refresh/` — JWT refresh (body: `refresh`)  
- `POST /api/auth/jwt/blacklist/` — Blacklist refresh token (body: `refresh`)  

**Products**  
- `GET /api/products/` — List all products (paginated, filter/search)  
- `GET /api/products/<slug>/` — Product detail with nested images and categories  
- `GET /api/categories/`, `GET /api/categories/<slug>/` — Categories  
- `GET /api/inventory-logs/` — Read-only inventory logs  

**Orders**  
- `GET /api/orders/` — List orders (**admin only**)  
- `GET /api/orders/<public_id>/` — Order detail (owner, admin, or guest with public_id)  
- `POST /api/orders/` — Create order (items, stock/price/coupon validated)  
- `PATCH /api/orders/<public_id>/status/` — Update order status (**admin only**)  

**Cart (session-based)**  
- `GET /api/cart/` — Get cart (items, subtotal)  
- `POST /api/cart/add/` — Add product (body: `product`, `quantity`)  
- `POST /api/cart/remove/` — Remove product (body: `product`, optional `quantity`)  

**Checkout & payment**  
- `POST /api/checkout/` — Validate cart (stock, price, coupon), compute totals (subtotal, discount, tax, shipping), create Order in a transaction, return Stripe `payment_client_secret` or PayPal `payment_url`. Stock is deducted only after webhook confirms payment.  
- `POST /api/webhook/payment/` — Stripe webhook: verify signature, on `payment_intent.succeeded` update Order (paid), deduct stock and create InventoryLog in one transaction. Idempotent (no double deduction). Always returns 200 OK.  

Checkout body: `customer_name`, `customer_phone`, `customer_email` (optional), `notes`, `delivery_address` (optional PK), `coupon_code` (optional), `payment_provider` (`stripe` | `paypal`). Cart from session.  
Checkout success response: `{ "success": true, "order_id": 123, "order_public_id": "ord_...", "order": {...}, "totals": { "subtotal", "discount", "tax", "shipping", "total" }, "payment_client_secret": "...", "payment_url": null }`.  
Error response: `{ "success": false, "errors": { ... } }`.  

Env for payment: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`; optional `CHECKOUT_TAX_RATE`, `CHECKOUT_SHIPPING_FIXED`.

**Coupons**  
- `GET /api/coupons/`, `GET /api/coupons/<code>/` — List/retrieve  
- `POST /api/coupon/apply/` — Validate code for subtotal (body: `code`, `subtotal`); returns discount and total_after  

Order create payload: `customer_name`, `customer_phone`, `customer_email` (optional), `notes`, `delivery_address` (optional PK), `coupon_code` (optional), `items` (list of `{ "product": <id>, "quantity": <n> }`). Checkout uses session cart + same customer fields.

## Models

- **accounts:** `User` (email as username, role, is_active), `Address`
- **products:** `Category`, `Product`, `ProductImage`, `ProductCategory` (M2M with is_primary), `InventoryLog` (signals on stock change)
- **orders:** `Coupon`, `Order`, `OrderItem`, `Payment`

All models use `created_at` / `updated_at`, proper FKs and `on_delete`, and unique constraints (email, slug, SKU, coupon code).

## Admin dashboard

- **URL:** `/admin/` — access only for users with role `admin` or `super_admin` (or superuser).
- **Product management:** CRUD, search, filter by category, stock alerts (low / out / OK).
- **Order management:** List with date hierarchy, search by user/date, edit status from list, OrderItems inline.
- **Coupons:** Create/edit, activate/deactivate (`list_editable`), track usage (`uses_count`).
- **Analytics (index):** Sales (today, 7 days, month, all time), active orders count, coupons used, best-selling products.
- Responsive: viewport meta and basic mobile-friendly grid for analytics.

## Security

- **HTTPS:** `SECURE_SSL_REDIRECT` and `SECURE_PROXY_SSL_HEADER` when not DEBUG (set `SECURE_SSL_REDIRECT=1` in production).
- **CSRF:** Enabled for session auth; secure and HttpOnly cookies when not DEBUG.
- **Passwords:** PBKDF2 (Django default); never logged or stored in plain text.
- **JWT:** Access token (default 60 min) + refresh token (default 7 days); blacklist on refresh. Endpoints: `POST /api/auth/jwt/token/` (body: `email`, `password`), `POST /api/auth/jwt/refresh/` (body: `refresh`), `POST /api/auth/jwt/blacklist/` (body: `refresh`). Env: `JWT_ACCESS_MINUTES`, `JWT_REFRESH_DAYS`.
- **Rate limiting:** Global anon/user throttle; strict `auth` throttle (default 10/hour) for register, login, and JWT obtain. Env: `THROTTLE_ANON`, `THROTTLE_USER`, `THROTTLE_AUTH`.
- **Input:** All validated server-side (serializers); no trust on frontend for payment or prices.
- **Webhooks:** Stripe signature verified; no payment state from client.
- **Secrets:** All keys and DB credentials from environment variables.
- **Logging:** No request bodies in default config; `LOG_LEVEL` env for level.
- **Role-based:** API admin-only routes use `IsAdminRole`; admin site uses `has_permission` (admin/super_admin only).
- **Transactions:** Order creation, checkout, and webhook stock deduction run in DB transactions.
