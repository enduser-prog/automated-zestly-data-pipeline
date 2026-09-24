-- ZESTLY DATABASE SCHEMA

-- CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    customer_name   VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    city            VARCHAR(100),
    state           VARCHAR(100),
    signup_month    DATE NOT NULL
);

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(150) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    cost_price      NUMERIC(10,2) NOT NULL CHECK (cost_price >= 0),
    selling_price   NUMERIC(10,2) NOT NULL CHECK (selling_price >= 0),
    stock_quantity  INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_level   INT NOT NULL DEFAULT 10
);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(customer_id),
    product_id      INT NOT NULL REFERENCES products(product_id),
    order_date      DATE NOT NULL,
    quantity        INT,
    payment_method  VARCHAR(50),
    order_source    VARCHAR(50),
    discount_pct    NUMERIC(5,2),
    order_status    VARCHAR(20)
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);