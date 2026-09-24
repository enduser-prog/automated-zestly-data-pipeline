import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
from config import DATABASE_URL

st.set_page_config(page_title="Zestly Analytics", page_icon="⚡", layout="wide")
engine = create_engine(DATABASE_URL)

# ---- DESIGN TOKENS ----
BG = "#F5F6FA"
CARD = "#FFFFFF"
BORDER = "#ECEDF3"
TEXT = "#171923"
MUTED = "#8B8FA3"

BLUE = "#4F46E5"
BLUE_SOFT = "rgba(79,70,229,0.10)"
GREEN = "#16A34A"
GREEN_SOFT = "rgba(22,163,74,0.12)"
AMBER = "#F59E0B"
AMBER_SOFT = "rgba(245,158,11,0.13)"
RED = "#DC2626"
RED_SOFT = "rgba(220,38,38,0.12)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
.stApp {{ background: {BG}; color: {TEXT}; }}
.block-container {{ padding-top: 1.4rem; max-width: 1440px; }}
h1,h2,h3 {{ font-weight: 800 !important; color: {TEXT} !important; }}
hr {{ border-color: {BORDER} !important; }}

div[role="radiogroup"] {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 999px;
    padding: 6px; gap: 4px; display: inline-flex; box-shadow: 0 2px 10px rgba(23,25,35,0.05);
}}
div[role="radiogroup"] label {{ border-radius: 999px !important; padding: 8px 18px !important; margin: 0 !important; }}
div[role="radiogroup"] label:has(input:checked) {{ background: {BLUE}; }}
div[role="radiogroup"] label:has(input:checked) p {{ color: #FFFFFF !important; font-weight: 700 !important; }}
div[role="radiogroup"] label p {{ font-size: 0.86rem; font-weight: 600; color: {MUTED}; margin: 0; }}

.zst-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 20px;
    padding: 20px 22px; margin-bottom: 8px; box-shadow: 0 4px 14px rgba(23,25,35,0.06);
}}
.zst-card .top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
.zst-card .icon {{
    width: 36px; height: 36px; border-radius: 11px; background: var(--soft, {BLUE_SOFT});
    color: var(--accent, {BLUE}); display: flex; align-items: center; justify-content: center; font-size: 1.05rem;
}}
.zst-card .label {{ font-size: 0.76rem; color: {MUTED}; font-weight: 600; margin-bottom: 6px; letter-spacing: 0.2px; }}
.zst-card .value {{ font-size: 1.55rem; font-weight: 800; color: {TEXT}; margin-bottom: 4px; }}
.zst-card .delta {{ font-size: 0.76rem; font-weight: 700; padding: 2px 9px; border-radius: 999px; }}
.zst-card .delta.up {{ background: {GREEN_SOFT}; color: {GREEN}; }}
.zst-card .delta.down {{ background: {RED_SOFT}; color: {RED}; }}
.zst-card .delta.flat {{ background: rgba(139,143,163,0.14); color: {MUTED}; }}
.zst-card .vs {{ font-size: 0.72rem; color: {MUTED}; margin-left: 4px; }}

.zst-panel {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 20px; padding: 22px;
    box-shadow: 0 4px 14px rgba(23,25,35,0.06); margin-bottom: 14px;
}}
.zst-panel .ptitle {{ font-size: 0.95rem; font-weight: 700; color: {TEXT}; margin-bottom: 3px; }}
.zst-panel .psub {{ font-size: 0.76rem; color: {MUTED}; margin-bottom: 14px; }}

.zst-stat-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid {BORDER}; }}
.zst-stat-row:last-child {{ border-bottom: none; }}
.zst-stat-row .l {{ font-size: 0.84rem; color: {MUTED}; }}
.zst-stat-row .v {{ font-weight: 800; font-size: 0.95rem; padding: 3px 10px; border-radius: 8px; }}

