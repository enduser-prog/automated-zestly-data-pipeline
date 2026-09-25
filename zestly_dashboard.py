from html import escape
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

from config import DATABASE_URL

st.set_page_config(page_title="Zestly", page_icon="⚡", layout="wide")
engine = create_engine(DATABASE_URL)
LOGO = Path(__file__).parent / "zestly_logo.png"
BG, CARD, BORDER, TEXT, MUTED = "#F3F4F8", "#FFFFFF", "#ECEDF3", "#111827", "#6B7280"
BLUE, GREEN, RED, AMBER = "#2F6BFF", "#22C55E", "#EF4444", "#F59E0B"
OFFWHITE, GREYTXT, GREYLINE = "#F7F7F4", "#6B7280", "#E2E3E8"
DARKGREY, DARKGREY_TXT = "#3F4451", "#E8E9EE"
SEARCH_BG, SEARCH_BORDER, SEARCH_TXT, SEARCH_HINT = "#E5E7EB", "#D1D5DB", "#1F2937", "#6B7280"
NAV_ICON, NAV_ICON_ACTIVE = "#4B5563", "#4C8DFF"
PALETTE = [BLUE, GREEN, AMBER, "#8B5CF6", "#EC4899", "#14B8A6", "#94A3B8"]
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
inr = lambda v: f"₹{v:,.0f}"
z = lambda n, d: n / d if d else 0


