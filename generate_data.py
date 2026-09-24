import random
from datetime import date, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SSLMODE

fake = Faker("en_IN")

# ---- RUNS EVERY 5 DAYS (via GitHub Actions) ----
NEW_ORDERS_PER_RUN = 1000
REPEAT_ORDER_PROBABILITY = 0.4
NEW_CUSTOMERS_NEEDED = int(NEW_ORDERS_PER_RUN * (1 - REPEAT_ORDER_PROBABILITY) * 1.1)

PAYMENT_METHODS = ["UPI", "Card", "COD", "NetBanking"]
ORDER_SOURCES = ["Website", "App", "In-Store"]
ORDER_STATUSES = ["Delivered", "Cancelled", "Returned"]
STATUS_WEIGHTS = [90, 6, 4]


def connect():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, sslmode=DB_SSLMODE
    )


def create_new_customers(cur, n):
    seen_emails = set()
    rows = []
    while len(rows) < n:
        email = fake.email().lower()
        if email in seen_emails:
            continue
        seen_emails.add(email)
        rows.append((
            fake.name(), email, fake.city(), fake.state(),
            date.today().replace(day=1)
        ))

    result = execute_values(
        cur,
        """INSERT INTO customers (customer_name, email, city, state, signup_month)
           VALUES %s
           ON CONFLICT (email) DO NOTHING
           RETURNING customer_id""",
        rows,
        fetch=True
    )
    return [r[0] for r in result]


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
        d = today - timedelta(days=random.randint(0, 5))
        weight = 1.0
        if d.weekday() >= 5:
            weight *= 1.6
        if d.month in (10, 11, 12):
            weight *= 1.5
        if random.random() < weight / 1.6:
            return d


def build_orders(n, existing_customer_ids, new_customer_ids, product_ids, weights):
    used_customers = list(existing_customer_ids)
    next_new = 0
    rows = []

    for _ in range(n):
        if used_customers and random.random() < REPEAT_ORDER_PROBABILITY:
            cust_id = random.choice(used_customers)
        elif next_new < len(new_customer_ids):
            cust_id = new_customer_ids[next_new]
            next_new += 1
            used_customers.append(cust_id)
        else:
            cust_id = random.choice(used_customers)

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

    return rows


def insert_orders(cur, rows):
    execute_values(
        cur,
        """INSERT INTO orders
           (customer_id, product_id, order_date, quantity, payment_method,
            order_source, discount_pct, order_status)
           VALUES %s""",
        rows
    )


def main():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products;")
    if cur.fetchone()[0] == 0:
        print("No products found — run seed_data.py first.")
        cur.close()
        conn.close()
        return

    cur.execute("SELECT customer_id FROM customers;")
    existing_customer_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT product_id FROM products;")
    product_ids = [r[0] for r in cur.fetchall()]
    weights = [random.paretovariate(1.5) for _ in product_ids]

    new_customer_ids = create_new_customers(cur, NEW_CUSTOMERS_NEEDED)
    conn.commit()

    order_rows = build_orders(
        NEW_ORDERS_PER_RUN, existing_customer_ids, new_customer_ids, product_ids, weights
    )
    insert_orders(cur, order_rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {NEW_ORDERS_PER_RUN} new orders ({len(new_customer_ids)} new customers created).")


if __name__ == "__main__":
    main()