.zst-feed-item {{ display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid {BORDER}; }}
.zst-feed-item:last-child {{ border-bottom: none; }}
.zst-feed-icon {{ width: 30px; height: 30px; border-radius: 9px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:0.9rem; }}
.zst-feed-text {{ font-size: 0.83rem; color: {TEXT}; line-height: 1.4; }}

div[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 14px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)


def render_html(markup):
    st.markdown(" ".join(l.strip() for l in markup.strip().splitlines() if l.strip()), unsafe_allow_html=True)


def kpi_card(col, icon, label, value, accent=BLUE, soft=BLUE_SOFT, delta=None, direction="flat"):
    delta_html = f'<span class="delta {direction}">{delta}</span><span class="vs">vs prior period</span>' if delta else ""
    with col:
        render_html(f"""<div class="zst-card" style="--accent:{accent};">
            <div class="top"><div class="icon" style="--soft:{soft};">{icon}</div></div>
            <div class="label">{label}</div><div class="value">{value}</div>{delta_html}</div>""")


def stat_row(label, value, color=TEXT, soft="transparent"):
    render_html(f"""<div class="zst-stat-row"><span class="l">{label}</span>
        <span class="v" style="color:{color};background:{soft};">{value}</span></div>""")


def panel_start(title, subtitle=""):
    sub = f'<div class="psub">{subtitle}</div>' if subtitle else ""
    render_html(f'<div class="zst-panel"><div class="ptitle">{title}</div>{sub}')


def panel_end():
    render_html("</div>")


def delta_from(current, previous):
    if previous is None or previous == 0:
        return None, "flat"
    pct = (current - previous) / previous * 100
    if pct > 0.05:
        return f"↑ {pct:.1f}%", "up"
    if pct < -0.05:
        return f"↓ {abs(pct):.1f}%", "down"
    return "flat", "flat"


def semantic(value, good, bad, higher_is_better=True):
    if higher_is_better:
        if value >= good: return GREEN, GREEN_SOFT
        if value >= bad: return AMBER, AMBER_SOFT
        return RED, RED_SOFT
    if value <= good: return GREEN, GREEN_SOFT
    if value <= bad: return AMBER, AMBER_SOFT
    return RED, RED_SOFT


def style_fig(fig, height=300):
    fig.update_layout(
        template="plotly_white", paper_bgcolor=CARD, plot_bgcolor=CARD, height=height,
        font=dict(family="Plus Jakarta Sans, sans-serif", color=MUTED, size=12),
        margin=dict(t=10, l=10, r=10, b=10), showlegend=False,
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    return fig


@st.cache_data(ttl=300)
def load_data():
    d = pd.read_sql("SELECT * FROM analytics_sales;", engine)
    d["order_date"] = pd.to_datetime(d["order_date"])
    return d


@st.cache_data(ttl=300)
def load_products():
    return pd.read_sql("SELECT * FROM products;", engine)


df = load_data()
products = load_products()

# ---- TOP BAR ----
top1, top2 = st.columns([3, 1])
with top1:
    st.markdown(f"<div style='font-size:1.5rem;font-weight:800;'>⚡ Zestly Analytics</div>", unsafe_allow_html=True)
with top2:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export CSV", csv, "zestly_sales.csv", "text/csv", use_container_width=True)

nav1, nav2, nav3 = st.columns([2.2, 1, 1])
with nav1:
    page = st.radio("Navigate", ["Overview", "Sales & Revenue", "Customers", "Products & Fulfillment"], label_visibility="collapsed")
with nav2:
    categories = sorted(df["category"].dropna().unique())
    selected_categories = st.multiselect("Category", categories, default=categories, label_visibility="collapsed")
with nav3:
    min_date, max_date = df["order_date"].min(), df["order_date"].max()
    date_range = st.date_input("Date range", (min_date, max_date), label_visibility="collapsed")

st.write("")

filtered = df[df["category"].isin(selected_categories)]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["order_date"] >= start) & (filtered["order_date"] <= end)]

