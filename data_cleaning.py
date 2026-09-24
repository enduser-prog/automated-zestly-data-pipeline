import statistics
import psycopg2
from psycopg2.extras import execute_values
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SSLMODE

VALID_SOURCES = {"website": "Website", "app": "App", "in-store": "In-Store"}


def connect():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, sslmode=DB_SSLMODE
    )


def add_quality_column(cur):
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS data_quality_flag VARCHAR(20);")


def fetch_uncleaned(cur):
    cur.execute("""
        SELECT order_id, customer_id, product_id, order_date, quantity,
               payment_method, order_source, discount_pct, order_status
        FROM orders
        WHERE data_quality_flag IS NULL
        ORDER BY order_id;
    """)
    return cur.fetchall()


def median_quantity(cur):
    cur.execute("SELECT quantity FROM orders WHERE quantity IS NOT NULL;")
    values = [r[0] for r in cur.fetchall()]
    return int(round(statistics.median(values))) if values else 1


def normalize_source(source):
    if source is None:
        return None, False
    cleaned = source.strip().lower()
    canonical = VALID_SOURCES.get(cleaned)
    if canonical is None:
        return source, False
    return canonical, canonical != source


def clean_rows(rows, fallback_qty):
    seen_keys = set()
    updates = []

    for row in rows:
        (order_id, customer_id, product_id, order_date, quantity,
         payment_method, order_source, discount_pct, order_status) = row

        corrected = False

        if quantity is None:
            quantity = fallback_qty
            corrected = True

        clean_source, source_changed = normalize_source(order_source)
        if source_changed:
            corrected = True
        order_source = clean_source

        key = (customer_id, product_id, order_date, quantity,
               payment_method, order_source, discount_pct, order_status)

        if key in seen_keys:
            flag = "Deduplicated"
        else:
            seen_keys.add(key)
            flag = "Corrected" if corrected else "Clean"

        updates.append((order_id, quantity, order_source, flag))

    return updates


def apply_updates(cur, updates):
    execute_values(
        cur,
        """UPDATE orders AS o
           SET quantity = t.quantity,
               order_source = t.order_source,
               data_quality_flag = t.flag
           FROM (VALUES %s) AS t(order_id, quantity, order_source, flag)
           WHERE o.order_id = t.order_id""",
        updates
    )


def main():
    conn = connect()
    cur = conn.cursor()

    add_quality_column(cur)
    conn.commit()

    fallback_qty = median_quantity(cur)
    rows = fetch_uncleaned(cur)

    if not rows:
        print("No uncleaned rows found.")
        cur.close()
        conn.close()
        return

    updates = clean_rows(rows, fallback_qty)
    apply_updates(cur, updates)

    conn.commit()
    cur.close()
    conn.close()

    flags = [u[3] for u in updates]
    print(f"Cleaned {len(updates)} rows — "
          f"Clean: {flags.count('Clean')}, "
          f"Corrected: {flags.count('Corrected')}, "
          f"Deduplicated: {flags.count('Deduplicated')}.")


if __name__ == "__main__":
    main()
