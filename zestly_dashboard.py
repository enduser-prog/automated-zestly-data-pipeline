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
# "Selected dates" / View dropdown: same family as the search bar, just a shade darker
SELECT_BG, SELECT_BG_HOVER, SELECT_BORDER, SELECT_TXT = "#D3D7DF", "#CBD0D9", "#BCC2CC", "#1F2937"
NAV_ICON, NAV_ICON_ACTIVE = "#4B5563", "#4C8DFF"
PALETTE = [BLUE, GREEN, AMBER, "#8B5CF6", "#EC4899", "#14B8A6", "#94A3B8"]
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
inr = lambda v: f"₹{v:,.0f}"
z = lambda n, d: n / d if d else 0

# Simple line-style magnifier (stroke only, no fill, no colour) used inside the search box
SEARCH_ICON = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' "
               "fill='none' stroke='%236B7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
               "<circle cx='11' cy='11' r='7'/><line x1='21' y1='21' x2='16.65' y2='16.65'/></svg>")


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
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {{ background-color:transparent !important; font-size:.84rem;
    color:{SEARCH_TXT} !important; -webkit-text-fill-color:{SEARCH_TXT} !important; caret-color:{SEARCH_TXT};
    background-image:url("{SEARCH_ICON}") !important; background-repeat:no-repeat !important; background-position:10px center !important;
    background-size:16px 16px !important; padding-left:34px !important; }}
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
details.inf {{ display:inline-block; position:relative; vertical-align:middle; margin-left:8px; }}
details.inf > summary {{ list-style:none; cursor:pointer; width:18px; height:18px; border-radius:50%; border:1.5px solid #9CA3AF; color:{MUTED};
    font:italic 700 .68rem Georgia,serif; display:inline-flex; align-items:center; justify-content:center; user-select:none; }}
details.inf > summary::-webkit-details-marker {{ display:none; }}
details.inf > summary:hover, details.inf[open] > summary {{ border-color:{BLUE}; color:{BLUE}; }}
details.inf > .tip {{ position:absolute; z-index:999; top:26px; left:-8px; width:250px; background:#fff; border:1px solid {BORDER}; border-radius:10px;
    box-shadow:0 8px 24px rgba(17,24,39,.14); padding:9px 11px; font-size:.76rem; font-weight:400; line-height:1.4; color:#374151; }}

/* ---- "Selected dates" / View dropdown: search-bar grey, one shade darker, on every page ---- */
div[data-testid="stSelectbox"], .stSelectbox {{ color-scheme:light; }}
/* the visible box */
div[data-testid="stSelectbox"] div[data-baseweb="select"],
.stSelectbox div[data-baseweb="select"],
div[data-baseweb="select"] {{ background:{SELECT_BG} !important; background-color:{SELECT_BG} !important;
    border:1px solid {SELECT_BORDER} !important; border-radius:12px !important; min-height:34px;
    box-shadow:none !important; overflow:hidden; color-scheme:light; }}
div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
div[data-baseweb="select"]:hover {{ background:{SELECT_BG_HOVER} !important; background-color:{SELECT_BG_HOVER} !important; }}
div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within,
div[data-baseweb="select"]:focus-within {{ border-color:{BLUE} !important; }}
/* everything inside the box stays see-through so Streamlit's dark theme cannot repaint it */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] div,
div[data-baseweb="select"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] div[data-baseweb="select"] input {{ background:transparent !important; background-color:transparent !important;
    border:none !important; box-shadow:none !important; }}
/* text + arrow */
div[data-baseweb="select"] *,
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{ color:{SELECT_TXT} !important; -webkit-text-fill-color:{SELECT_TXT} !important;
    font-size:.8rem; font-weight:600; }}