clean_df = filtered[filtered["data_quality_flag"] != "Deduplicated"]
valid = clean_df[clean_df["order_status"] == "Delivered"]

prev_valid = pd.DataFrame(columns=valid.columns)
if len(date_range) == 2:
    window = end - start
    p_start, p_end = start - window - pd.Timedelta(days=1), start - pd.Timedelta(days=1)
    prev_clean = df[(df["category"].isin(selected_categories)) & (df["order_date"] >= p_start) & (df["order_date"] <= p_end) & (df["data_quality_flag"] != "Deduplicated")]
    prev_valid = prev_clean[prev_clean["order_status"] == "Delivered"]


# ==================== PAGE 1: OVERVIEW ====================
if page == "Overview":
    total_revenue = valid["revenue"].sum()
    total_orders = valid["order_id"].nunique()
    aov = valid["revenue"].mean() if len(valid) else 0
    gross_margin_pct = (valid["gross_profit"].sum() / total_revenue * 100) if total_revenue else 0

    monthly_rev = valid.groupby("order_month")["revenue"].sum().sort_index()
    mom_growth = ((monthly_rev.iloc[-1] - monthly_rev.iloc[-2]) / monthly_rev.iloc[-2] * 100) if len(monthly_rev) >= 2 else 0

    prev_revenue = prev_valid["revenue"].sum() if len(prev_valid) else None
    prev_orders = prev_valid["order_id"].nunique() if len(prev_valid) else None
    prev_aov = prev_valid["revenue"].mean() if len(prev_valid) else None
    prev_margin = (prev_valid["gross_profit"].sum() / prev_revenue * 100) if prev_revenue else None

    r1 = st.columns(5)
    d, dr = delta_from(total_revenue, prev_revenue)
    kpi_card(r1[0], "₹", "Total Revenue", f"₹{total_revenue:,.0f}", BLUE, BLUE_SOFT, d, dr)
    d, dr = delta_from(total_orders, prev_orders)
    kpi_card(r1[1], "🛒", "Total Orders", f"{total_orders:,}", BLUE, BLUE_SOFT, d, dr)
    d, dr = delta_from(aov, prev_aov)
    kpi_card(r1[2], "📦", "Avg Order Value", f"₹{aov:,.0f}", BLUE, BLUE_SOFT, d, dr)
    d, dr = delta_from(gross_margin_pct, prev_margin)
    kpi_card(r1[3], "📊", "Gross Profit Margin", f"{gross_margin_pct:.1f}%", GREEN, GREEN_SOFT, d, dr)
    kpi_card(r1[4], "📈", "MoM Revenue Growth", f"{mom_growth:.1f}%", GREEN if mom_growth >= 0 else RED, GREEN_SOFT if mom_growth >= 0 else RED_SOFT)

    st.write("")
    c1, c2, c3 = st.columns([2, 1, 1.1])

    with c1:
        panel_start("Revenue Trend", "Monthly revenue, delivered orders only")
        monthly_df = monthly_rev.reset_index()
        fig = go.Figure(go.Scatter(x=monthly_df["order_month"], y=monthly_df["revenue"], mode="lines+markers",
                                    line=dict(color=BLUE, width=3), fill="tozeroy", fillcolor="rgba(79,70,229,0.08)",
                                    marker=dict(size=6, color=BLUE)))
        st.plotly_chart(style_fig(fig, 260), use_container_width=True)
        panel_end()

    with c2:
        panel_start("Orders by Status", "Delivered / cancelled / returned")
        sc = valid["order_status"].value_counts() if False else clean_df["order_status"].value_counts().reset_index()
        sc.columns = ["status", "count"]
        fig2 = px.pie(sc, names="status", values="count", hole=0.68, color="status",
                      color_discrete_map={"Delivered": GREEN, "Cancelled": RED, "Returned": AMBER})
        fig2.update_traces(marker=dict(line=dict(color=CARD, width=3)))
        st.plotly_chart(style_fig(fig2, 220), use_container_width=True)
        panel_end()

    with c3:
        panel_start("Fulfillment Health", "Order outcome rates")
        fulfillment_pct = (clean_df["order_status"] == "Delivered").mean() * 100 if len(clean_df) else 0
        cancel_pct = (clean_df["order_status"] == "Cancelled").mean() * 100 if len(clean_df) else 0
        return_pct = (clean_df["order_status"] == "Returned").mean() * 100 if len(clean_df) else 0
        c, s = semantic(fulfillment_pct, 90, 75, True)
        stat_row("Fulfillment Rate", f"{fulfillment_pct:.1f}%", c, s)
        c, s = semantic(cancel_pct, 5, 10, False)
        stat_row("Cancellation Rate", f"{cancel_pct:.1f}%", c, s)
        c, s = semantic(return_pct, 5, 10, False)
        stat_row("Return Rate", f"{return_pct:.1f}%", c, s)
        panel_end()

    st.write("")
    panel_start("Key Insights")
    top_product = valid.groupby("product_name")["quantity"].sum().idxmax() if not valid.empty else "N/A"
    best_category = valid.groupby("category")["revenue"].sum().idxmax() if not valid.empty else "N/A"
    total_customers = valid["customer_id"].nunique()
    repeat_customers = valid[valid["is_repeat_customer"]]["customer_id"].nunique()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers else 0
    insights = [
        ("💰", BLUE_SOFT, BLUE, f"<b>{best_category}</b> is the top-performing category by revenue."),
        ("🏆", GREEN_SOFT, GREEN, f"<b>{top_product}</b> is the best-selling product by units."),
        ("🔁", GREEN_SOFT, GREEN, f"Repeat customer rate stands at <b>{repeat_rate:.1f}%</b>."),
    ]
    feed = "".join(f'<div class="zst-feed-item"><div class="zst-feed-icon" style="background:{soft};">{icon}</div><div class="zst-feed-text">{text}</div></div>' for icon, soft, color, text in insights)
    render_html(feed)
    panel_end()


