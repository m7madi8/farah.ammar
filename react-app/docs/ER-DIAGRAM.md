# Nana's Bites — Entity-Relationship Diagram

## Mermaid ER (tables + relationships)

```mermaid
erDiagram
  users ||--o{ orders : "places"
  users ||--o{ addresses : "has"
  categories ||--o{ product_categories : "has"
  products ||--o{ product_categories : "belongs to"
  products ||--o{ product_images : "has"
  products ||--o{ order_items : "ordered as"
  products ||--o{ inventory_logs : "logged"
  orders ||--o{ order_items : "contains"
  orders ||--o{ payments : "has"
  orders }o--|| addresses : "delivery"
  orders }o--o| coupons : "uses"
  addresses }o--o| users : "belongs to"
  payments }o--o| orders : "for"
  inventory_logs }o--o| users : "created by"

  users {
    bigserial id PK
    varchar email UK
    varchar password_hash
    varchar full_name
    varchar phone
    char role
    timestamptz created_at
    timestamptz updated_at
  }

  categories {
    bigserial id PK
    varchar slug UK
    varchar name_en
    varchar name_ar
    int sort_order
    boolean is_active
  }

  products {
    bigserial id PK
    varchar slug UK
    varchar sku UK
    varchar name_en
    varchar name_ar
    numeric price
    int stock_quantity
    int sort_order
    boolean is_active
    timestamptz created_at
  }

  product_images {
    bigserial id PK
    bigint product_id FK
    varchar url
    boolean is_hero
    int sort_order
  }

  product_categories {
    bigint product_id PK,FK
    bigint category_id PK,FK
    boolean is_primary
  }

  addresses {
    bigserial id PK
    bigint user_id FK
    varchar full_name
    varchar phone
    varchar line1
    varchar city
    char country
  }

  coupons {
    bigserial id PK
    varchar code UK
    varchar discount_type
    numeric discount_value
    timestamptz valid_from
    timestamptz valid_until
  }

  orders {
    bigserial id PK
    varchar public_id UK
    bigint user_id FK
    varchar customer_name
    varchar customer_phone
    numeric subtotal
    numeric total
    varchar status
    bigint coupon_id FK
    timestamptz created_at
  }

  order_items {
    bigserial id PK
    bigint order_id FK
    bigint product_id FK
    int quantity
    numeric unit_price_at_purchase
    numeric total
  }

  payments {
    bigserial id PK
    bigint order_id FK
    varchar provider
    varchar external_id
    varchar status
    numeric amount
    boolean webhook_verified
    jsonb webhook_payload
  }

  inventory_logs {
    bigserial id PK
    bigint product_id FK
    int change_qty
    int quantity_after
    varchar reason
    varchar reference_type
    bigint reference_id
    bigint created_by FK
    timestamptz created_at
  }
```

---

## Tables and relationships (summary)

| Table               | Primary key     | Main FKs / relationships |
|---------------------|-----------------|---------------------------|
| **users**           | id              | —                         |
| **categories**      | id              | —                         |
| **products**        | id              | —                         |
| **product_images**  | id              | product_id → products     |
| **product_categories** | (product_id, category_id) | product_id → products, category_id → categories |
| **addresses**       | id              | user_id → users           |
| **coupons**         | id              | —                         |
| **orders**          | id              | user_id → users, delivery_address_id → addresses, coupon_id → coupons |
| **order_items**     | id              | order_id → orders, product_id → products |
| **payments**        | id              | order_id → orders         |
| **inventory_logs** | id              | product_id → products, created_by → users |

---

## Relationship rules

- **users ↔ orders**: 1 user : 0..n orders (guest orders have `user_id` NULL).
- **users ↔ addresses**: 1 user : 0..n addresses.
- **products ↔ categories**: n : m via `product_categories`; optional `is_primary` per product.
- **products ↔ product_images**: 1 product : n images; one image per product can be `is_hero`.
- **orders ↔ order_items**: 1 order : n items; each item stores `unit_price_at_purchase`.
- **orders ↔ payments**: 1 order : n payments (e.g. one COD, or Stripe + refund).
- **orders ↔ addresses**: optional `delivery_address_id`; snapshot in `shipping_*` for history.
- **orders ↔ coupons**: optional `coupon_id`; one coupon per order.
- **products ↔ inventory_logs**: 1 product : n logs; `change_qty` and `quantity_after` for stock.

---

## Business rules (from schema comments)

1. **Price at purchase**: `order_items.unit_price_at_purchase` and `total`; do not use `products.price` for past orders.
2. **Stock**: `products.stock_quantity`; use `inventory_logs` for movements (sale, restock, adjustment, return, damage).
3. **Payments**: Multiple providers per order; `external_id` for idempotency; `webhook_verified` and `webhook_payload` for webhook handling.
4. **Guest checkout**: `orders.user_id` and `orders.delivery_address_id` can be NULL; use `customer_*` and `shipping_*` snapshot.
5. **Product soft-delete**: Prefer `products.is_active = false`; `order_items.product_id` can be SET NULL if product is removed.
6. **Coupons**: `discount_type` percent or fixed; `valid_from` / `valid_until`; `max_uses` and `uses_count` for caps.
