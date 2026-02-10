-- =============================================================================
-- Nana's Bites — PostgreSQL Schema (Production E‑commerce)
-- Aligned with frontend: products (slug, i18n), orders (name, phone, address),
-- cart/order items (productId, quantity, price at purchase).
-- =============================================================================

-- Extensions (optional, for UUIDs and crypto for webhook signing)
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USERS
-- Guest checkout supported; user_id on orders nullable.
-- =============================================================================
CREATE TABLE users (
  id                BIGSERIAL PRIMARY KEY,
  email             VARCHAR(255) UNIQUE NOT NULL,
  password_hash     VARCHAR(255),                    -- NULL if OAuth-only
  full_name         VARCHAR(255) NOT NULL,
  phone             VARCHAR(50),
  preferred_lang     CHAR(2) DEFAULT 'en',            -- en, ar
  role              VARCHAR(20) NOT NULL DEFAULT 'customer',  -- customer, admin, super_admin
  is_active         BOOLEAN NOT NULL DEFAULT true,
  email_verified_at TIMESTAMPTZ,
  last_login_at     TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_users_role CHECK (role IN ('customer', 'admin', 'super_admin')),
  CONSTRAINT chk_users_lang CHECK (preferred_lang IN ('en', 'ar'))
);

COMMENT ON TABLE users IS 'Registered users; orders can be guest (user_id NULL) or linked.';