# ==================== PAGE 2: SALES & REVENUE ====================
elif page == "Sales & Revenue":
    median_ov = valid["revenue"].median() if len(valid) else 0
    discount_util_pct = (valid["discount_pct"] > 0).mean() * 100 if len(valid) else 0
    avg_discount_pct = valid.loc[valid["discount_pct"] > 0, "discount_pct"].mean() if (valid["discount_pct"] > 0).any() else 0
    cust_rev = valid.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
    pareto_pct = (cust_rev.head(max(1, int(len(cust_rev) * 0.2))).sum() / cust_rev.sum() * 100) if len(cust_rev) else 0

    r1 = st.columns(4)
    kpi_card(r1[0], "📦", "Median Order Value", f"₹{median_ov:,.0f}")
    kpi_card(r1[1], "🏷", "Discount Utilization", f"{discount_util_pct:.1f}%")
    kpi_card(r1[2], "💸", "Avg Discount Applied", f"{avg_discount_pct:.1f}%")
    kpi_card(r1[3], "🎯", "Top 20% Customers = Revenue", f"{pareto_pct:.1f}%", AMBER, AMBER_SOFT)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        panel_start("Revenue by Payment Method")
        rpm = valid.groupby("payment_method")["revenue"].sum().sort_values(ascending=False).reset_index()
        st.plotly_chart(style_fig(px.bar(rpm, x="payment_method", y="revenue", color_discrete_sequence=[BLUE])), use_container_width=True)
        panel_end()
    with c2:
        panel_start("Revenue by Order Source")
        rso = valid.groupby("order_source")["revenue"].sum().sort_values(ascending=False).reset_index()
        st.plotly_chart(style_fig(px.bar(rso, x="order_source", y="revenue", color_discrete_sequence=[BLUE])), use_container_width=True)
        panel_end()

    c3, c4 = st.columns(2)
    with c3:
        panel_start("Weekday vs. Weekend Revenue")
        is_wknd = valid["day_of_week"].isin(["Saturday", "Sunday"]).map({True: "Weekend", False: "Weekday"})
        wk = valid.groupby(is_wknd)["revenue"].sum().reset_index()
        wk.columns = ["period", "revenue"]
        st.plotly_chart(style_fig(px.bar(wk, x="period", y="revenue", color_discrete_sequence=[BLUE])), use_container_width=True)
        panel_end()
    with c4:
        panel_start("Top Cities by Revenue")
        tc = valid.groupby("city")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(tc, x="revenue", y="city", orientation="h", color_discrete_sequence=[BLUE])
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_fig(fig), use_container_width=True)
        panel_end()

    panel_start("Category: Revenue vs. Profit Margin")
    cat = valid.groupby("category").agg(revenue=("revenue", "sum"), margin=("profit_margin_pct", "mean")).reset_index()
    c5, c6 = st.columns(2)
    c5.plotly_chart(style_fig(px.bar(cat, x="category", y="revenue", color_discrete_sequence=[BLUE])), use_container_width=True)
    c6.plotly_chart(style_fig(px.bar(cat, x="category", y="margin", color_discrete_sequence=[GREEN])), use_container_width=True)
    panel_end()


