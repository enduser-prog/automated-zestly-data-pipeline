# Zestly — Automated E-Commerce Data Pipeline
( https://automated-zestly-data-pipeline-yvhmeweq73qp9n4ufbqerg.streamlit.app/ )---> link to live dashboard 

A self-running data pipeline that generates messy, realistic e-commerce orders, cleans them on a schedule, rebuilds an analytics layer, and serves the results through a live Streamlit dashboard — with zero manual intervention after setup.

This isn't a one-off analysis of a static CSV. It's a small production-style system: **data generation → cleaning → transformation → visualization**, running on autopilot via GitHub Actions.

<img width="943" height="308" alt="Screenshot 2026-09-27 231135" src="https://github.com/user-attachments/assets/2837ee50-8d59-45aa-a155-bd63af3204d3" />

---
Aiven database where data will be stored

<img width="943" height="279" alt="image" src="https://github.com/user-attachments/assets/ae20a6a4-bffa-427b-a71b-1c81581ce524" />


## The brief

**Zestly** is a fictional e-commerce brand used as the scenario for this project. The premise: Zestly's team doesn't want to wait on someone to manually pull, clean, and refresh sales reports every week — they want to open one link and see the current state of the business, fully caught up, every time.

That requirement is what shapes the whole system. It's not enough to build a dashboard once; the pipeline behind it has to keep collecting new orders, catching data-entry problems, and rebuilding the numbers on its own schedule — so that whenever someone on the Zestly team checks in, what they see reflects the business *right now*, not the last time an analyst had time to update a spreadsheet.

---

## Why this exists

Most portfolio data projects analyze a dataset once and stop. This project asks a different question: *what does it take to keep a dashboard trustworthy when new, imperfect data keeps arriving?*

So instead of a clean Kaggle CSV, the pipeline deliberately generates data the way real systems produce it — with missing values, inconsistent formatting, and duplicate rows — and then has to detect and fix those problems automatically, every single run, without a human checking each time.

---

## How it actually works

```
┌─────────────────┐     every 5 days (cron)      ┌──────────────────┐
│  generate_data.py │ ─────────────────────────▶ │   PostgreSQL DB   │
│  (new messy       │                             │  (Aiven, managed) │
│   orders +        │                             └─────────┬────────┘
│   customers)       │                                       │
└─────────────────┘                                       ▼
                                                   ┌──────────────────┐
                                                   │ data_cleaning.py  │
                                                   │ fixes/flags rows  │
                                                   └─────────┬────────┘
                                                              ▼
                                                   ┌──────────────────┐
                                                   │  sales_data.py    │
                                                   │ rebuilds analytics│
                                                   │ table + 30 KPIs   │
                                                   └─────────┬────────┘
                                                              ▼
                                                   ┌──────────────────┐
                                                   │ zestly_dashboard  │
                                                   │   (Streamlit)     │
                                                   └──────────────────┘
```

**1. `seed_data.py` — one-time bootstrap**
Wipes and rebuilds the schema, then generates 50 products across 5 categories and ~5,000 initial orders using `Faker`. Orders are seeded with realistic *defects on purpose*: ~3% missing quantities, ~15% inconsistently cased/whitespaced order sources (`"App"`, `"app "`, `"APP"`), and a small rate of accidental duplicate rows.

**2. `generate_data.py` — the recurring job**
Runs every 5 days via a scheduled GitHub Action. Adds 1,000 new orders on top of the existing database, mixing repeat customers (40% probability) with newly generated ones — mimicking how a real store's customer base grows over time. Injects the same class of messiness as the seed step, so the cleaning logic always has real work to do.

**3. `data_cleaning.py` — automated quality control**
Scans only the rows that haven't been processed yet (`data_quality_flag IS NULL`), then:
- Fills missing quantities with the **median** quantity across all orders (not a hardcoded guess)
- Normalizes order source casing/whitespace to a canonical form
- Detects duplicate orders by a composite key and flags them for exclusion
- Tags every row `Clean`, `Corrected`, or `Deduplicated` — so nothing is silently altered; the audit trail stays in the database

**4. `sales_data.py` — the transformation layer**
Joins customers, products, and orders into one denormalized `analytics_sales` table, computing revenue, cost, gross profit, margin, repeat-customer status, and customer tenure at the row level. It also calculates **30 separate business KPIs** — from Customer Lifetime Value and Revenue Pareto Ratio to cancellation rate by payment method — as a sanity-check console report each run, separate from what the dashboard renders live.

**5. `zestly_dashboard.py` — the interface**
A 7-page Streamlit app (Overview, Sales, Profitability, Products, Customers, Orders, Data Quality) with period-over-period comparisons, a built-in search across products/categories/orders/customers, and CSV export. The **Data Quality page** is the one most people skip building — it visualizes duplicate rates and missing-value counts over time, because a dashboard that hides its own data problems isn't one you should trust.

The whole cycle (steps 2–4) repeats automatically every 5 days through the GitHub Actions workflow, authenticating with **GitHub Secrets** rather than any credential stored in the codebase — so the pipeline keeps running unattended without the database password ever touching the repository.

---

## The 30 KPIs calculated in `sales_data.py`

Every run, after the `analytics_sales` table is rebuilt, the script computes 30 business metrics as a console-logged sanity check — grouped here by what question each one answers:

**Revenue & order value**
Total Revenue · Month-over-Month Revenue Growth % · Average Order Value · Median Order Value · Average Items per Order

**Customers**
Customer Lifetime Value (CLV) · Repeat Customer Rate % · New vs. Returning Revenue Split · New Customer Signups per Month · Average Customer Tenure at Purchase · AOV: New vs. Repeat Customers · Days Since Last Order (avg. recency)

**Profitability**
Gross Profit Margin % · Category Revenue vs. Margin Comparison

**Products & inventory**
Top-Selling Product · Best-Performing Category · Inventory Turnover Rate · Slow-Moving Products (bottom 20% by units sold) · Product Revenue Concentration (top 20% of products)

**Order fulfillment**
Order Fulfillment Rate % · Cancellation Rate % · Return Rate % · Cancellation Rate by Payment Method

**Discounts & channels**
Discount Utilization Rate % · Average Discount Applied % · Revenue by Payment Method · Revenue by Order Source · Weekday vs. Weekend Revenue Split

**Concentration & geography**
Top Cities by Revenue · Revenue Pareto Ratio (share of revenue from the top 20% of customers)

Worth being precise about one thing: these 30 are printed to the console as a run-by-run audit log, not queried directly by the dashboard. The dashboard computes its own live version of the overlapping metrics (revenue, margin, repeat rate, etc.) directly from the `analytics_sales` table, filtered to whatever date range is selected — so the two layers double-check each other rather than one blindly trusting the other.

---

## How the dashboard is organized

Each of the 7 pages in `zestly_dashboard.py` is scoped to one business question, with its own KPI row and supporting charts:

| Page | KPI row | Supporting views |
|---|---|---|
| **Overview** | Revenue, Orders, Avg Order Value, Customers | Profit trend, top customer segments by category, best-selling products, most active weekday, repeat-customer gauge |
| **Sales** | Booked Revenue (all statuses), Units Sold, Items per Order, Avg Daily Revenue | Daily revenue trend, revenue by category, revenue by weekday, best trading days |
| **Profitability** | Gross Margin, Profit per Order, Profit per Unit, Loss-Making Orders %, Value Lost to Negative Margin | Margin trend, profit by category, margin by category, lowest-margin products |
| **Products** | Active Products, Avg Selling Price, Top-5 Revenue Share, Loss-Making Products | Top products by revenue, units sold by category, top products by profit, slow movers |
| **Customers** | New Customers, Repeat Customers, Orders per Customer, Revenue per Customer | Active customers per day, new vs. repeat revenue split, customers by category, top customers |
| **Orders** | Orders Placed, Delivered Orders, Delivery Rate, Undelivered Rate | Orders per day, order status breakdown, order value distribution, orders by category |
| **Data Quality** | Total Records, Duplicates Removed, Duplicate Rate, Rows with Missing Values | Duplicates per day, records by quality flag, missing values by field |

Every page compares the selected date range against the equivalent prior period automatically, and a single search bar in the sidebar cuts across all pages — searching products, categories, orders, and customers at once regardless of which page is currently open.

---

## Tech stack

| Layer | Tool |
|---|---|
| Data generation | Python, `Faker` |
| Database | PostgreSQL (Aiven, managed) |
| Data access | `psycopg2` (writes), `SQLAlchemy` + `pandas` (reads) |
| Scheduling | GitHub Actions (`cron`, plus manual dispatch) |
| Dashboard | Streamlit, Plotly |
| Config | `python-dotenv` / `st.secrets`, environment-variable driven |

---

## Honest scope

- **The data is synthetic**, generated with `Faker`, not real transactions. The point of the project is the *pipeline mechanics* — automated scheduling, data-quality handling, and analytics rebuilding — not real-world sales patterns.
- **Cleaning rules are intentionally simple** (median imputation, string normalization, exact-match deduplication). A production system would likely need fuzzy deduplication and more nuanced imputation, but the goal here was a clear, auditable baseline rather than an opaque one.
- **`analytics_sales` is fully rebuilt each run** (`if_exists="replace"`), not incrementally updated — simpler to reason about, at the cost of redoing work on every cycle. Fine at this data volume; a real system with millions of rows would need an incremental approach.

---

## Project structure

```
├── .github/workflows/generate_data.yml   # scheduled + manual pipeline trigger
├── config.py                             # env-driven DB configuration
├── database.sql                          # schema: customers, products, orders
├── seed_data.py                          # one-time initial data generation
├── generate_data.py                      # recurring new-order generation
├── data_cleaning.py                      # automated cleaning + quality flags
├── sales_data.py                         # analytics table + KPI calculations
├── zestly_dashboard.py                   # Streamlit dashboard
└── requirements.txt
```
