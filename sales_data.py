import pandas as pd
from sqlalchemy import create_engine
from config import DATABASE_URL


def run():
    engine = create_engine(DATABASE_URL)

    customers = pd.read_sql("SELECT * FROM customers;", engine)
    products = pd.read_sql("SELECT * FROM products;", engine)
    orders = pd.read_sql("SELECT * FROM orders;", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    customers["signup_month"] = pd.to_datetime(customers["signup_month"])
    orders["quantity"] = orders["quantity"].fillna(1)
    orders["discount_pct"] = orders["discount_pct"].fillna(0)

    df = orders.merge(customers, on="customer_id", how="left")
    df = df.merge(products, on="product_id", how="left")

    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["order_date"].dt.day_name()

    df["revenue"] = (df["selling_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)).round(2)
    df["total_cost"] = (df["cost_price"] * df["quantity"]).round(2)
    df["gross_profit"] = (df["revenue"] - df["total_cost"]).round(2)
    df["profit_margin_pct"] = (df["gross_profit"] / df["revenue"] * 100).round(2)

    order_counts = df.groupby("customer_id")["order_id"].transform("nunique")
    df["is_repeat_customer"] = order_counts > 1

    df["customer_tenure_days"] = (df["order_date"] - df["signup_month"]).dt.days
    df["customer_email_domain"] = df["email"].str.split("@").str[1]
    df["stock_quantity_at_order"] = df["stock_quantity"]

    final_columns = [
        "order_id", "customer_id", "customer_name", "city", "signup_month",
        "product_id", "product_name", "category", "order_date", "order_month", "day_of_week",
        "quantity", "selling_price", "cost_price", "discount_pct", "revenue", "total_cost",
        "gross_profit", "profit_margin_pct", "payment_method", "order_status",
        "is_repeat_customer", "customer_tenure_days", "stock_quantity_at_order",
        "order_source", "customer_email_domain", "data_quality_flag",
    ]

    analytics_sales = df[final_columns]
    analytics_sales.to_sql("analytics_sales", engine, if_exists="replace", index=False)

    clean_df = df[df["data_quality_flag"] != "Deduplicated"]
    valid = clean_df[clean_df["order_status"] == "Delivered"]
    cust_unique = df.drop_duplicates("customer_id")

    # 1. Total Revenue
    total_revenue = valid["revenue"].sum()

    # 2. Gross Profit Margin %
    gross_margin_pct = valid["gross_profit"].sum() / total_revenue * 100

    # 3. Month-over-Month Revenue Growth %
    monthly_rev = valid.groupby("order_month")["revenue"].sum().sort_index()
    mom_growth_pct = ((monthly_rev.iloc[-1] - monthly_rev.iloc[-2]) / monthly_rev.iloc[-2] * 100) if len(monthly_rev) >= 2 else 0

    # 4. Average Order Value
    aov = valid["revenue"].mean()

    # 5. Median Order Value
    median_order_value = valid["revenue"].median()

    # 6. Customer Lifetime Value (CLV)
    clv = valid.groupby("customer_id")["revenue"].sum().mean()

    # 7. Repeat Customer Rate %
    total_customers = valid["customer_id"].nunique()
    repeat_customers = valid[valid["is_repeat_customer"]]["customer_id"].nunique()
    repeat_rate_pct = repeat_customers / total_customers * 100

    # 8. New vs. Returning Revenue Split
    new_vs_returning_rev = valid.groupby("is_repeat_customer")["revenue"].sum()

    # 9. New Customer Signups per Month
    signups_per_month = cust_unique.groupby(cust_unique["signup_month"].dt.to_period("M").astype(str)).size()

    # 10. Average Customer Tenure at Purchase
    avg_tenure_days = valid["customer_tenure_days"].mean()

    # 11. Top-Selling Product
    top_product = valid.groupby("product_name")["quantity"].sum().idxmax()

    # 12. Best-Performing Category
    best_category = valid.groupby("category")["revenue"].sum().idxmax()

    # 13. Category Revenue vs. Margin Comparison
    category_rev_vs_margin = valid.groupby("category").agg(revenue=("revenue", "sum"), margin=("profit_margin_pct", "mean"))

    # 14. Inventory Turnover Rate
    turnover = valid.groupby("product_name").agg(sold=("quantity", "sum"), stock=("stock_quantity_at_order", "mean"))
    turnover["turnover_rate"] = turnover["sold"] / turnover["stock"].replace(0, 1)

    # 15. Slow-Moving Products (bottom 20% by units sold)
    slow_threshold = turnover["sold"].quantile(0.2)
    slow_moving_products = turnover[turnover["sold"] <= slow_threshold]

    # 16. Average Items per Order
    avg_items_per_order = valid["quantity"].mean()

    # 17. Order Fulfillment Rate %
    fulfillment_rate_pct = (clean_df["order_status"] == "Delivered").mean() * 100

    # 18. Cancellation Rate %
    cancellation_rate_pct = (clean_df["order_status"] == "Cancelled").mean() * 100

    # 19. Return Rate %
    return_rate_pct = (clean_df["order_status"] == "Returned").mean() * 100

    # 20. Discount Utilization Rate %
    discount_utilization_pct = (valid["discount_pct"] > 0).mean() * 100

    # 21. Average Discount Applied %
    avg_discount_pct = valid.loc[valid["discount_pct"] > 0, "discount_pct"].mean()

    # 22. Revenue by Payment Method
    revenue_by_payment_method = valid.groupby("payment_method")["revenue"].sum()

    # 23. Revenue by Order Source
    revenue_by_order_source = valid.groupby("order_source")["revenue"].sum()

    # 24. Weekday vs. Weekend Revenue Split
    is_weekend = valid["day_of_week"].isin(["Saturday", "Sunday"])
    weekday_vs_weekend_rev = valid.groupby(is_weekend.map({True: "Weekend", False: "Weekday"}))["revenue"].sum()

    # 25. Top Cities by Revenue
    top_cities_by_revenue = valid.groupby("city")["revenue"].sum().sort_values(ascending=False).head(10)

    # 26. Revenue Pareto Ratio (top 20% customers)
    cust_revenue = valid.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
    top20_n = max(1, int(len(cust_revenue) * 0.2))
    revenue_pareto_ratio_pct = cust_revenue.head(top20_n).sum() / cust_revenue.sum() * 100

    # 27. Product Revenue Concentration (top 20% products)
    prod_revenue = valid.groupby("product_name")["revenue"].sum().sort_values(ascending=False)
    top20_n_prod = max(1, int(len(prod_revenue) * 0.2))
    product_revenue_concentration_pct = prod_revenue.head(top20_n_prod).sum() / prod_revenue.sum() * 100

    # 28. AOV: New vs. Repeat Customers
    aov_new_vs_repeat = valid.groupby("is_repeat_customer")["revenue"].mean()

    # 29. Cancellation Rate by Payment Method
    cancellation_rate_by_payment = clean_df.groupby("payment_method")["order_status"].apply(lambda s: (s == "Cancelled").mean() * 100)

    # 30. Days Since Last Order (avg customer recency)
    last_order = valid.groupby("customer_id")["order_date"].max()
    avg_recency_days = (pd.Timestamp.today() - last_order).dt.days.mean()

    print(f"analytics_sales rebuilt: {len(analytics_sales)} rows, {len(final_columns)} columns.")
    print(f"1. Total Revenue: ₹{total_revenue:,.0f}")
    print(f"2. Gross Profit Margin: {gross_margin_pct:.2f}%")
    print(f"3. MoM Revenue Growth: {mom_growth_pct:.2f}%")
    print(f"4. Average Order Value: ₹{aov:,.2f}")
    print(f"5. Median Order Value: ₹{median_order_value:,.2f}")
    print(f"6. Customer Lifetime Value: ₹{clv:,.2f}")
    print(f"7. Repeat Customer Rate: {repeat_rate_pct:.2f}%")
    print(f"8. New vs Returning Revenue:\n{new_vs_returning_rev}")
    print(f"9. New Signups per Month:\n{signups_per_month}")
    print(f"10. Avg Customer Tenure: {avg_tenure_days:.1f} days")
    print(f"11. Top-Selling Product: {top_product}")
    print(f"12. Best-Performing Category: {best_category}")
    print(f"13. Category Revenue vs Margin:\n{category_rev_vs_margin}")
    print(f"14. Inventory Turnover Rate (top 5):\n{turnover.sort_values('turnover_rate', ascending=False).head()}")
    print(f"15. Slow-Moving Products: {len(slow_moving_products)} products")
    print(f"16. Average Items per Order: {avg_items_per_order:.2f}")
    print(f"17. Order Fulfillment Rate: {fulfillment_rate_pct:.2f}%")
    print(f"18. Cancellation Rate: {cancellation_rate_pct:.2f}%")
    print(f"19. Return Rate: {return_rate_pct:.2f}%")
    print(f"20. Discount Utilization Rate: {discount_utilization_pct:.2f}%")
    print(f"21. Average Discount Applied: {avg_discount_pct:.2f}%")
    print(f"22. Revenue by Payment Method:\n{revenue_by_payment_method}")
    print(f"23. Revenue by Order Source:\n{revenue_by_order_source}")
    print(f"24. Weekday vs Weekend Revenue:\n{weekday_vs_weekend_rev}")
    print(f"25. Top Cities by Revenue:\n{top_cities_by_revenue}")
    print(f"26. Revenue Pareto Ratio (top 20% customers): {revenue_pareto_ratio_pct:.2f}%")
    print(f"27. Product Revenue Concentration (top 20% products): {product_revenue_concentration_pct:.2f}%")
    print(f"28. AOV New vs Repeat:\n{aov_new_vs_repeat}")
    print(f"29. Cancellation Rate by Payment Method:\n{cancellation_rate_by_payment}")
    print(f"30. Avg Days Since Last Order: {avg_recency_days:.1f} days")

    return len(analytics_sales)


if __name__ == "__main__":
    run()