-- =============================================================================
-- CATEGORIES
-- e.g. boxes (Dumplings), sauces, chopsticks — maps to frontend filter keys.
-- =============================================================================
CREATE TABLE categories (
  id          BIGSERIAL PRIMARY KEY,
  slug        VARCHAR(100) UNIQUE NOT NULL,          -- e.g. boxes, sauces, chopsticks
  name_en     VARCHAR(255) NOT NULL,
  name_ar     VARCHAR(255),
  description TEXT,
  sort_order  INT NOT NULL DEFAULT 0,
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE categories IS 'Product categories for filtering; slug used in frontend.';

-- =============================================================================
-- PRODUCTS
-- Core product entity; price and stock here; order_items store price at purchase.
-- =============================================================================
CREATE TABLE products (
  id              BIGSERIAL PRIMARY KEY,
  slug            VARCHAR(200) UNIQUE NOT NULL,     -- URL-safe, e.g. dumplings-chicken
  sku             VARCHAR(100) UNIQUE,              -- optional internal SKU
  name_en         VARCHAR(255) NOT NULL,
  name_ar         VARCHAR(255),
  description_en  TEXT,
  description_ar  TEXT,
  badge           VARCHAR(50),                     -- Signature, Sauce, Accessory (display only)
  details         JSONB DEFAULT '[]',             -- list of i18n keys or text for "What's inside"
  price           NUMERIC(10,2) NOT NULL,
  currency        CHAR(3) NOT NULL DEFAULT 'ILS',  -- ₪
  cost_price      NUMERIC(10,2),                   -- optional, for margin reporting
  stock_quantity  INT NOT NULL DEFAULT 0,          -- 0 = no stock tracking / allow oversell
  allow_backorder BOOLEAN NOT NULL DEFAULT false,
  sort_order      INT NOT NULL DEFAULT 0,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_products_price CHECK (price >= 0),
  CONSTRAINT chk_products_stock CHECK (stock_quantity >= 0)
);

COMMENT ON TABLE products IS 'Products; price here is current. order_items store price at purchase time.';
COMMENT ON COLUMN products.stock_quantity IS 'If 0 and no backorder, frontend may hide or show out-of-stock.';
COMMENT ON COLUMN products.details IS 'Array of detail keys or text for product page "What\'s inside".';

-- =============================================================================
-- PRODUCT_CATEGORIES (many-to-many)
-- A product can belong to multiple categories.
-- =============================================================================
CREATE TABLE product_categories (
  product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  is_primary  BOOLEAN NOT NULL DEFAULT false,       -- primary category for filters
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (product_id, category_id)
);
-- One primary category per product (enforced by partial unique index)
CREATE UNIQUE INDEX uq_product_primary_category ON product_categories(product_id) WHERE is_primary = true;

COMMENT ON TABLE product_categories IS 'Product–category many-to-many; is_primary for default filter.';

-- =============================================================================
-- PRODUCT_IMAGES
-- Multiple images per product; one can be hero (for product page).
-- =============================================================================
CREATE TABLE product_images (
  id         BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  url        VARCHAR(1024) NOT NULL,               -- full URL or path, e.g. /img/1.png
  alt_en     VARCHAR(255),
  alt_ar     VARCHAR(255),
  sort_order INT NOT NULL DEFAULT 0,
  is_hero    BOOLEAN NOT NULL DEFAULT false,       -- used as main image on product page
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- One hero image per product (partial unique index)
CREATE UNIQUE INDEX uq_product_hero_image ON product_images(product_id) WHERE is_hero = true;

COMMENT ON TABLE product_images IS 'Product images; is_hero used for product detail page.';

-- =============================================================================
-- ADDRESSES
-- Delivery/billing addresses; can be user-linked or one-off on order.
-- =============================================================================
CREATE TABLE addresses (
  id           BIGSERIAL PRIMARY KEY,
  user_id      BIGINT REFERENCES users(id) ON DELETE SET NULL,
  label        VARCHAR(100),                      -- Home, Work, etc.
  full_name    VARCHAR(255) NOT NULL,
  phone        VARCHAR(50) NOT NULL,
  line1        VARCHAR(255) NOT NULL,
  line2        VARCHAR(255),
  city         VARCHAR(100) NOT NULL,
  state_region VARCHAR(100),
  postal_code  VARCHAR(20),
  country      CHAR(2) NOT NULL DEFAULT 'IL',
  is_default   BOOLEAN NOT NULL DEFAULT false,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE addresses IS 'Addresses; user_id NULL for guest one-off addresses stored on order.';

-- =============================================================================
-- COUPONS
-- Discount codes; can be percent or fixed amount; optional validity window.
-- =============================================================================
CREATE TABLE coupons (
  id              BIGSERIAL PRIMARY KEY,
  code            VARCHAR(50) UNIQUE NOT NULL,
  description     VARCHAR(255),
  discount_type   VARCHAR(20) NOT NULL,            -- percent, fixed
  discount_value  NUMERIC(10,2) NOT NULL,
  min_order_total NUMERIC(10,2) DEFAULT 0,
  max_uses        INT,                            -- NULL = unlimited
  uses_count      INT NOT NULL DEFAULT 0,
  valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
  valid_until     TIMESTAMPTZ,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_coupons_type CHECK (discount_type IN ('percent', 'fixed')),
  CONSTRAINT chk_coupons_value CHECK (discount_value > 0),
  CONSTRAINT chk_coupons_uses CHECK (max_uses IS NULL OR max_uses >= 0)
);

COMMENT ON TABLE coupons IS 'Discount codes; discount_type percent (0–100) or fixed amount.';

-- =============================================================================
-- ORDERS
-- Order header; guest orders have user_id NULL, name/phone/address from form.
-- =============================================================================
CREATE TABLE orders (
  id              BIGSERIAL PRIMARY KEY,
  public_id       VARCHAR(32) UNIQUE NOT NULL,     -- e.g. ord_abc123 for customer-facing
  user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
  -- Guest / snapshot fields (from checkout form)
  customer_name   VARCHAR(255) NOT NULL,
  customer_phone  VARCHAR(50) NOT NULL,
  customer_email  VARCHAR(255),
  delivery_address_id BIGINT REFERENCES addresses(id) ON DELETE SET NULL,
  -- Snapshot of address at order time (denormalized for history)
  shipping_line1  VARCHAR(255),
  shipping_line2  VARCHAR(255),
  shipping_city   VARCHAR(100),
  shipping_region VARCHAR(100),
  shipping_postal VARCHAR(20),
  shipping_country CHAR(2),
  notes           TEXT,
  -- Totals and discount
  subtotal        NUMERIC(12,2) NOT NULL,
  discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
  total           NUMERIC(12,2) NOT NULL,
  currency        CHAR(3) NOT NULL DEFAULT 'ILS',
  coupon_id       BIGINT REFERENCES coupons(id) ON DELETE SET NULL,
  -- Status and fulfillment
  status          VARCHAR(30) NOT NULL DEFAULT 'pending',
  paid_at         TIMESTAMPTZ,
  fulfilled_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_orders_total CHECK (total >= 0),
  CONSTRAINT chk_orders_status CHECK (status IN (
    'pending', 'confirmed', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
  ))
);

COMMENT ON TABLE orders IS 'Order header; guest orders use customer_* and shipping_* snapshot. Price at purchase in order_items.';
COMMENT ON COLUMN orders.public_id IS 'Short unique id for invoices and customer reference.';

-- =============================================================================
-- ORDER_ITEMS
-- Line items; store product snapshot and unit_price at purchase time.
-- =============================================================================
CREATE TABLE order_items (
  id                   BIGSERIAL PRIMARY KEY,
  order_id             BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id           BIGINT REFERENCES products(id) ON DELETE SET NULL,  -- SET NULL if product deleted
  product_snapshot     JSONB,                             -- { name_en, name_ar, sku } at order time
  quantity             INT NOT NULL,
  unit_price_at_purchase NUMERIC(10,2) NOT NULL,
  total                NUMERIC(12,2) NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_order_items_qty CHECK (quantity > 0),
  CONSTRAINT chk_order_items_price CHECK (unit_price_at_purchase >= 0)
);

COMMENT ON TABLE order_items IS 'Line items; unit_price_at_purchase preserves price at order time. product_snapshot for display if product removed.';

-- =============================================================================
-- PAYMENTS
-- Multiple providers (Stripe, PayPal, COD, etc.); webhook verification support.
-- =============================================================================
CREATE TABLE payments (
  id                BIGSERIAL PRIMARY KEY,
  order_id          BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  provider          VARCHAR(30) NOT NULL,           -- stripe, paypal, cod, bank_transfer
  external_id        VARCHAR(255),                  -- provider payment/charge id
  status            VARCHAR(30) NOT NULL DEFAULT 'pending',
  amount            NUMERIC(12,2) NOT NULL,
  currency          CHAR(3) NOT NULL DEFAULT 'ILS',
  metadata          JSONB DEFAULT '{}',             -- provider-specific (payment_intent_id, etc.)
  webhook_verified  BOOLEAN NOT NULL DEFAULT false,
  webhook_payload   JSONB,                         -- last webhook body for debugging
  webhook_received_at TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_payments_provider CHECK (provider IN ('stripe', 'paypal', 'cod', 'bank_transfer', 'other')),
  CONSTRAINT chk_payments_status CHECK (status IN ('pending', 'authorized', 'captured', 'failed', 'cancelled', 'refunded'))
);

COMMENT ON TABLE payments IS 'Payments per order; support multiple providers. webhook_verified and webhook_payload for idempotent webhook handling.';
COMMENT ON COLUMN payments.external_id IS 'Provider charge/payment id for idempotency and lookups.';

-- =============================================================================
-- INVENTORY_LOGS
-- Stock movements for auditing and stock management.
-- =============================================================================
CREATE TABLE inventory_logs (
  id          BIGSERIAL PRIMARY KEY,
  product_id  BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  change_qty  INT NOT NULL,                        -- positive = in, negative = out
  quantity_after INT NOT NULL,
  reason      VARCHAR(50) NOT NULL,                -- sale, restock, adjustment, return, damage
  reference_type VARCHAR(30),                      -- order, manual, purchase_order
  reference_id   BIGINT,                           -- e.g. order_id
  notes       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by  BIGINT REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT chk_inv_change CHECK (change_qty != 0),
  CONSTRAINT chk_inv_reason CHECK (reason IN ('sale', 'restock', 'adjustment', 'return', 'damage', 'transfer'))
);

COMMENT ON TABLE inventory_logs IS 'Stock movement log; quantity_after = stock after this change.';

-- =============================================================================
-- INDEXES (performance)
-- =============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role) WHERE is_active = true;

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_active ON categories(is_active) WHERE is_active = true;

CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = true;
CREATE INDEX idx_products_sort ON products(sort_order);
CREATE INDEX idx_products_sku ON products(sku) WHERE sku IS NOT NULL;

CREATE INDEX idx_product_categories_category ON product_categories(category_id);
CREATE INDEX idx_product_categories_primary ON product_categories(product_id) WHERE is_primary = true;

CREATE INDEX idx_product_images_product ON product_images(product_id);
CREATE INDEX idx_product_images_hero ON product_images(product_id) WHERE is_hero = true;

CREATE INDEX idx_addresses_user ON addresses(user_id) WHERE user_id IS NOT NULL;

CREATE INDEX idx_coupons_code ON coupons(code) WHERE is_active = true;
CREATE INDEX idx_coupons_valid ON coupons(valid_from, valid_until) WHERE is_active = true;

CREATE INDEX idx_orders_public_id ON orders(public_id);
CREATE INDEX idx_orders_user ON orders(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_orders_phone ON orders(customer_phone);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id) WHERE product_id IS NOT NULL;

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_provider_external ON payments(provider, external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_payments_status ON payments(status);

CREATE INDEX idx_inventory_logs_product ON inventory_logs(product_id);
CREATE INDEX idx_inventory_logs_created ON inventory_logs(created_at DESC);
CREATE INDEX idx_inventory_logs_reference ON inventory_logs(reference_type, reference_id) WHERE reference_id IS NOT NULL;

-- =============================================================================
-- UPDATED_AT TRIGGERS (optional)
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_addresses_updated_at BEFORE UPDATE ON addresses FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_coupons_updated_at BEFORE UPDATE ON coupons FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER tr_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE PROCEDURE set_updated_at();