div[data-baseweb="select"] svg,
div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{ fill:{SELECT_TXT} !important; color:{SELECT_TXT} !important; }}
/* the list that opens under it */
div[data-baseweb="popover"] div[data-baseweb="menu"],
div[data-baseweb="popover"] ul,
div[data-testid="stSelectboxVirtualDropdown"],
ul[role="listbox"] {{ background:{CARD} !important; background-color:{CARD} !important; color-scheme:light; }}
ul[role="listbox"] li, ul[role="listbox"] li * {{ background-color:transparent !important; color:{TEXT} !important; -webkit-text-fill-color:{TEXT} !important; font-size:.82rem; }}
ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] {{ background-color:#EAF1FF !important; }}
table.bs.good th {{ color:#15803D; border-bottom:2px solid {GREEN}; }}
table.bs.slow th {{ color:#B45309; border-bottom:2px solid {AMBER}; }}
.rk {{ display:inline-flex; width:24px; height:24px; border-radius:50%; background:#DCFCE7; color:#15803D; font-weight:800; font-size:.72rem;
    align-items:center; justify-content:center; margin-right:10px; }}
.slw {{ background:#FEF3C7; color:#B45309; font-weight:700; font-size:.76rem; padding:2px 8px; border-radius:6px; white-space:nowrap; }}
.chips {{ display:flex; gap:10px; flex-wrap:wrap; margin:2px 0 6px; }}
.chip {{ background:#F3F4F6; border-radius:10px; padding:6px 12px; }}
.chip .cl {{ font-size:.68rem; color:{MUTED}; font-weight:600; letter-spacing:.3px; }}
.chip .cv {{ font-size:.98rem; font-weight:800; color:{TEXT}; }}
</style>""", unsafe_allow_html=True)


@st.cache_data(ttl=10)
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
                           all_base=base_, all_cv=base_[base_.order_status == "Delivered"], all_raw=df,
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


VIEWS = ["Selected dates", "Monthly", "Quarterly", "Yearly"]
PERIOD = {"D": "D", "W": "W-SUN", "M": "M"}


def view_picker(key):
    st.selectbox("View", VIEWS, key=f"tv_{key}", label_visibility="collapsed")


def span(c, key):
    """Window + bucket size for a time chart, from its View dropdown (windows end on the header's end date).
    Selected dates = the header range, bucketed automatically; Monthly = last 30 days by day;
    Quarterly = last ~4 months by week; Yearly = last 12 months by month."""
    mode, e = st.session_state.get(f"tv_{key}", VIEWS[0]), c.e
    if mode == "Monthly":
        s, freq = e - pd.Timedelta(days=29), "D"
    elif mode == "Quarterly":
        s = e - pd.Timedelta(days=111)
        s, freq = s - pd.Timedelta(days=s.weekday()), "W"
    elif mode == "Yearly":
        s, freq = (e.to_period("M") - 11).start_time, "M"
    else:
        s, freq = c.s, ("D" if c.n <= 62 else "W" if c.n <= 240 else "M")
    n = (e - s).days + 1
    ps, pe = (c.ps, c.pe) if mode == VIEWS[0] else (s - pd.Timedelta(days=n), s - pd.Timedelta(days=1))
    return SimpleNamespace(s=s, e=e, ps=ps, pe=pe, freq=freq)


def tseries(v, col, sp, fn="sum", prev=False):
    """One value per day / week / month between the window's dates (empty buckets = 0)."""
    s, e = (sp.ps, sp.pe) if prev else (sp.s, sp.e)
    day = v.order_date.dt.normalize()
    d = v[(day >= s) & (day <= e)]
    pf = PERIOD[sp.freq]
    out = getattr(d.groupby(d.order_date.dt.to_period(pf))[col], fn)().reindex(pd.period_range(s, e, freq=pf), fill_value=0)
    out.index = out.index.to_timestamp()
    return out


def tl(v, col, sp, fn="sum"):
    return tseries(v, col, sp, fn), tseries(v, col, sp, fn, prev=True)


def margin_tl(v, sp):
    m = lambda prev: (tseries(v, "gross_profit", sp, prev=prev) / tseries(v, "revenue", sp, prev=prev).replace(0, float("nan")) * 100).fillna(0)
    return m(False), m(True)


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


def ttl(title, info=None, style="margin:6px 0"):
    i = f'<details class="inf"><summary>i</summary><div class="tip">{escape(info)}</div></details>' if info else ""
    return f'<div class="ttl" style="{style}">{title}{i}</div>'


def card(title, info=None, tv=None):
    c = st.container(border=True)
    with c:
        if tv:
            a, b = st.columns([3, 1.1], vertical_alignment="center")
            with a:
                html(ttl(title, info))
            with b:
                view_picker(tv)
        else:
            html(ttl(title, info))
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


def trend(cs, ps, h=220, pre="₹", suf="", yt=None, freq="D"):
    f = go.Figure()
    f.add_scatter(x=cs.index, y=cs.values, name="This period", mode="lines",
                  line=dict(color=BLUE, width=2.5, shape="spline"), fill="tozeroy", fillcolor="rgba(47,107,255,.08)")
    f.add_scatter(x=cs.index, y=ps.values[:len(cs)], name="Last period", mode="lines",
                  line=dict(color="#B8BCCB", width=1.5, dash="dot", shape="spline"))
    f.update_layout(hovermode="x unified", showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=11, color=CHARTTXT)))
    f.update_xaxes(tickformat="%b %Y" if freq == "M" else "%d %b",
                   hoverformat={"D": "%d %b %Y", "W": "Week of %d %b %Y", "M": "%B %Y"}[freq])
    if freq == "M" and len(cs) <= 13:
        f.update_xaxes(dtick="M1")
    f.update_yaxes(tickprefix=pre, ticksuffix=suf)
    base(f, h)
    axis_style(f, xt={"D": "Date", "W": "Week starting", "M": "Month"}[freq], yt=yt)
    show(f)


def shade(v, lo, hi):
    """Pale blue (lowest) -> full blue (highest)."""
    t = (v - lo) / (hi - lo) if hi > lo else 1
    a, b = (0xC7, 0xD3, 0xF5), (0x2F, 0x6B, 0xFF)
    return "#" + "".join(f"{round(p + (q - p) * t):02X}" for p, q in zip(a, b))


def bars(x, y, h=230, gradient=False, horiz=False, pre="", suf="", cat=None, val=None):
    x, y = list(x), list(y)
    colors = [shade(v, min(y), max(y)) for v in y] if gradient else [BLUE] * len(y)
    f = go.Figure(go.Bar(x=y if horiz else x, y=x if horiz else y, orientation="h" if horiz else "v",
                         marker_color=colors,
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


NICE_STEPS = [500, 1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000]


def hist(values, h=250):
    """Order value distribution: orders grouped into clear price ranges, with median / average / largest shown as chips.
    The range is cut at the 95th percentile and everything above goes into one last '₹X+' bar,
    so a few huge orders can't squash the rest of the chart."""
    v = pd.Series(list(values), dtype="float").dropna()
    if v.empty:
        html('<div class="vs">No data in this period</div>')
        return

    tot, med, avg, big = len(v), v.median(), v.mean(), v.max()
    fmt = lambda x: f"₹{x / 1000:g}k" if abs(x) >= 1000 else f"₹{x:g}"

    cap = v.quantile(0.95)
    step = next((s for s in NICE_STEPS if cap / s <= 8), NICE_STEPS[-1])
    top = max(step, int(-(-cap // step)) * step)
    edges = list(range(0, int(top) + 1, int(step)))

    bins = [float("-inf")] + edges[1:] + [float("inf")]
    labels = [f"Under {fmt(edges[1])}"] + [f"{fmt(edges[i])}–{fmt(edges[i + 1])}" for i in range(1, len(edges) - 1)] + [f"{fmt(edges[-1])}+"]
    counts = pd.cut(v, bins=bins, right=False).value_counts(sort=False).values

    med_bin = int(pd.cut(pd.Series([med]), bins=bins, right=False).cat.codes.iloc[0])
    colors = [BLUE if i == med_bin else "#A9C1FF" for i in range(len(labels))]

    chip = lambda l, val: f'<div class="chip"><div class="cl">{l}</div><div class="cv">{val}</div></div>'
    html(f'<div class="chips">{chip("MEDIAN ORDER", inr(med))}{chip("AVERAGE ORDER", inr(avg))}{chip("LARGEST ORDER", inr(big))}</div>')

    f = go.Figure(go.Bar(x=labels, y=counts, marker_color=colors,
                         text=[f"{n:,}<br>{n / tot * 100:.0f}%" for n in counts],
                         textposition="outside", textfont=dict(color=CHARTTXT, size=11), cliponaxis=False,
                         hovertemplate="%{x}<br>%{y:,} orders<extra></extra>"))
    try:
        f.update_layout(barcornerradius=6)
    except Exception:
        pass
    base(f, h)
    axis_style(f, xt="Order value", yt="Number of orders", xgrid=False, ygrid=True)
    f.update_layout(margin=dict(t=36, l=5, r=5, b=5), bargap=0.15)
    f.update_yaxes(range=[0, max(counts) * 1.25])
    show(f)


def gauge(rate, h=190):
    g = go.Figure(go.Indicator(mode="gauge+number", value=rate, number=dict(suffix="%", font=dict(size=34, color=TEXT)),
                               gauge=dict(axis=dict(range=[0, 100], visible=False), bar=dict(color=GREEN, thickness=0.28),
                                          bgcolor="#EEF0F6", borderwidth=0)))
    show(base(g, h))


def tbl(head, rows, left=1, cls=""):
    al = lambda i: "" if i < left else ' style="text-align:right"'
    th = "".join(f"<th{al(i)}>{h}</th>" for i, h in enumerate(head))
    tr = "".join("<tr>" + "".join(f"<td{al(i)}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    html(f'<table class="bs {cls}"><tr>{th}</tr>{tr}</table>' if rows else f'<div class="vs">No data in this period</div>')


def nm(name, badge='<span class="ico">📦</span>'):
    return f'{badge}{escape(str(name))[:32]}'


def sgn(v):
    return f'<span style="color:{GREEN if v >= 0 else RED};font-weight:600">{inr(v)}</span>'


PROD_HEAD = ["NAME", "SOLD", "REVENUE", "PROFIT", "MARGIN"]


def prow(name, r, badge='<span class="ico">📦</span>', slow=False):
    sold = f"{int(r.sold):,} sold"
    return [nm(name, badge), f'<span class="slw">{sold}</span>' if slow else sold, inr(r.rev), sgn(r.gp),
            f"{z(r.gp, r.rev) * 100:.1f}%" if r.rev else "—"]


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
                html(ttl("Total Profit", "Profit made from delivered orders in the selected period. The dotted line on the chart is the previous period.", style="")
                     + f'<div style="height:38px"></div>'
                     f'<div class="kv" style="font-size:2rem">{inr(a["gp"])}</div>{pill(a["gp"], b["gp"])}')
            with y:
                _, pk = st.columns([2.4, 1])
                with pk:
                    view_picker("ovw")
                sp = span(c, "ovw")
                trend(*tl(c.all_cv, "gross_profit", sp), 200, yt="Profit (₹)", freq=sp.freq)
            segs = c.cv.groupby("category").customer_id.nunique().sort_values(ascending=False).head(3)
            for col, (n, v), clr in zip(st.columns(3), segs.items(), [BLUE, GREEN, AMBER]):
                col.markdown(f'<div class="seg" style="--c:{clr}"><div class="n">{v:,}</div><div class="t">{escape(str(n))}</div></div>',
                             unsafe_allow_html=True)
        st.write("")
        with card("Best Selling Products", "The five products that sold the most units in this period."):
            bs = prod(c.cv).sort_values("sold", ascending=False).head(5)
            # Revenue is plain; Profit is green (or red if it ever were a loss)
            tbl(["ID", "NAME", "SOLD", "REVENUE", "PROFIT"],
                [[f'<span style="color:{MUTED}">#{83000 + i}</span>', nm(n), f"{int(r.sold):,} sold",
                  inr(r.rev), sgn(r.gp)]
                 for i, (n, r) in enumerate(bs.iterrows(), 1)], left=2)
    with right:
        with card("Orders by Weekday", "How many orders came in on each day of the week. Darker bars are busier days."):
            dw = c.cv.groupby("day_of_week").order_id.nunique().reindex(DAYS, fill_value=0)
            bars([d[:3] for d in DAYS], dw.values, 220, gradient=True, cat="Weekday", val="Orders")
        st.write("")
        with card("Repeat Customer Rate", "The share of customers in this period who have bought from you before."):
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
    with l, card("Revenue Over Time", "Money earned from delivered orders over time. The dotted line is the previous period.", tv="sales"):
        sp = span(c, "sales")
        trend(*tl(c.all_cv, "revenue", sp), yt="Revenue (₹)", freq=sp.freq)
    with r, card("Revenue by Category", "Which product categories bring in the most money."):
        rc = c.cv.groupby("category").revenue.sum().sort_values(ascending=False).head(6)
        bars(rc.index, rc.values, 220, horiz=True, pre="₹", cat="Category", val="Revenue (₹)")
    st.write("")
    l, r = st.columns(2)
    with l, card("Revenue by Weekday", "Total revenue earned on each day of the week. Darker bars mean more revenue."):
        rw = c.cv.groupby("day_of_week").revenue.sum().reindex(DAYS, fill_value=0)
        bars([d[:3] for d in DAYS], rw.values, 230, gradient=True, pre="₹", cat="Weekday", val="Revenue (₹)")
    with r, card("Best Trading Days", "The five individual days with the highest revenue."):
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
    with l, card("Profit Margin Over Time", "How much of every ₹100 of sales is kept as profit. Higher is better.", tv="margin"):
        sp = span(c, "margin")
        trend(*margin_tl(c.all_cv, sp), 220, pre="", suf="%", yt="Gross margin (%)", freq=sp.freq)
    with r, card("Profit by Category", "Total profit made by each product category."):
        pc = c.cv.groupby("category").gross_profit.sum().sort_values(ascending=False).head(6)
        bars(pc.index, pc.values, 220, horiz=True, pre="₹", cat="Category", val="Profit (₹)")
    st.write("")
    l, r = st.columns(2)
    with l, card("Margin by Category", "The share of sales kept as profit in each category."):
        g = c.cv.groupby("category")[["gross_profit", "revenue"]].sum()
        mc = (g.gross_profit / g.revenue.replace(0, float("nan")) * 100).dropna().sort_values(ascending=False).head(6)
        bars(mc.index, mc.values, 230, horiz=True, suf="%", cat="Category", val="Margin (%)")
    with r, card("Lowest Margin Products", "Products that keep the smallest share of their sales as profit. Worth a price or cost check."):
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
    with l, card("Top Products by Revenue", "The products that brought in the most money."):
        t = pa.rev.sort_values(ascending=False).head(8)
        bars([str(n)[:28] for n in t.index], t.values, 300, horiz=True, pre="₹", cat="Product", val="Revenue (₹)")
    with r, card("Units Sold by Category", "How the total number of items sold is split across categories."):
        u = c.cv.groupby("category").quantity.sum().sort_values(ascending=False).head(6)
        donut(u.index, u.values, 300)
    st.write("")
    l, r = st.columns(2)
    with l, card("Top Products by Profit", "Your five biggest earners: the products that made the most profit."):
        tbl(PROD_HEAD, [prow(n, x, f'<span class="rk">{i}</span>') for i, (n, x) in enumerate(pa.nlargest(5, "gp").iterrows(), 1)], cls="good")
    with r, card("Slow Movers", "Products that sold the fewest units in this period. They may need a promotion or a review."):
        tbl(PROD_HEAD, [prow(n, x, '<span class="ico">🐢</span>', slow=True) for n, x in pa[pa.sold > 0].nsmallest(5, "sold").iterrows()], cls="slow")


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
    with l, card("Buying Customers Over Time", "How many different customers placed an order in each day, week or month. Each customer is counted once per period.", tv="cust"):
        sp = span(c, "cust")
        trend(*tl(c.all_cv, "customer_id", sp, "nunique"), 220, pre="", yt="Customers", freq=sp.freq)
    with r, card("New vs Repeat Revenue", "Revenue from first-time customers compared with customers who have bought before."):
        sp = c.cv.groupby("is_repeat_customer").revenue.sum().reindex([False, True], fill_value=0)
        donut(["New", "Repeat"], sp.values)
    st.write("")
    l, r = st.columns(2)
    with l, card("Customers by Category", "How many different customers bought from each category."):
        cc = c.cv.groupby("category").customer_id.nunique().sort_values(ascending=False).head(6)
        bars(cc.index, cc.values, 240, horiz=True, cat="Category", val="Customers")
    with r, card("Top Customers", "The five customers who spent the most in this period."):
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
    with l, card("Orders Over Time", "How many orders were placed over time, including ones not yet delivered. The dotted line is the previous period.", tv="orders"):
        sp = span(c, "orders")
        trend(*tl(c.all_base, "order_id", sp, "nunique"), 220, pre="", yt="Orders", freq=sp.freq)
    with r, card("Order Status", "The share of orders in each status, such as delivered or not delivered."):
        s = c.cur.groupby("order_status").order_id.nunique().sort_values(ascending=False)
        donut(s.index, s.values)
    st.write("")
    l, r = st.columns(2)
    with l, card("Order Value Distribution",
                 "How big your delivered orders are. Each bar counts the orders in a price range, with the number and share of orders on top. "
                 "The darker bar is where the median (typical) order falls. If the average is well above the median, "
                 "a few very large orders are pulling it up. The last bar groups all the biggest orders together."):
        hist(c.cv.groupby("order_id").revenue.sum().values)
    with r, card("Orders by Category", "How many orders include products from each category."):
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
    with l, card("Duplicates Over Time", "How many repeated (duplicate) records were found and removed over time. Fewer is better.", tv="dups"):
        sp = span(c, "dups")
        trend(*tl(c.all_raw[c.all_raw.data_quality_flag == "Deduplicated"], "order_id", sp, "count"), 220, pre="", yt="Duplicates", freq=sp.freq)
    with r, card("Records by Quality Flag", "How many records are clean and how many were flagged, for example as duplicates."):
        fl = c.raw.data_quality_flag.fillna("Unflagged").value_counts()
        donut(fl.index, fl.values)
    st.write("")
    with card("Missing Values by Field", "For each data field, how many records have nothing filled in."):
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
    st.text_input("search", placeholder="Search products, orders...", label_visibility="collapsed", key="q")
    st.write("")
    for p in pages:
        st.page_link(p)

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