# ==================== PAGE 3: CUSTOMERS ====================
elif page == "Customers":
    clv = valid.groupby("customer_id")["revenue"].sum().mean() if not valid.empty else 0
    total_customers = valid["customer_id"].nunique()
    repeat_customers = valid[valid["is_repeat_customer"]]["customer_id"].nunique()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers else 0
    avg_tenure = valid["customer_tenure_days"].mean() if len(valid) else 0
    last_order = valid.groupby("customer_id")["order_date"].max()
    avg_recency = (pd.Timestamp.today() - last_order).dt.days.mean() if len(last_order) else 0

    r1 = st.columns(5)
    kpi_card(r1[0], "💎", "Customer Lifetime Value", f"₹{clv:,.0f}")
    kpi_card(r1[1], "🔁", "Repeat Customer Rate", f"{repeat_rate:.1f}%", GREEN, GREEN_SOFT)
    kpi_card(r1[2], "👥", "Active Customers", f"{total_customers:,}")
    kpi_card(r1[3], "🗓", "Avg Customer Tenure", f"{avg_tenure:.0f} days")
    c, s = semantic(avg_recency, 20, 45, higher_is_better=False)
    kpi_card(r1[4], "⏱", "Avg Days Since Last Order", f"{avg_recency:.0f} days", c, s)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        panel_start("New vs. Returning Customer Revenue")
        nvr = valid.groupby("is_repeat_customer")["revenue"].sum().reset_index()
        nvr["segment"] = nvr["is_repeat_customer"].map({True: "Returning", False: "New"})
        fig = px.bar(nvr, x="segment", y="revenue", color="segment", color_discrete_map={"New": BLUE, "Returning": GREEN})
        st.plotly_chart(style_fig(fig), use_container_width=True)
        panel_end()
    with c2:
        panel_start("Avg Order Value: New vs. Returning")
        aovnr = valid.groupby("is_repeat_customer")["revenue"].mean().reset_index()
        aovnr["segment"] = aovnr["is_repeat_customer"].map({True: "Returning", False: "New"})
        fig2 = px.bar(aovnr, x="segment", y="revenue", color="segment", color_discrete_map={"New": BLUE, "Returning": GREEN})
        st.plotly_chart(style_fig(fig2), use_container_width=True)
        panel_end()

    panel_start("New Customer Signups per Month")
    cust_unique = filtered.drop_duplicates("customer_id")
    signups = cust_unique.groupby(cust_unique["signup_month"].astype(str).str[:7]).size().reset_index()
    signups.columns = ["month", "new_customers"]
    signups = signups.sort_values("month")
    st.plotly_chart(style_fig(px.bar(signups, x="month", y="new_customers", color_discrete_sequence=[BLUE])), use_container_width=True)
    panel_end()

    panel_start("Customer Lifetime Value Distribution")
    clv_df = valid.groupby("customer_id")["revenue"].sum().reset_index()
    st.plotly_chart(style_fig(px.histogram(clv_df, x="revenue", nbins=30, color_discrete_sequence=[BLUE])), use_container_width=True)
    panel_end()