def style():
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {BG}; color: {TEXT}; }}
header[data-testid="stHeader"] {{ display: none; }}
.block-container {{ padding: 1rem 1.6rem 2rem; max-width: 1500px; }}
section[data-testid="stSidebar"] {{ background: {CARD}; border-right: 1px solid {BORDER}; width: 250px !important; }}
section[data-testid="stSidebar"] .block-container {{ padding: 1.2rem 1rem; }}
section[data-testid="stSidebar"] [data-testid="stImage"] {{ margin-top: -14px; }}
.brand {{ font-weight: 800; font-size: 1.15rem; display:flex; align-items:center; gap:8px; margin-bottom: 22px; }}
.brand .logo {{ width:26px; height:26px; border-radius:8px; background:{BLUE}; display:inline-block; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{ border-radius:10px; padding:9px 12px; margin-bottom:3px; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p {{ font-size:.84rem; font-weight:500; color:#374151; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] svg {{ color:{NAV_ICON} !important; fill:{NAV_ICON} !important; -webkit-text-fill-color:{NAV_ICON} !important; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{ background:#EAF1FF; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] svg {{ color:{NAV_ICON_ACTIVE} !important; fill:{NAV_ICON_ACTIVE} !important; -webkit-text-fill-color:{NAV_ICON_ACTIVE} !important; }}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] p {{ color:{BLUE}; font-weight:700; }}
section[data-testid="stSidebar"] [data-testid="stTextInputRootElement"],
section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"] {{ background:{SEARCH_BG} !important; background-color:{SEARCH_BG} !important;
    border:1px solid {SEARCH_BORDER} !important; border-radius:12px !important; box-shadow:none !important; color-scheme:light; }}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="base-input"] {{ background:transparent !important; }}
section[data-testid="stSidebar"] [data-testid="stTextInputField"],
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {{ background:transparent !important; background-color:transparent !important; font-size:.84rem;
    color:{SEARCH_TXT} !important; -webkit-text-fill-color:{SEARCH_TXT} !important; caret-color:{SEARCH_TXT}; }}
section[data-testid="stSidebar"] [data-testid="stTextInputField"]::placeholder,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {{ color:{SEARCH_HINT} !important; -webkit-text-fill-color:{SEARCH_HINT} !important; opacity:1 !important; }}
section[data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:focus-within,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{ border-color:{BLUE} !important; }}
.premium {{ margin-top: 40px; background: linear-gradient(160deg,#1E3A8A,#2F6BFF); color:#fff; border-radius:14px; padding:16px; }}
.premium b {{ font-size:.9rem; }} .premium p {{ font-size:.72rem; opacity:.85; margin:6px 0 12px; }}
.premium .btn {{ background:#fff; color:{BLUE}; text-align:center; border-radius:10px; padding:8px; font-weight:700; font-size:.8rem; }}
.pgtitle {{ font-family:'Plus Jakarta Sans','Inter',sans-serif; font-size:2.9rem; font-weight:800; letter-spacing:-.035em; line-height:1.15; display:inline-block; padding-bottom:.08em;
    background:linear-gradient(95deg,{TEXT} 0%,#1E3A8A 60%,{BLUE} 100%); -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color:transparent; color:transparent; }}
.pgbar {{ width:48px; height:5px; border-radius:99px; margin-top:4px; background:linear-gradient(90deg,#FF9A1F,#FF5A1F); }}
div[data-testid="stDateInput"] [data-testid="stDateInputField"],
div[data-testid="stDateInput"] div[data-baseweb="input"] {{ background:{SEARCH_BG} !important; background-color:{SEARCH_BG} !important;
    border:1px solid {SEARCH_BORDER} !important; border-radius:12px !important; box-shadow:none !important; color-scheme:light; }}
div[data-testid="stDateInput"] div[data-baseweb="base-input"] {{ background:transparent !important; }}
div[data-testid="stDateInput"] [data-testid="stDateInputField"] *,
div[data-testid="stDateInput"] input {{ color:{SEARCH_TXT} !important; -webkit-text-fill-color:{SEARCH_TXT} !important; font-weight:600; font-size:.88rem; }}
div[data-testid="stDateInput"] input {{ background:transparent !important; text-align:center; }}
div[data-testid="stDateInput"] svg {{ fill:{SEARCH_TXT} !important; color:{SEARCH_TXT} !important; }}
div[data-testid="stDateInput"] [data-testid="stDateInputField"]:focus-within,
div[data-testid="stDateInput"] div[data-baseweb="input"]:focus-within {{ border-color:{BLUE} !important; }}
div[data-baseweb="popover"] div[data-baseweb="calendar"] {{ background:{CARD} !important; }}
div[data-baseweb="popover"] {{ background:{CARD} !important; border-radius:12px; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background:{CARD}; border:1px solid {BORDER} !important; border-radius:20px;
    box-shadow: 0 6px 20px rgba(17,24,39,.08); padding: 6px 8px; transition: box-shadow .15s ease; }}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{ box-shadow: 0 8px 26px rgba(17,24,39,.11); }}
.ttl {{ font-weight:700; font-size:.92rem; }}
.kl {{ font-family:'Plus Jakarta Sans','Inter',sans-serif; font-size:1.02rem; font-weight:700; letter-spacing:-.01em; color:#1F2937;
    display:flex; justify-content:space-between; align-items:center; }}
.kl span:last-child {{ font-size:1.1rem; }}
.kv {{ font-size:1.7rem; font-weight:800; margin:6px 0 2px; }}
.pill {{ font-size:.72rem; font-weight:700; padding:2px 8px; border-radius:6px; }}
.up {{ background:#DCFCE7; color:{GREEN}; }} .down {{ background:#FEE2E2; color:{RED}; }} .flat {{ background:#F3F4F6; color:{MUTED}; }}
.vs {{ font-size:.72rem; color:{MUTED}; margin-left:6px; }}
.seg {{ border-bottom:3px solid var(--c); padding:6px 4px 8px; }}
.seg .n {{ font-weight:800; font-size:1.05rem; }} .seg .t {{ font-size:.72rem; color:{MUTED}; }}
table.bs {{ width:100%; border-collapse:collapse; font-size:.82rem; }}
table.bs th {{ text-align:left; color:{MUTED}; font-weight:600; font-size:.7rem; letter-spacing:.5px; padding:8px 6px; }}
table.bs td {{ padding:12px 6px; border-top:1px solid {BORDER}; }}
.ico {{ width:30px; height:30px; border-radius:8px; background:#F3F4F6; display:inline-flex; align-items:center; justify-content:center; margin-right:10px; }}
div[data-testid="stDownloadButton"] button {{ background:{BLUE}; color:#fff; border:none; border-radius:10px; font-weight:600; }}
</style>""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load():
    d = pd.read_sql("SELECT * FROM analytics_sales;", engine)
    d["order_date"] = pd.to_datetime(d["order_date"])
    return d


def ctx():
    """Current and previous period frames, driven by the date range in the header."""
    df = load()
    s, e = (pd.to_datetime(x) for x in st.session_state["rng"])
    n = (e - s).days + 1
    ps, pe = s - pd.Timedelta(days=n), s - pd.Timedelta(days=1)
    win = lambda d, a, b: d[(d.order_date >= a) & (d.order_date <= b)]
    base_ = df[df["data_quality_flag"] != "Deduplicated"]
    cur, prv = win(base_, s, e), win(base_, ps, pe)
    return SimpleNamespace(df=df, raw=win(df, s, e), raw_p=win(df, ps, pe), cur=cur, prv=prv,
                           cv=cur[cur.order_status == "Delivered"], pv=prv[prv.order_status == "Delivered"],
                           s=s, e=e, ps=ps, pe=pe, n=n)


def mt(v):
    """Every headline metric for one (delivered) frame, so current and previous use the same maths."""
    o, r, g, u, cu = v.order_id.nunique(), v.revenue.sum(), v.gross_profit.sum(), v.quantity.sum(), v.customer_id.nunique()
    rp = v[v.is_repeat_customer].customer_id.nunique()
    per_order = v.groupby("order_id").gross_profit.sum()
    return dict(rev=r, ord=o, gp=g, units=u, cust=cu, rep=rp, new=cu - rp, aov=v.revenue.mean() if len(v) else 0,
                mar=z(g, r) * 100, ppo=z(g, o), ppu=z(g, u), ipo=z(u, o), asp=z(r, u), rpc=z(r, cu), opc=z(o, cu),
                rate=z(rp, cu) * 100, lossr=(per_order < 0).mean() * 100 if o else 0,
                lossv=-v.gross_profit.clip(upper=0).sum())


def daily(v, col, s, e, fn="sum"):
    return getattr(v.groupby(v.order_date.dt.normalize())[col], fn)().reindex(pd.date_range(s, e), fill_value=0)


def margin_daily(v, s, e):
    return (daily(v, "gross_profit", s, e) / daily(v, "revenue", s, e).replace(0, float("nan")) * 100).fillna(0)


def prod(v):
    return v.groupby("product_name").agg(sold=("quantity", "sum"), rev=("revenue", "sum"), gp=("gross_profit", "sum"))


# ---------- UI pieces ----------
def html(markup):
    st.markdown(" ".join(l.strip() for l in markup.strip().splitlines() if l.strip()), unsafe_allow_html=True)


def pill(cur, prev, inv=False, pp=False):
    up = None
    if not prev:
        t = "—"
    else:
        ch = cur - prev if pp else (cur - prev) / prev * 100
        up = ch >= 0
        t = f"{'▲' if up else '▼'} {abs(ch):.1f}{'pp' if pp else '%'}"
    cls = "flat" if up is None else ("up" if up != inv else "down")
    return f'<span class="pill {cls}">{t}</span><span class="vs">vs. last period</span>'


def kpi(col, label, value, cur, prev, icon="◉", inv=False, pp=False):
    with col, st.container(border=True):
        html(f'<div class="kl"><span>{label}</span><span style="color:{BLUE}">{icon}</span></div>'
             f'<div class="kv">{value}</div>{pill(cur, prev, inv, pp)}')


def row(specs):
    for col, s in zip(st.columns(len(specs)), specs):
        kpi(col, *s)


def card(title):
    c = st.container(border=True)
    with c:
        html(f'<div class="ttl" style="margin:6px 0">{title}</div>')
    return c


CHARTTXT = "#4B5563"


def base(fig, h):
    fig.update_layout(height=h, margin=dict(t=5, l=5, r=5, b=5), paper_bgcolor=CARD, plot_bgcolor=CARD,
                      font=dict(family="Inter", color=CHARTTXT, size=11), showlegend=False)
    return fig


def show(fig):
    # theme=None stops Streamlit's chart theme from overriding our axis/label colours
    st.plotly_chart(fig, use_container_width=True, theme=None)


def axis_style(f, xt=None, yt=None, xgrid=False, ygrid=True):
    """Make both axes visible: dark tick labels, a light axis line, optional axis titles."""
    def kw(title, grid):
        d = dict(tickfont=dict(size=11, color=CHARTTXT), automargin=True, showline=True, linecolor="#D1D5DB",
                 zeroline=False, showgrid=grid, gridcolor=BORDER, showticklabels=True, ticks="outside", tickcolor="#D1D5DB")
        if title:
            d["title"] = dict(text=title, font=dict(size=11, color=CHARTTXT), standoff=8)
        return d
    f.update_xaxes(**kw(xt, xgrid))
    f.update_yaxes(**kw(yt, ygrid))
    return f


def trend(cs, ps, h=220, pre="₹", suf="", yt=None):
    f = go.Figure()
    f.add_scatter(x=cs.index, y=cs.values, name="This period", mode="lines",
                  line=dict(color=BLUE, width=2.5, shape="spline"), fill="tozeroy", fillcolor="rgba(47,107,255,.08)")
    f.add_scatter(x=cs.index, y=ps.values[:len(cs)], name="Last period", mode="lines",
                  line=dict(color="#B8BCCB", width=1.5, dash="dot", shape="spline"))
    f.update_layout(hovermode="x unified", showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=11, color=CHARTTXT)))
    f.update_xaxes(tickformat="%d %b")
    f.update_yaxes(tickprefix=pre, ticksuffix=suf)
    base(f, h)
    axis_style(f, xt="Date", yt=yt)
    show(f)


def bars(x, y, h=230, peak=False, horiz=False, pre="", suf="", cat=None, val=None):
    x, y = list(x), list(y)
    top = y.index(max(y)) if y else -1
    on = lambda i: not peak or i == top
    f = go.Figure(go.Bar(x=y if horiz else x, y=x if horiz else y, orientation="h" if horiz else "v",
                         marker_color=[BLUE if on(i) else "#C7D3F5" for i in range(len(y))],
                         text=[f"{pre}{v:,.0f}{suf}" for v in y],
                         textfont=dict(color=CHARTTXT, size=11),
                         textposition="outside", cliponaxis=False))
    try:
        f.update_layout(barcornerradius=8)
    except Exception:
        pass
    base(f, h)
    if horiz:
        f.update_yaxes(autorange="reversed")
        f.update_xaxes(tickprefix=pre, ticksuffix=suf)
        axis_style(f, xt=val, yt=cat, xgrid=True, ygrid=False)
        f.update_layout(margin=dict(t=5, l=5, r=55, b=5))
    else:
        f.update_yaxes(tickprefix=pre, ticksuffix=suf)
        axis_style(f, xt=cat, yt=val, xgrid=False, ygrid=True)
        f.update_layout(margin=dict(t=22, l=5, r=5, b=5))
    show(f)


def donut(labels, values, h=230):
    f = go.Figure(go.Pie(labels=list(labels), values=list(values), hole=.7, sort=False,
                         textinfo="percent", textposition="inside",
                         insidetextfont=dict(color="#FFFFFF", size=11, family="Inter"),
                         texttemplate="%{percent:.1%}",
                         marker=dict(colors=PALETTE, line=dict(color=CARD, width=2))))
    show(base(f, h).update_layout(showlegend=True, legend=dict(font=dict(size=11, color=CHARTTXT))))


def hist(values, h=230):
    f = go.Figure(go.Histogram(x=list(values), nbinsx=20, marker_color=BLUE))
    f.update_xaxes(tickprefix="₹")
    base(f, h)
    axis_style(f, xt="Order value (₹)", yt="Orders")
    show(f)


def gauge(rate, h=190):
    g = go.Figure(go.Indicator(mode="gauge+number", value=rate, number=dict(suffix="%", font=dict(size=34, color=TEXT)),
                               gauge=dict(axis=dict(range=[0, 100], visible=False), bar=dict(color=GREEN, thickness=0.28),
                                          bgcolor="#EEF0F6", borderwidth=0)))
    show(base(g, h))


def tbl(head, rows, left=1):
    al = lambda i: "" if i < left else ' style="text-align:right"'
    th = "".join(f"<th{al(i)}>{h}</th>" for i, h in enumerate(head))
    tr = "".join("<tr>" + "".join(f"<td{al(i)}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    html(f'<table class="bs"><tr>{th}</tr>{tr}</table>' if rows else f'<div class="vs">No data in this period</div>')


def nm(name):
    return f'<span class="ico">📦</span>{escape(str(name))[:32]}'


def sgn(v):
    return f'<span style="color:{GREEN if v >= 0 else RED};font-weight:600">{inr(v)}</span>'


PROD_HEAD = ["NAME", "SOLD", "REVENUE", "PROFIT", "MARGIN"]


def prow(name, r):
    return [nm(name), f"{int(r.sold):,} sold", inr(r.rev), sgn(r.gp), f"{z(r.gp, r.rev) * 100:.1f}%" if r.rev else "—"]


# ------------------------------------------------------------------ Overview
def overview():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    row([("Revenue", inr(a["rev"]), a["rev"], b["rev"], "◉"),
         ("Orders", f"{a['ord']:,}", a["ord"], b["ord"], "▤"),
         ("Avg Order Value", inr(a["aov"]), a["aov"], b["aov"], "◎"),
         ("Customers", f"{a['cust']:,}", a["cust"], b["cust"], "☺")])
    st.write("")
    left, right = st.columns([2.1, 1])
    with left:
        with st.container(border=True):
            x, y = st.columns([1, 2.2])
            with x:
                html(f'<div class="ttl">Total Profit</div><div style="height:38px"></div>'
                     f'<div class="kv" style="font-size:2rem">{inr(a["gp"])}</div>{pill(a["gp"], b["gp"])}')
            with y:
                trend(daily(c.cv, "gross_profit", c.s, c.e), daily(c.pv, "gross_profit", c.ps, c.pe), 200, yt="Profit (₹)")
            segs = c.cv.groupby("category").customer_id.nunique().sort_values(ascending=False).head(3)
            for col, (n, v), clr in zip(st.columns(3), segs.items(), [BLUE, GREEN, AMBER]):
                col.markdown(f'<div class="seg" style="--c:{clr}"><div class="n">{v:,}</div><div class="t">{escape(str(n))}</div></div>',
                             unsafe_allow_html=True)
        st.write("")
        with card("Best Selling Products"):
            bs = prod(c.cv).sort_values("sold", ascending=False).head(5)
            tbl(["ID", "NAME", "SOLD", "REVENUE", "PROFIT"],
                [[f'<span style="color:{MUTED}">#{83000 + i}</span>', nm(n), f"{int(r.sold):,} sold",
                  sgn(r.rev) if r.gp >= 0 else f'<span style="color:{RED};font-weight:600">{inr(r.rev)}</span>', inr(r.gp)]
                 for i, (n, r) in enumerate(bs.iterrows(), 1)], left=2)
    with right:
        with card("Most Day Active"):
            dw = c.cv.groupby("day_of_week").order_id.nunique().reindex(DAYS, fill_value=0)
            bars([d[:3] for d in DAYS], dw.values, 220, peak=True, cat="Weekday", val="Orders")
        st.write("")
        with card("Repeat Customer Rate"):
            gauge(a["rate"])


# --------------------------------------------------------------------- Sales
def sales():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    bk, pbk = c.cur.revenue.sum(), c.prv.revenue.sum()
    row([("Booked Revenue (all statuses)", inr(bk), bk, pbk, "◉"),
         ("Units Sold", f"{a['units']:,.0f}", a["units"], b["units"], "▣"),
         ("Items per Order", f"{a['ipo']:.2f}", a["ipo"], b["ipo"], "▤"),
         ("Avg Daily Revenue", inr(a["rev"] / c.n), a["rev"] / c.n, b["rev"] / c.n, "◎")])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Daily Revenue"):
        trend(daily(c.cv, "revenue", c.s, c.e), daily(c.pv, "revenue", c.ps, c.pe), yt="Revenue (₹)")
    with r, card("Revenue by Category"):
        rc = c.cv.groupby("category").revenue.sum().sort_values(ascending=False).head(6)
        bars(rc.index, rc.values, 220, horiz=True, pre="₹", cat="Category", val="Revenue (₹)")
    st.write("")
    l, r = st.columns(2)
    with l, card("Revenue by Weekday"):
        rw = c.cv.groupby("day_of_week").revenue.sum().reindex(DAYS, fill_value=0)
        bars([d[:3] for d in DAYS], rw.values, 230, peak=True, pre="₹", cat="Weekday", val="Revenue (₹)")
    with r, card("Best Trading Days"):
        dr, do = daily(c.cv, "revenue", c.s, c.e), daily(c.cv, "order_id", c.s, c.e, "nunique")
        top = dr.nlargest(5)
        tbl(["DAY", "ORDERS", "REVENUE"], [[f"{d:%a, %d %b %Y}", f"{int(do[d]):,}", inr(v)] for d, v in top[top > 0].items()])


# ------------------------------------------------------------- Profitability
def profitability():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    row([("Gross Margin", f"{a['mar']:.1f}%", a["mar"], b["mar"], "◉", False, True),
         ("Profit per Order", inr(a["ppo"]), a["ppo"], b["ppo"], "▤"),
         ("Profit per Unit", inr(a["ppu"]), a["ppu"], b["ppu"], "▣"),
         ("Loss-making Orders", f"{a['lossr']:.1f}%", a["lossr"], b["lossr"], "▼", True, True),
         ("Value Lost to Negative Margin", inr(a["lossv"]), a["lossv"], b["lossv"], "◎", True)])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Gross Margin Trend"):
        trend(margin_daily(c.cv, c.s, c.e), margin_daily(c.pv, c.ps, c.pe), 220, pre="", suf="%", yt="Gross margin (%)")
    with r, card("Profit by Category"):
        pc = c.cv.groupby("category").gross_profit.sum().sort_values(ascending=False).head(6)
        bars(pc.index, pc.values, 220, horiz=True, pre="₹", cat="Category", val="Profit (₹)")
    st.write("")
    l, r = st.columns(2)
    with l, card("Margin by Category"):
        g = c.cv.groupby("category")[["gross_profit", "revenue"]].sum()
        mc = (g.gross_profit / g.revenue.replace(0, float("nan")) * 100).dropna().sort_values(ascending=False).head(6)
        bars(mc.index, mc.values, 230, horiz=True, suf="%", cat="Category", val="Margin (%)")
    with r, card("Lowest Margin Products"):
        p = prod(c.cv)
        p = p[p.rev > 0].assign(m=lambda d: d.gp / d.rev * 100).sort_values("m").head(5)
        tbl(PROD_HEAD, [prow(n, x) for n, x in p.iterrows()])


# ------------------------------------------------------------------ Products
def products():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    pa, pb = prod(c.cv), prod(c.pv)
    share = lambda p: z(p.rev.nlargest(5).sum(), p.rev.sum()) * 100
    la, lb = int((pa.gp < 0).sum()), int((pb.gp < 0).sum())
    row([("Active Products", f"{len(pa):,}", len(pa), len(pb), "▣"),
         ("Avg Selling Price", inr(a["asp"]), a["asp"], b["asp"], "◎"),
         ("Top-5 Revenue Share", f"{share(pa):.1f}%", share(pa), share(pb), "◉", True, True),
         ("Loss-making Products", f"{la:,}", la, lb, "▼", True)])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Top Products by Revenue"):
        t = pa.rev.sort_values(ascending=False).head(8)
        bars([str(n)[:28] for n in t.index], t.values, 300, horiz=True, pre="₹", cat="Product", val="Revenue (₹)")
    with r, card("Units Sold by Category"):
        u = c.cv.groupby("category").quantity.sum().sort_values(ascending=False).head(6)
        donut(u.index, u.values, 300)
    st.write("")
    l, r = st.columns(2)
    with l, card("Top Products by Profit"):
        tbl(PROD_HEAD, [prow(n, x) for n, x in pa.nlargest(5, "gp").iterrows()])
    with r, card("Slow Movers"):
        tbl(PROD_HEAD, [prow(n, x) for n, x in pa[pa.sold > 0].nsmallest(5, "sold").iterrows()])


# ----------------------------------------------------------------- Customers
def customers():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    row([("New Customers", f"{a['new']:,}", a["new"], b["new"], "☺"),
         ("Repeat Customers", f"{a['rep']:,}", a["rep"], b["rep"], "◉"),
         ("Orders per Customer", f"{a['opc']:.2f}", a["opc"], b["opc"], "▤"),
         ("Revenue per Customer", inr(a["rpc"]), a["rpc"], b["rpc"], "◎")])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Active Customers per Day"):
        trend(daily(c.cv, "customer_id", c.s, c.e, "nunique"), daily(c.pv, "customer_id", c.ps, c.pe, "nunique"), 220, pre="", yt="Customers")
    with r, card("New vs Repeat Revenue"):
        sp = c.cv.groupby("is_repeat_customer").revenue.sum().reindex([False, True], fill_value=0)
        donut(["New", "Repeat"], sp.values)
    st.write("")
    l, r = st.columns(2)
    with l, card("Customers by Category"):
        cc = c.cv.groupby("category").customer_id.nunique().sort_values(ascending=False).head(6)
        bars(cc.index, cc.values, 240, horiz=True, cat="Category", val="Customers")
    with r, card("Top Customers"):
        t = c.cv.groupby("customer_id").agg(o=("order_id", "nunique"), rev=("revenue", "sum"), gp=("gross_profit", "sum")).nlargest(5, "rev")
        tbl(["CUSTOMER", "ORDERS", "REVENUE", "PROFIT"],
            [[f"Customer {escape(str(i))}", f"{int(x.o):,} orders", inr(x.rev), sgn(x.gp)] for i, x in t.iterrows()])


# -------------------------------------------------------------------- Orders
def orders():
    c = ctx()
    a, b = mt(c.cv), mt(c.pv)
    pl, ppl = c.cur.order_id.nunique(), c.prv.order_id.nunique()
    dr, pdr = z(a["ord"], pl) * 100, z(b["ord"], ppl) * 100
    row([("Orders Placed", f"{pl:,}", pl, ppl, "▤"),
         ("Delivered Orders", f"{a['ord']:,}", a["ord"], b["ord"], "◉"),
         ("Delivery Rate", f"{dr:.1f}%", dr, pdr, "◎", False, True),
         ("Undelivered Rate", f"{100 - dr:.1f}%" if pl else "—", 100 - dr, 100 - pdr, "▼", True, True)])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Orders per Day"):
        trend(daily(c.cur, "order_id", c.s, c.e, "nunique"), daily(c.prv, "order_id", c.ps, c.pe, "nunique"), 220, pre="", yt="Orders")
    with r, card("Order Status"):
        s = c.cur.groupby("order_status").order_id.nunique().sort_values(ascending=False)
        donut(s.index, s.values)
    st.write("")
    l, r = st.columns(2)
    with l, card("Order Value Distribution"):
        hist(c.cv.groupby("order_id").revenue.sum().values)
    with r, card("Orders by Category"):
        oc = c.cur.groupby("category").order_id.nunique().sort_values(ascending=False).head(6)
        bars(oc.index, oc.values, 230, horiz=True, cat="Category", val="Orders")


# -------------------------------------------------------------- Data quality
def quality():
    c = ctx()
    key = ["order_id", "order_date", "customer_id", "product_name", "category", "quantity", "revenue", "gross_profit"]
    dup = lambda d: int((d.data_quality_flag == "Deduplicated").sum())
    miss = lambda d: int(d[key].isna().any(axis=1).sum())
    tot, ptot, da, db = len(c.raw), len(c.raw_p), dup(c.raw), dup(c.raw_p)
    ra, rb = z(da, tot) * 100, z(db, ptot) * 100
    row([("Total Records", f"{tot:,}", tot, ptot, "▤"),
         ("Duplicates Removed", f"{da:,}", da, db, "▼", True),
         ("Duplicate Rate", f"{ra:.1f}%", ra, rb, "◎", True, True),
         ("Rows with Missing Values", f"{miss(c.raw):,}", miss(c.raw), miss(c.raw_p), "◉", True)])
    st.write("")
    l, r = st.columns([2.1, 1])
    with l, card("Duplicates per Day"):
        d, p = c.raw[c.raw.data_quality_flag == "Deduplicated"], c.raw_p[c.raw_p.data_quality_flag == "Deduplicated"]
        trend(daily(d, "order_id", c.s, c.e, "count"), daily(p, "order_id", c.ps, c.pe, "count"), 220, pre="", yt="Duplicates")
    with r, card("Records by Quality Flag"):
        fl = c.raw.data_quality_flag.fillna("Unflagged").value_counts()
        donut(fl.index, fl.values)
    st.write("")
    with card("Missing Values by Field"):
        ms = c.raw[key].isna().sum()
        tbl(["FIELD", "MISSING", "SHARE"], [[k, f"{int(v):,}", f"{z(v, tot) * 100:.1f}%"] for k, v in ms.items()])


# -------------------------------------------------------------------- Search
def search_results(q, c):
    """Sidebar search: matches pages, products, categories, orders and customers (all dates, duplicates excluded)."""
    d = c.df[c.df["data_quality_flag"] != "Deduplicated"]
    ql = q.lower()
    has = lambda col: d[col].astype(str).str.lower().str.contains(ql, regex=False, na=False)
    delivered = lambda f: f[f.order_status == "Delivered"]

    page_hits = [p for p in pages if ql in p.title.lower()]

    pm = d[has("product_name")]
    pr = prod(delivered(pm)).reindex(pm.product_name.unique(), fill_value=0).sort_values("rev", ascending=False)

    cm = delivered(d[has("category")])
    cg = cm.groupby("category").agg(o=("order_id", "nunique"), rev=("revenue", "sum"), gp=("gross_profit", "sum")).sort_values("rev", ascending=False)

    om = d[has("order_id") | has("customer_id")].sort_values("order_date", ascending=False)

    html(f'<div class="vs" style="margin:0 0 12px">Matches for <b>“{escape(q)}”</b> across all dates. Clear the search box to go back.</div>')

    if not (page_hits or len(pr) or len(cg) or len(om)):
        with card("No matches"):
            html(f'<div class="vs">Nothing found for “{escape(q)}”. Try a product name, category, order ID or customer ID.</div>')
        return

    if page_hits:
        with card("Pages"):
            for p in page_hits:
                st.page_link(p)
    if len(pr) or len(cg):
        l, r = st.columns([2.1, 1])
        if len(pr):
            with l, card(f"Products ({len(pr):,} found)"):
                tbl(PROD_HEAD, [prow(n, x) for n, x in pr.head(10).iterrows()])
        if len(cg):
            with r, card(f"Categories ({len(cg):,} found)"):
                tbl(["CATEGORY", "ORDERS", "REVENUE", "PROFIT"],
                    [[escape(str(n)), f"{int(x.o):,}", inr(x.rev), sgn(x.gp)] for n, x in cg.head(6).iterrows()])
    if len(om):
        st.write("")
        with card(f"Orders & Customers ({len(om):,} rows{', showing latest 10' if len(om) > 10 else ''})"):
            tbl(["ORDER", "DATE", "CUSTOMER", "PRODUCT", "STATUS", "REVENUE"],
                [[escape(str(x.order_id)), f"{x.order_date:%d %b %Y}", f"Customer {escape(str(x.customer_id))}",
                  escape(str(x.product_name))[:28], escape(str(x.order_status)), inr(x.revenue)]
                 for x in om.head(10).itertuples()], left=5)


# ------------------------------------------------------------------ App shell
style()

pages = [
    st.Page(overview, title="Overview", icon=":material/dashboard:", url_path="overview", default=True),
    st.Page(sales, title="Sales", icon=":material/payments:", url_path="sales"),
    st.Page(profitability, title="Profitability", icon=":material/trending_up:", url_path="profitability"),
    st.Page(products, title="Products", icon=":material/inventory_2:", url_path="products"),
    st.Page(customers, title="Customers", icon=":material/group:", url_path="customers"),
    st.Page(orders, title="Orders", icon=":material/receipt_long:", url_path="orders"),
    st.Page(quality, title="Data Quality", icon=":material/verified:", url_path="data-quality"),
]
pg = st.navigation(pages, position="hidden")

# Moving to another page clears the search so that page shows normally (must run before the search widget is created).
if st.session_state.get("_page") != pg.title:
    st.session_state["_page"] = pg.title
    st.session_state["q"] = ""

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=185)
    else:
        html('<div class="brand"><span class="logo"></span>Zestly</div>')
    st.text_input("search", placeholder="🔍  Search products, orders...", label_visibility="collapsed", key="q")
    st.write("")
    for p in pages:
        st.page_link(p)
    html("""<div class="premium"><b>Upgrade to Premium!</b><p>Upgrade your account and unlock all of the benefits.</p>
        <div class="btn">Upgrade premium</div></div>""")

q = st.session_state.get("q", "").strip()

h1, h2, h3 = st.columns([3, 2.2, 1], vertical_alignment="center")
h1.markdown(f'<div class="pgtitle">{"Search results" if q else escape(pg.title)}</div><div class="pgbar"></div>', unsafe_allow_html=True)
df = load()
mn, mx = df["order_date"].min(), df["order_date"].max()
with h2:
    rng = st.date_input("range", (max(mn, mx - pd.Timedelta(days=29)), mx), key="rng", label_visibility="collapsed")
if len(rng) != 2:
    st.stop()

c = ctx()
h3.download_button("⬇ Export", c.raw.to_csv(index=False).encode(), f"zestly_{c.s:%Y%m%d}_{c.e:%Y%m%d}.csv",
                   "text/csv", use_container_width=True)
st.write("")
if q:
    search_results(q, c)
else:
    pg.run()
