import random
from datetime import date, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SSLMODE

fake = Faker("en_IN")

SEED_ORDERS = 5000
REPEAT_ORDER_PROBABILITY = 0.4
# Estimate how many unique customers you'll actually need
NUM_CUSTOMERS = int(SEED_ORDERS * (1 - REPEAT_ORDER_PROBABILITY) * 1.1)  # small buffer

CATEGORIES = {
    "Groceries": (50, 500),
    "Fashion": (299, 2999),
    "Electronics": (999, 50000),
    "Home & Kitchen": (199, 5999),
    "Beauty": (99, 1999),
}

PRICE_POINTS = [49, 99, 149, 199, 249, 299, 399, 499, 599, 699, 999,
                1499, 1999, 2499, 2999, 4999, 9999, 14999, 19999, 29999, 49999]

PAYMENT_METHODS = ["UPI", "Card", "COD", "NetBanking"]
ORDER_SOURCES = ["Website", "App", "In-Store"]
ORDER_STATUSES = ["Delivered", "Cancelled", "Returned"]
STATUS_WEIGHTS = [90, 6, 4]


def connect():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, sslmode=DB_SSLMODE
    )


def wipe_existing_data(cur):
    cur.execute("TRUNCATE orders, customers, products RESTART IDENTITY CASCADE;")


def seed_products(cur):
    rows = []
    for category, (lo, hi) in CATEGORIES.items():
        valid_prices = [p for p in PRICE_POINTS if lo <= p <= hi]
        for _ in range(10):
            price = random.choice(valid_prices)
            cost = round(price * random.uniform(0.55, 0.8), 2)
            stock = random.randint(0, 200)
            reorder = random.randint(10, 30)
            name = f"{fake.word().title()} {category.split()[0]}"
            rows.append((name, category, cost, price, stock, reorder))

    execute_values(
        cur,
        """INSERT INTO products
           (product_name, category, cost_price, selling_price, stock_quantity, reorder_level)
           VALUES %s""",
        rows
    )


def seed_customers(cur, n):
    """Bulk-create n customers in one round trip, return their IDs."""
    seen_emails = set()
    rows = []
    while len(rows) < n:
        email = fake.email().lower()
        if email in seen_emails:
            continue
        seen_emails.add(email)
        name = fake.name()
        city = fake.city()
        state = fake.state()
        signup_month = date.today().replace(day=1)
        rows.append((name, email, city, state, signup_month))

    customer_ids = execute_values(
        cur,
        """INSERT INTO customers (customer_name, email, city, state, signup_month)
           VALUES %s
           ON CONFLICT (email) DO NOTHING
           RETURNING customer_id""",
        rows,
        fetch=True
    )
    return [r[0] for r in customer_ids]


def messy_quantity():
    if random.random() < 0.03:
        return None
    return random.randint(1, 5)


def messy_source():
    source = random.choice(ORDER_SOURCES)
    if random.random() < 0.15:
        source = random.choice([source.upper(), source.lower(), f" {source} "])
    return source


def random_order_date():
    today = date.today()
    while True:
        d = today - timedelta(days=random.randint(0, 150))
        weight = 1.0
        if d.weekday() >= 5:
            weight *= 1.6
        if d.month in (10, 11, 12):
            weight *= 1.5
        if random.random() < weight / 1.6:
            return d


def seed_orders(cur, n, customer_ids, product_ids, weights):
    insert_sql = """INSERT INTO orders
        (customer_id, product_id, order_date, quantity, payment_method,
         order_source, discount_pct, order_status)
        VALUES %s"""

    used_customers = []
    rows = []

    for _ in range(n):
        if used_customers and random.random() < REPEAT_ORDER_PROBABILITY:
            cust_id = random.choice(used_customers)
        else:
            cust_id = customer_ids[len(used_customers) % len(customer_ids)]
            used_customers.append(cust_id)

        prod_id = random.choices(product_ids, weights=weights, k=1)[0]

        values = (
            cust_id, prod_id, random_order_date(), messy_quantity(),
            random.choice(PAYMENT_METHODS), messy_source(),
            random.choice([0, 0, 0, 5, 10, 15, 20]),
            random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0],
        )
        rows.append(values)
        if random.random() < 0.02:
            rows.append(values)

    execute_values(cur, insert_sql, rows)


def main():
    conn = connect()
    cur = conn.cursor()

    wipe_existing_data(cur)
    conn.commit()

    seed_products(cur)
    conn.commit()

    cur.execute("SELECT product_id FROM products;")
    product_ids = [r[0] for r in cur.fetchall()]
    weights = [random.paretovariate(1.5) for _ in product_ids]

    customer_ids = seed_customers(cur, NUM_CUSTOMERS)
    conn.commit()

    seed_orders(cur, SEED_ORDERS, customer_ids, product_ids, weights)
    conn.commit()

    cur.close()
    conn.close()
    print(f"Seed complete: existing data wiped, 50 products, {len(customer_ids)} customers, {SEED_ORDERS} orders created.")


if __name__ == "__main__":
    main()