# ==================== PAGE 4: PRODUCTS & FULFILLMENT ====================
elif page == "Products & Fulfillment":
    top_product = valid.groupby("product_name")["quantity"].sum().idxmax() if not valid.empty else "N/A"
    best_category = valid.groupby("category")["revenue"].sum().idxmax() if not valid.empty else "N/A"
    avg_items = valid["quantity"].mean() if len(valid) else 0
    low_stock = products[products["stock_quantity"] <= products["reorder_level"]]
    out_of_stock = products[products["stock_quantity"] == 0]

    r1 = st.columns(5)
    kpi_card(r1[0], "🏆", "Top-Selling Product", top_product[:18])
    kpi_card(r1[1], "⭐", "Best Category", best_category)
    kpi_card(r1[2], "📦", "Avg Items per Order", f"{avg_items:.2f}")
    c, s = semantic(len(low_stock), 0, max(3, len(products) * 0.2), higher_is_better=False)
    kpi_card(r1[3], "⚠", "Low Stock Products", len(low_stock), c, s)
    c, s = semantic(len(out_of_stock), 0, 3, higher_is_better=False)
    kpi_card(r1[4], "✕", "Out of Stock Products", len(out_of_stock), c, s)

    st.write("")
    fulfillment_pct = (clean_df["order_status"] == "Delivered").mean() * 100 if len(clean_df) else 0
    cancel_pct = (clean_df["order_status"] == "Cancelled").mean() * 100 if len(clean_df) else 0
    return_pct = (clean_df["order_status"] == "Returned").mean() * 100 if len(clean_df) else 0
    r2 = st.columns(3)
    c, s = semantic(fulfillment_pct, 90, 75, True)
    kpi_card(r2[0], "✅", "Order Fulfillment Rate", f"{fulfillment_pct:.1f}%", c, s)
    c, s = semantic(cancel_pct, 5, 10, False)
    kpi_card(r2[1], "🚫", "Cancellation Rate", f"{cancel_pct:.1f}%", c, s)
    c, s = semantic(return_pct, 5, 10, False)
    kpi_card(r2[2], "↩", "Return Rate", f"{return_pct:.1f}%", c, s)

    st.write("")
    panel_start("Cancellation Rate by Payment Method")
    cbp = clean_df.groupby("payment_method")["order_status"].apply(lambda s: (s == "Cancelled").mean() * 100).reset_index()
    cbp.columns = ["payment_method", "cancellation_rate"]
    fig = px.bar(cbp, x="payment_method", y="cancellation_rate", color_discrete_sequence=[RED])
    st.plotly_chart(style_fig(fig), use_container_width=True)
    panel_end()

    c1, c2 = st.columns(2)
    with c1:
        panel_start("Inventory Turnover Rate", "Top 10 by turnover")
        turnover = valid.groupby("product_name").agg(sold=("quantity", "sum"), stock=("stock_quantity_at_order", "mean")).reset_index()
        turnover["turnover_rate"] = (turnover["sold"] / turnover["stock"].replace(0, 1)).round(2)
        st.dataframe(turnover.sort_values("turnover_rate", ascending=False).head(10), use_container_width=True, hide_index=True)
        panel_end()
    with c2:
        panel_start("Slow-Moving Products", "Bottom 20% by units sold")
        threshold = turnover["sold"].quantile(0.2)
        st.dataframe(turnover[turnover["sold"] <= threshold], use_container_width=True, hide_index=True)
        panel_end()