import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import json
import re

st.set_page_config(
    page_title="FL Wingmen Dashboard",
    page_icon="\U0001F357",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #FAFBFC; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    .dash-header {
        background: linear-gradient(135deg, #1A3C34 0%, #2D6A4F 100%);
        padding: 1.2rem 1.8rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .dash-header h1 { color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0; }
    .dash-header p { color: #B7E4C7; font-size: 0.82rem; margin: 0.2rem 0 0 0; }

    .kpi-box {
        background: #FFFFFF;
        border: 1px solid #E8ECF0;
        border-radius: 10px;
        padding: 1rem 0.8rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-label {
        color: #6B7280;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-value {
        color: #1F2937;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .kpi-value.green { color: #059669; }
    .kpi-value.orange { color: #D97706; }
    .kpi-value.red { color: #DC2626; }

    .section-title {
        color: #1F2937;
        font-size: 1rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #2D6A4F;
        display: inline-block;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8ECF0;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label { color: #6B7280 !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.5px; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #1F2937 !important; font-size: 1.4rem !important; font-weight: 700 !important; }

    .stTabs [data-baseweb="tab-list"] { display: none; }

    section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E8ECF0; width: 220px !important; min-width: 220px !important; }
    section[data-testid="stSidebar"] > div { width: 220px !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] .stMarkdown h1 { color: #1A3C34; font-size: 1rem; font-weight: 700; }
    section[data-testid="stSidebar"] label { color: #374151 !important; font-size: 0.8rem !important; }
    section[data-testid="stSidebar"] .stMarkdown p { color: #6B7280; font-size: 0.8rem; }
    section[data-testid="stSidebar"] .stMarkdown hr { border-color: #E8ECF0; }
    section[data-testid="stSidebar"] .stSelectbox > div > div { font-size: 0.82rem; }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { border: 2px solid #1A3C34 !important; border-radius: 8px !important; }

    .stDataFrame { border-radius: 8px; overflow: hidden; }
    .stDataFrame [data-testid="stDataFrameResizable"] { background: #FFFFFF; border: 1px solid #E8ECF0; border-radius: 8px; }
    .stDataFrame th { background: #F0FDF4 !important; color: #1F2937 !important; font-size: 0.78rem !important; font-weight: 600 !important; border-bottom: 2px solid #2D6A4F !important; }
    .stDataFrame td { color: #374151 !important; font-size: 0.78rem !important; background: #FFFFFF !important; }
    .stDataFrame tr:hover td { background: #F9FAFB !important; }
    [data-testid="glideDataEditor"] { border: 1px solid #E8ECF0 !important; border-radius: 8px !important; }
    [data-testid="glideDataEditor"] th, [data-testid="glideDataEditor"] .header-cell { background: #F0FDF4 !important; color: #1F2937 !important; }
    [data-testid="stDataFrame"] > div { background: #FFFFFF; border-radius: 8px; }

    div[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid #E8ECF0; border-radius: 8px; }
    div[data-testid="stExpander"] summary span { color: #374151 !important; }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div { gap: 0.15rem; }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background: transparent;
        color: #374151 !important;
        padding: 0.45rem 0.7rem;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
        color: #374151 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background: #F0FDF4;
        color: #2D6A4F !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
        color: #2D6A4F !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background: #2D6A4F;
        color: #FFFFFF !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span p { margin: 0; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path(__file__).parent / "data"
CONFIG_PATH = Path(__file__).parent / "config.json"

DISTRICTS = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        DISTRICTS = config.get("stores", {})

STORE_TO_DISTRICT = {}
for district, stores in DISTRICTS.items():
    for store in stores:
        store_num = store.split(" - ")[0].strip().lstrip("0")
        STORE_TO_DISTRICT[store_num] = district

GREEN = "#059669"
GOLD = "#D97706"
TEAL = "#0D9488"
ORANGE = "#D97706"
RED = "#DC2626"
DARK = "#64748B"
CHART_BG = "#FFFFFF"
GRID_COLOR = "#F1F5F9"
FONT_COLOR = "#374151"

CHART_LAYOUT = dict(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font=dict(color=FONT_COLOR, size=11),
    margin=dict(l=50, r=20, t=30, b=90),
    xaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=9), fixedrange=True),
    yaxis=dict(gridcolor=GRID_COLOR, fixedrange=True),
    dragmode=False,
)

CHART_CONFIG = dict(
    displayModeBar=False,
    scrollZoom=False,
)


def fiscal_week_label(d):
    """Wingstop fiscal weeks run Sunday-Saturday. Returns (week_start_date, label)."""
    from datetime import date
    if not isinstance(d, date):
        return None, "Unknown"
    days_since_sun = (d.weekday() + 1) % 7
    week_start = d - timedelta(days=days_since_sun)
    fy_start = date(2025, 12, 28)
    week_num = ((week_start - fy_start).days // 7) + 1
    return week_start, f"W{week_num}"


def parse_time_to_minutes(t):
    if pd.isna(t) or not isinstance(t, str):
        return None
    m = re.match(r"(\d+):(\d+)", str(t))
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    return None


def parse_pct(v):
    if pd.isna(v) or not isinstance(v, str):
        return None
    v = str(v).replace("%", "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def extract_store_number(name):
    m = re.match(r"(\d+)", str(name))
    return m.group(1) if m else None


def short_name(store):
    parts = str(store).split("-", 2)
    if len(parts) >= 3:
        return parts[2].strip()[:22]
    return str(store)[:22]


def forecast_short_name(store):
    parts = str(store).split(" - ", 1)
    if len(parts) == 2:
        return parts[1].strip()[:22]
    return str(store)[:22]


def forecast_store_num(store):
    m = re.match(r"0*(\d+)", str(store))
    return m.group(1) if m else None


@st.cache_data(ttl=300)
def load_kds_detailed():
    return _load_kds_excel(DATA_DIR / "kds_detailed.xlsx")


@st.cache_data(ttl=300)
def load_daily_kds():
    history_path = DATA_DIR / "kds_history.csv"
    daily_path = DATA_DIR / "smart_kitchen_daily.xlsx"

    if history_path.exists():
        df = pd.read_csv(history_path)
    elif daily_path.exists():
        df = pd.read_excel(daily_path, sheet_name="Smart Kitchen Daily", header=None, skiprows=10)
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
        df = df.dropna(subset=["STORE FULL NAME"])
        file_mod = datetime.fromtimestamp(daily_path.stat().st_mtime)
        recent_date = (file_mod - timedelta(days=1)).strftime("%Y-%m-%d")
        prior_date = (file_mod - timedelta(days=2)).strftime("%Y-%m-%d")
        df["data_date"] = df.groupby("STORE FULL NAME").cumcount().map({0: recent_date, 1: prior_date})
    else:
        return pd.DataFrame()

    df["data_date"] = pd.to_datetime(df["data_date"]).dt.date

    col_map = {}
    for c in df.columns:
        if c.strip() == "SOS (Overall)":
            col_map[c] = "SOS (Overall)"
        elif c.strip() == "SOS (Lunch)":
            col_map[c] = "SOS (Lunch)"
        elif c.strip() == "SOS (Snack)":
            col_map[c] = "SOS (Snack)"
        elif c.strip() == "SOS (Late)":
            col_map[c] = "SOS (Late)"
        elif c.strip() == "Bone in Guide Accuracy (Overall)":
            col_map[c] = "Bone in Guide Accuracy (Overall)"
    if col_map:
        df = df.rename(columns=col_map)

    df["store_num"] = df["STORE FULL NAME"].apply(extract_store_number)
    df["district"] = df["store_num"].map(STORE_TO_DISTRICT)
    df["short_name"] = df["STORE FULL NAME"].apply(short_name)

    sos_col = "SOS (Overall)" if "SOS (Overall)" in df.columns else "SOS (Overall) "
    df["sos_min"] = df[sos_col].apply(parse_time_to_minutes)
    lunch_col = "SOS (Lunch)" if "SOS (Lunch)" in df.columns else "SOS (Lunch) "
    df["sos_lunch"] = df[lunch_col].apply(parse_time_to_minutes) if lunch_col in df.columns else None
    snack_col = "SOS (Snack)" if "SOS (Snack)" in df.columns else "SOS (Snack) "
    df["sos_snack"] = df[snack_col].apply(parse_time_to_minutes) if snack_col in df.columns else None
    df["sos_dinner"] = df["SOS (Dinner)"].apply(parse_time_to_minutes) if "SOS (Dinner)" in df.columns else None
    late_col = "SOS (Late)" if "SOS (Late)" in df.columns else "SOS (Late) "
    df["sos_late"] = df[late_col].apply(parse_time_to_minutes) if late_col in df.columns else None

    df["pre_bump"] = pd.to_numeric(df["Pre Bump Rate"], errors="coerce") * 100
    df["bone_in_adopt"] = pd.to_numeric(df["Adoption of Cooks"], errors="coerce") * 100
    df["make_ahead_rate"] = pd.to_numeric(df["Make Ahead Rate"], errors="coerce") * 100
    acc_col = "Bone in Guide Accuracy (Overall)" if "Bone in Guide Accuracy (Overall)" in df.columns else "Bone in Guide Accuracy (Overall) "
    df["bone_in_accuracy"] = pd.to_numeric(df[acc_col], errors="coerce") * 100
    df["pct_7_10"] = pd.to_numeric(df["Percent Orders between 7-10 Mins"], errors="coerce") * 100
    df["waste"] = pd.to_numeric(df["Waste"], errors="coerce") * 100
    df["orders_num"] = pd.to_numeric(df["Orders"], errors="coerce")
    df["sss"] = pd.to_numeric(df["SSS"], errors="coerce") * 100
    df["aqt_var"] = df["AQT Variance"].apply(parse_time_to_minutes)

    return df


def _load_kds_excel(path):
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_excel(path, header=None, skiprows=2)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    df["store_num"] = df["Store Full Name"].apply(extract_store_number)
    df["district"] = df["store_num"].map(STORE_TO_DISTRICT)
    df["short_name"] = df["Store Full Name"].apply(short_name)
    df["sos_min"] = df["SOS"].apply(parse_time_to_minutes)
    df["pre_bump"] = pd.to_numeric(df["Pre-Bump Rate"], errors="coerce") * 100
    df["bone_in_adopt"] = pd.to_numeric(df["Bone-in Cook Adoption"], errors="coerce") * 100
    df["boneless_adopt"] = pd.to_numeric(df["Bone-less Cook Adoption"], errors="coerce") * 100
    df["bone_in_qty_var"] = pd.to_numeric(df["Bone-in Qty Variance"], errors="coerce") * 100
    df["make_ahead_rate"] = pd.to_numeric(df["Make Ahead Rate(Bone-in)"], errors="coerce") * 100
    df["bone_in_accuracy"] = pd.to_numeric(df["Bone-in Guide Accuracy"], errors="coerce") * 100
    df["pct_7_10"] = pd.to_numeric(df["Percent Orders Between 7-10 mins"], errors="coerce") * 100
    df["waste"] = pd.to_numeric(df["Bone-in Waste"], errors="coerce") * 100
    df["qt_bombardier"] = df["Queue Time Bombardier"].apply(parse_time_to_minutes)
    df["qt_gunner"] = df["Queue Time Gunner"].apply(parse_time_to_minutes)
    df["t_wingman"] = df["Time at Wingman"].apply(parse_time_to_minutes)
    df["t_pilot"] = df["Time at Pilot"].apply(parse_time_to_minutes)
    df["quadrant"] = df["Quadrant"].astype(str)
    return df


@st.cache_data(ttl=300)
def load_kds_q1():
    return _load_kds_excel(DATA_DIR / "kds_q1.xlsx")



def _load_forecast_quarter(periods):
    path = DATA_DIR / "forecast.xlsm"
    if not path.exists():
        return pd.DataFrame(), pd.DataFrame()
    raw = pd.read_excel(path, sheet_name="Forecast_Data")
    qtr = raw[(raw["year"] == 2026) & (raw["period"].isin(periods))].copy()
    if qtr.empty:
        return pd.DataFrame(), pd.DataFrame()

    store_agg = qtr.groupby(["store", "district"]).agg(
        forecast_sales=("forecast_sales", "sum"),
        actual_sales=("actual_sales", "sum"),
        guide_hours=("guide_hours", "sum"),
        schedule_hours=("schedule_hours", "sum"),
        actual_hours=("actual_crew_hours", "sum"),
        schedule_labor=("schedule_labor", "sum"),
        actual_labor=("actual_labor", "sum"),
        ovt_hours=("ovt_hours", "sum"),
        weeks=("week_d", "count"),
    ).reset_index()

    store_agg["sales_var_pct"] = (store_agg["actual_sales"] - store_agg["forecast_sales"]) / store_agg["forecast_sales"]
    store_agg["labor_var_pct"] = (store_agg["actual_hours"] - store_agg["guide_hours"]) / store_agg["guide_hours"]
    store_agg["actual_labor_pct"] = store_agg["actual_labor"] / store_agg["actual_sales"]
    store_agg["schedule_labor_pct"] = store_agg["schedule_labor"] / store_agg["forecast_sales"]
    store_agg["labor_pct_variance"] = store_agg["actual_labor_pct"] - store_agg["schedule_labor_pct"]
    store_agg["store_num"] = store_agg["store"].apply(forecast_store_num)
    store_agg["short_name"] = store_agg["store"].apply(forecast_short_name)
    store_agg["config_district"] = store_agg["store_num"].map(STORE_TO_DISTRICT)

    qtr["store_num"] = qtr["store"].apply(forecast_store_num)
    qtr["config_district"] = qtr["store_num"].map(STORE_TO_DISTRICT)
    qtr["actual_labor_pct"] = qtr["actual_labor"] / qtr["actual_sales"]
    qtr["schedule_labor_pct"] = qtr["schedule_labor"] / qtr["forecast_sales"]
    qtr["labor_pct_variance"] = qtr["actual_labor_pct"] - qtr["schedule_labor_pct"]
    qtr["short_name"] = qtr["store"].apply(forecast_short_name)

    return store_agg, qtr


@st.cache_data(ttl=300)
def load_q1_data():
    return _load_forecast_quarter([1, 2, 3])


@st.cache_data(ttl=300)
def load_q2_data():
    return _load_forecast_quarter([4, 5, 6])


kds_df_all = load_kds_detailed()
daily_df_all = load_daily_kds()
kds_q1_all = load_kds_q1()
q1_store, q1_weekly = load_q1_data()
q2_store, q2_weekly = load_q2_data()

if kds_df_all.empty and q2_store.empty:
    st.warning("No data found. Place kds_detailed.xlsx or forecast.xlsm in the data/ folder.")
    st.stop()

# ── Sidebar ──
with st.sidebar:
    st.markdown("# FL Wingmen")
    st.markdown("---")
    with st.container(border=True):
        st.markdown('<div style="background:#F0FDF4; border-left:3px solid #059669; padding:0.4rem 0.6rem; border-radius:4px; margin-bottom:0.3rem;">'
                    '<span style="color:#1A3C34; font-weight:700; font-size:0.85rem;">Filters</span></div>', unsafe_allow_html=True)

        district_options = ["All Districts"] + sorted(DISTRICTS.keys())
        selected_district = st.selectbox("District", district_options, label_visibility="collapsed")

        if not kds_df_all.empty:
            store_src = kds_df_all
        else:
            store_src = pd.DataFrame(columns=["Store Full Name", "store_num"])

        if selected_district == "All Districts":
            store_list = sorted(store_src["Store Full Name"].dropna().unique())
        else:
            district_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            store_list = sorted(store_src[store_src["store_num"].isin(district_nums)]["Store Full Name"].dropna().unique())

        store_options = ["All Stores"] + store_list
        selected_store = st.selectbox("Store", store_options, label_visibility="collapsed")

    nav_options = ["Daily KDS Snapshot", "Schedule Guide", "Sales Performance", "Labor Dashboard", "SMG (Guest Satisfaction)", "District Comparison", "Q1 Performance", "Q2 Performance", "Scorecard", "Watch List", "Trends", "Wing Worm"]
    selected_tab = st.radio("Navigation", nav_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"**{len(store_src)}** stores | **{len(DISTRICTS)}** districts")

# ── Header ──
filter_text = "All Stores"
if selected_store != "All Stores":
    filter_text = short_name(selected_store)
elif selected_district != "All Districts":
    filter_text = selected_district

st.markdown(f"""
<div class="dash-header">
    <h1>FL Wingmen Dashboard</h1>
    <p>{filter_text} &nbsp;|&nbsp; {len(DISTRICTS)} districts</p>
</div>
""", unsafe_allow_html=True)


def kpi_card(label, value, color=""):
    cls = f" {color}" if color else ""
    return f"""<div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value{cls}">{value}</div>
    </div>"""


# ════════════════════════════════
# DAILY KDS SNAPSHOT
# ════════════════════════════════
if selected_tab == "Daily KDS Snapshot":

    if daily_df_all.empty:
        st.warning("No daily KDS data found. Run fetch_outlook.py to grab the Smart Kitchen Daily email.")
    else:
        available_dates = sorted(daily_df_all["data_date"].dropna().unique(), reverse=True)

        week_map = {}
        for d in available_dates:
            ws, wl = fiscal_week_label(d)
            today_ws, _ = fiscal_week_label(datetime.now().date())
            label = "Current Week" if ws == today_ws else f"2026 {wl}"
            week_map.setdefault(label, []).append(d)

        week_options = list(week_map.keys())
        default_week_idx = 1 if "Current Week" in week_options else 0

        quarter_map = {}
        for d in available_dates:
            _, wl = fiscal_week_label(d)
            wnum = int(wl[1:])
            if wnum <= 13:
                quarter_map.setdefault("Q1 (W1-W13)", []).append(d)
            else:
                quarter_map.setdefault("Q2 (W14-W26)", []).append(d)

        period_options = list(quarter_map.keys()) + ["All Weeks"] + week_options

        fw1, fw2 = st.columns(2)
        with fw1:
            selected_week = st.selectbox(
                "Fiscal Week", period_options,
                index=period_options.index("Current Week") if "Current Week" in period_options else 0,
                key="fiscal_week_picker",
            )
        with fw2:
            if selected_week in quarter_map:
                date_choices = sorted(quarter_map[selected_week], reverse=True)
            elif selected_week == "All Weeks":
                date_choices = available_dates
            else:
                date_choices = sorted(week_map[selected_week], reverse=True)
            date_labels = {d: f"{d.strftime('%A')}, {d.strftime('%B')} {d.day}, {d.year}" for d in date_choices}
            is_group = selected_week != "All Weeks"
            group_label = "Entire Quarter" if selected_week in quarter_map else "Entire Week"
            date_options = [group_label] + list(date_choices) if is_group else list(date_choices)
            selected_date_option = st.selectbox(
                "Date", date_options,
                format_func=lambda d: d if d in ("Entire Week", "Entire Quarter") else date_labels.get(d, str(d)),
                key="daily_date_picker",
            )

        if selected_date_option in ("Entire Week", "Entire Quarter"):
            filter_dates = set(date_choices)
            is_agg_view = True
        else:
            filter_dates = {selected_date_option}
            is_agg_view = False

        kds = daily_df_all[daily_df_all["data_date"].isin(filter_dates)].copy()
        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            kds = kds[kds["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            kds = kds[kds["store_num"].isin(d_nums)]

        if is_agg_view and len(filter_dates) > 1:
            kds = kds.groupby(["store_num", "district", "short_name", "STORE FULL NAME"], dropna=False).agg(
                sos_min=("sos_min", "mean"), sos_lunch=("sos_lunch", "mean"),
                sos_snack=("sos_snack", "mean"), sos_dinner=("sos_dinner", "mean"),
                sos_late=("sos_late", "mean"), pre_bump=("pre_bump", "mean"),
                bone_in_adopt=("bone_in_adopt", "mean"), make_ahead_rate=("make_ahead_rate", "mean"),
                bone_in_accuracy=("bone_in_accuracy", "mean"), pct_7_10=("pct_7_10", "mean"),
                waste=("waste", "mean"), orders_num=("orders_num", "sum"),
                sss=("sss", "mean"), aqt_var=("aqt_var", "mean"),
            ).reset_index()

        history_path = DATA_DIR / "kds_history.csv"
        check_path = history_path if history_path.exists() else DATA_DIR / "smart_kitchen_daily.xlsx"
        if check_path.exists():
            file_mod = datetime.fromtimestamp(check_path.stat().st_mtime)
            freshness = (datetime.now() - file_mod).total_seconds() / 3600
            fresh_tag = ' <span style="color:#059669;">&#9679; Updated today</span>' if freshness < 18 else ' <span style="color:#DC2626;">&#9679; Stale data</span>'
        else:
            fresh_tag = ""

        if is_agg_view:
            date_range = sorted(filter_dates)
            if date_range:
                date_display = f"{selected_week} ({date_range[0].strftime('%m/%d')} - {date_range[-1].strftime('%m/%d')}) &mdash; {len(date_range)} day avg"
            else:
                date_display = selected_week
        else:
            date_display = date_labels.get(selected_date_option, str(selected_date_option))
        st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Data as of <span style="color:#059669; font-weight:600;">{date_display}</span> &nbsp;|&nbsp; {len(kds)} stores{fresh_tag}</p>', unsafe_allow_html=True)

        # ── 5 Key KPI Cards ──
        k1, k2, k3, k4, k5 = st.columns(5)
        avg_sos = kds["sos_min"].mean() if kds["sos_min"].notna().any() else 0
        avg_prebump = kds["pre_bump"].mean() if kds["pre_bump"].notna().any() else 0
        avg_adopt = kds["bone_in_adopt"].mean() if kds["bone_in_adopt"].notna().any() else 0
        avg_make = kds["make_ahead_rate"].mean() if kds["make_ahead_rate"].notna().any() else 0
        avg_waste = kds["waste"].mean() if kds["waste"].notna().any() else 0

        sos_c = "green" if avg_sos < 10 else ("orange" if avg_sos < 13 else "red")
        pb_c = "green" if avg_prebump <= 0.5 else ("orange" if avg_prebump <= 1.5 else "red")
        adopt_c = "green" if avg_adopt >= 85 else "red"
        ma_c = "green" if avg_make <= 10 else "red"
        waste_c = "green" if avg_waste <= 5 else "red"

        k1.markdown(kpi_card("Avg SOS", f"{avg_sos:.1f} min", sos_c), unsafe_allow_html=True)
        k2.markdown(kpi_card("Pre-Bump Rate", f"{avg_prebump:.2f}%", pb_c), unsafe_allow_html=True)
        k3.markdown(kpi_card("Cook Adoption", f"{avg_adopt:.1f}%", adopt_c), unsafe_allow_html=True)
        k4.markdown(kpi_card("Make Ahead Rate", f"{avg_make:.1f}%", ma_c), unsafe_allow_html=True)
        k5.markdown(kpi_card("Waste", f"{avg_waste:.2f}%", waste_c), unsafe_allow_html=True)

        st.markdown("")

        # ── SOS Overall by Store ──
        st.markdown('<div class="section-title">Speed of Service (Overall) by Store</div>', unsafe_allow_html=True)
        sos_kds = kds[kds["sos_min"].notna()].sort_values("sos_min")
        sos_colors = [RED if v >= 13 else (ORANGE if v >= 10 else TEAL) for v in sos_kds["sos_min"]]
        fig_sos_k = go.Figure(go.Bar(
            x=sos_kds["short_name"], y=sos_kds["sos_min"],
            marker_color=sos_colors,
            hovertemplate="%{x}<br>SOS: %{y:.1f} min<extra></extra>",
        ))
        fig_sos_k.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1.5,
                            annotation_text="10 min target", annotation_font=dict(color="#DC2626", size=10))
        fig_sos_k.update_layout(**CHART_LAYOUT, height=380,
                                yaxis_title="Minutes", xaxis_tickangle=-45)
        st.plotly_chart(fig_sos_k, use_container_width=True, key="kds_sos", config=CHART_CONFIG)

        # ── SOS by Daypart ──
        st.markdown('<div class="section-title">SOS by Daypart</div>', unsafe_allow_html=True)
        daypart_kds = kds[kds["sos_min"].notna()].sort_values("sos_min")
        fig_dp = go.Figure()
        dayparts = [
            ("sos_lunch", "Lunch", "#059669"),
            ("sos_snack", "Snack", TEAL),
            ("sos_dinner", "Dinner", ORANGE),
            ("sos_late", "Late", "#AB47BC"),
        ]
        for col, name, color in dayparts:
            if col in daypart_kds.columns and daypart_kds[col].notna().any():
                fig_dp.add_trace(go.Bar(
                    x=daypart_kds["short_name"], y=daypart_kds[col],
                    name=name, marker_color=color,
                    hovertemplate=f"%{{x}}<br>{name}: %{{y:.1f}} min<extra></extra>",
                ))
        fig_dp.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1.5,
                         annotation_text="10 min target", annotation_font=dict(color="#DC2626", size=10))
        fig_dp.update_layout(
            **CHART_LAYOUT, barmode="group", height=420,
            yaxis_title="Minutes", xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(color="#374151")),
        )
        st.plotly_chart(fig_dp, use_container_width=True, key="kds_daypart", config=CHART_CONFIG)

        # ── Pre-Bump Rate & Cook Adoption ──
        pb_l, pb_r = st.columns(2)
        with pb_l:
            st.markdown('<div class="section-title">Pre-Bump Rate by Store</div>', unsafe_allow_html=True)
            pb_kds = kds[kds["pre_bump"].notna()].sort_values("pre_bump", ascending=False)
            pb_colors = [RED if v > 1.5 else (ORANGE if v > 0.5 else TEAL) for v in pb_kds["pre_bump"]]
            fig_pb = go.Figure(go.Bar(
                x=pb_kds["short_name"], y=pb_kds["pre_bump"],
                marker_color=pb_colors,
                hovertemplate="%{x}<br>Pre-Bump: %{y:.2f}%<extra></extra>",
            ))
            fig_pb.update_layout(**CHART_LAYOUT, height=370,
                                 yaxis_title="Pre-Bump %", xaxis_tickangle=-45)
            st.plotly_chart(fig_pb, use_container_width=True, key="kds_pb", config=CHART_CONFIG)

        with pb_r:
            st.markdown('<div class="section-title">Adoption of Cooks by Store</div>', unsafe_allow_html=True)
            ad_kds = kds[kds["bone_in_adopt"].notna()].sort_values("bone_in_adopt")
            ad_colors = [RED if v < 85 else "#059669" for v in ad_kds["bone_in_adopt"]]
            fig_ad = go.Figure(go.Bar(
                x=ad_kds["short_name"], y=ad_kds["bone_in_adopt"],
                marker_color=ad_colors,
                hovertemplate="%{x}<br>Adoption: %{y:.1f}%<extra></extra>",
            ))
            fig_ad.add_hline(y=100, line_dash="dash", line_color=GREEN, line_width=1.5,
                             annotation_text="100%", annotation_font=dict(color="#059669", size=10))
            fig_ad.update_layout(**CHART_LAYOUT, height=370,
                                 yaxis_title="Adoption %", xaxis_tickangle=-45)
            st.plotly_chart(fig_ad, use_container_width=True, key="kds_adopt", config=CHART_CONFIG)

        # ── Make Ahead & Waste ──
        ma_l, ma_r = st.columns(2)
        with ma_l:
            st.markdown('<div class="section-title">Make Ahead Rate by Store</div>', unsafe_allow_html=True)
            ma_kds = kds[kds["make_ahead_rate"].notna()].sort_values("make_ahead_rate")
            ma_colors = [RED if v > 10 else "#059669" for v in ma_kds["make_ahead_rate"]]
            fig_ma = go.Figure(go.Bar(
                x=ma_kds["short_name"], y=ma_kds["make_ahead_rate"],
                marker_color=ma_colors,
                hovertemplate="%{x}<br>Make Ahead: %{y:.1f}%<extra></extra>",
            ))
            fig_ma.update_layout(**CHART_LAYOUT, height=370,
                                 yaxis_title="Make Ahead %", xaxis_tickangle=-45)
            st.plotly_chart(fig_ma, use_container_width=True, key="kds_ma", config=CHART_CONFIG)

        with ma_r:
            st.markdown('<div class="section-title">Waste % by Store</div>', unsafe_allow_html=True)
            w_kds = kds[kds["waste"].notna()].sort_values("waste", ascending=False)
            w_colors = [RED if v > 5 else TEAL for v in w_kds["waste"]]
            fig_w = go.Figure(go.Bar(
                x=w_kds["short_name"], y=w_kds["waste"],
                marker_color=w_colors,
                hovertemplate="%{x}<br>Waste: %{y:.2f}%<extra></extra>",
            ))
            fig_w.update_layout(**CHART_LAYOUT, height=370,
                                yaxis_title="Waste %", xaxis_tickangle=-45)
            st.plotly_chart(fig_w, use_container_width=True, key="kds_waste", config=CHART_CONFIG)

        # ── Bone-In Accuracy & % Orders 7-10 min ──
        ex1, ex2 = st.columns(2)
        with ex1:
            st.markdown('<div class="section-title">Bone-In Guide Accuracy</div>', unsafe_allow_html=True)
            acc_kds = kds[kds["bone_in_accuracy"].notna()].sort_values("bone_in_accuracy")
            fig_acc = go.Figure(go.Bar(
                x=acc_kds["short_name"], y=acc_kds["bone_in_accuracy"],
                marker_color=DARK,
                hovertemplate="%{x}<br>Accuracy: %{y:.1f}%<extra></extra>",
            ))
            fig_acc.add_hline(y=100, line_dash="dash", line_color=GREEN, line_width=1.5,
                              annotation_text="100%", annotation_font=dict(color="#059669", size=10))
            fig_acc.update_layout(**CHART_LAYOUT, height=350,
                                  yaxis_title="Accuracy %", xaxis_tickangle=-45)
            st.plotly_chart(fig_acc, use_container_width=True, key="kds_acc", config=CHART_CONFIG)

        with ex2:
            st.markdown('<div class="section-title">% Orders Between 7-10 Minutes</div>', unsafe_allow_html=True)
            pct_kds = kds[kds["pct_7_10"].notna()].sort_values("pct_7_10", ascending=False)
            fig_pct = go.Figure(go.Bar(
                x=pct_kds["short_name"], y=pct_kds["pct_7_10"],
                marker_color=ORANGE,
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
            ))
            fig_pct.update_layout(**CHART_LAYOUT, height=350,
                                  yaxis_title="% Orders 7-10 min", xaxis_tickangle=-45)
            st.plotly_chart(fig_pct, use_container_width=True, key="kds_pct", config=CHART_CONFIG)

        # ── Daily KDS Detail Table ──
        st.markdown('<div class="section-title">Daily Store Details</div>', unsafe_allow_html=True)
        detail_cols = ["short_name", "district", "sos_min", "sos_lunch", "sos_snack",
                       "sos_dinner", "sos_late", "pre_bump", "bone_in_adopt",
                       "make_ahead_rate", "bone_in_accuracy", "waste", "pct_7_10", "orders_num"]
        detail_cols = [c for c in detail_cols if c in kds.columns]
        detail = kds[detail_cols].copy()
        col_names = {
            "short_name": "Store", "district": "District", "sos_min": "SOS",
            "sos_lunch": "Lunch", "sos_snack": "Snack", "sos_dinner": "Dinner",
            "sos_late": "Late", "pre_bump": "Pre-Bump %", "bone_in_adopt": "Adoption %",
            "make_ahead_rate": "Make Ahead %", "bone_in_accuracy": "Accuracy %",
            "waste": "Waste %", "pct_7_10": "% 7-10 min", "orders_num": "Orders",
        }
        detail = detail.rename(columns=col_names)
        detail = detail.sort_values("SOS")
        st.dataframe(detail, use_container_width=True, hide_index=True)

# ════════════════════════════════
# SCHEDULE GUIDE
# ════════════════════════════════
elif selected_tab == "Schedule Guide":
    st.markdown('<div class="section-title">Scheduling Guide</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6B7280; font-size:0.85rem;">Weekly sales forecast and ideal staffing hours by store. Hours guide applies to hourly staff only (excludes GMs).</p>', unsafe_allow_html=True)

    sched_file = DATA_DIR / "schedule_guide.csv"
    if sched_file.exists():
        sched_df = pd.read_csv(sched_file)

        # Period selector
        periods_avail = sorted(sched_df["Period"].unique().tolist())
        sel_period = st.selectbox("Select Week", periods_avail, index=len(periods_avail) - 1)
        week_data = sched_df[sched_df["Period"] == sel_period].copy()
        start_dt = week_data["Start Date"].iloc[0] if len(week_data) > 0 else ""
        end_dt = week_data["End Date"].iloc[0] if len(week_data) > 0 else ""

        st.markdown(f'<p style="color:#374151; font-size:0.9rem; font-weight:600;">Week: {start_dt} — {end_dt}</p>', unsafe_allow_html=True)

        # KPIs
        total_sales = week_data["Sales Forecast"].sum()
        total_hours = week_data["Hours Guide"].sum()
        n_stores = week_data["Store No"].nunique()
        avg_sales = total_sales / n_stores if n_stores else 0
        avg_hours = total_hours / n_stores if n_stores else 0

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f'<div class="kpi-box"><div class="kpi-label">Total Sales Forecast</div><div class="kpi-value">${total_sales:,.0f}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-box"><div class="kpi-label">Total Hours Guide</div><div class="kpi-value">{total_hours:,.0f}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-box"><div class="kpi-label">Stores</div><div class="kpi-value">{n_stores}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-box"><div class="kpi-label">Avg Sales / Store</div><div class="kpi-value">${avg_sales:,.0f}</div></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="kpi-box"><div class="kpi-label">Avg Hours / Store</div><div class="kpi-value">{avg_hours:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        # District filter
        districts = sorted(week_data["District"].unique().tolist())
        sel_district = st.selectbox("Filter by District", ["All Districts"] + districts)
        if sel_district != "All Districts":
            week_data = week_data[week_data["District"] == sel_district]

        # Show data grouped by district like the PDF
        for district in sorted(week_data["District"].unique()):
            d_data = week_data[week_data["District"] == district].copy()
            d_sales = d_data["Sales Forecast"].sum()
            d_hours = d_data["Hours Guide"].sum()

            st.markdown(f"""
            <div style="background:#1A3C34; color:#FFFFFF; padding:0.5rem 1rem; border-radius:6px 6px 0 0; margin-top:1rem;
                        display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; font-size:0.95rem;">{district}</span>
                <span style="font-size:0.82rem;">Sales: <b>${d_sales:,.0f}</b> &nbsp;|&nbsp; Hours: <b>{d_hours:,.0f}</b></span>
            </div>
            """, unsafe_allow_html=True)

            display_df = d_data[["Store No", "Store Name", "Sales Forecast", "Hours Guide"]].copy()
            display_df["Sales Forecast"] = display_df["Sales Forecast"].apply(lambda x: f"${x:,.0f}")
            display_df["Hours Guide"] = display_df["Hours Guide"].apply(lambda x: f"{x:,.0f}")
            display_df = display_df.reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        # District comparison chart
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size:1rem;">District Comparison</div>', unsafe_allow_html=True)

        dist_summary = week_data.groupby("District").agg(
            Sales=("Sales Forecast", "sum"),
            Hours=("Hours Guide", "sum"),
            Stores=("Store No", "nunique"),
        ).reset_index()

        col_a, col_b = st.columns(2)
        with col_a:
            fig_s = px.bar(dist_summary, x="District", y="Sales", text_auto="$,.0f",
                           color_discrete_sequence=[GREEN])
            sched_layout = {**CHART_LAYOUT, "yaxis": dict(gridcolor=GRID_COLOR, fixedrange=True, title="Sales Forecast ($)")}
            fig_s.update_layout(**sched_layout, title="Sales Forecast by District")
            fig_s.update_traces(textposition="outside")
            st.plotly_chart(fig_s, use_container_width=True, config=CHART_CONFIG)
        with col_b:
            fig_h = px.bar(dist_summary, x="District", y="Hours", text_auto=",.0f",
                           color_discrete_sequence=[TEAL])
            hours_layout = {**CHART_LAYOUT, "yaxis": dict(gridcolor=GRID_COLOR, fixedrange=True, title="Hours Guide")}
            fig_h.update_layout(**hours_layout, title="Hours Guide by District")
            fig_h.update_traces(textposition="outside")
            st.plotly_chart(fig_h, use_container_width=True, config=CHART_CONFIG)

        # Trend across weeks if multiple periods
        if len(periods_avail) > 1:
            st.markdown('<div class="section-title" style="font-size:1rem;">Week-over-Week Trend</div>', unsafe_allow_html=True)
            trend_df = sched_df.groupby("Period").agg(
                Sales=("Sales Forecast", "sum"),
                Hours=("Hours Guide", "sum"),
            ).reindex(periods_avail).reset_index()

            col_c, col_d = st.columns(2)
            with col_c:
                fig_ts = px.line(trend_df, x="Period", y="Sales", markers=True, color_discrete_sequence=[GREEN])
                ts_layout = {**CHART_LAYOUT, "yaxis": dict(gridcolor=GRID_COLOR, fixedrange=True, title="Total Sales ($)")}
                fig_ts.update_layout(**ts_layout, title="Total Sales by Week")
                st.plotly_chart(fig_ts, use_container_width=True, config=CHART_CONFIG)
            with col_d:
                fig_th = px.line(trend_df, x="Period", y="Hours", markers=True, color_discrete_sequence=[TEAL])
                th_layout = {**CHART_LAYOUT, "yaxis": dict(gridcolor=GRID_COLOR, fixedrange=True, title="Total Hours")}
                fig_th.update_layout(**th_layout, title="Total Hours by Week")
                st.plotly_chart(fig_th, use_container_width=True, config=CHART_CONFIG)
    else:
        st.warning("No schedule data found. Place schedule_guide.csv in the data/ folder.")

# ════════════════════════════════
# Q1 PERFORMANCE
# ════════════════════════════════
elif selected_tab == "Q1 Performance":

    if kds_q1_all.empty and q1_store.empty:
        st.warning("No Q1 data found. Place kds_q1.xlsx and/or forecast.xlsm in the data/ folder.")
    else:
        # Filter by sidebar
        q1k = kds_q1_all.copy()
        q1f = q1_store.copy()
        q1w = q1_weekly.copy()
        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            q1k = q1k[q1k["store_num"] == sk_num]
            q1f = q1f[q1f["store_num"] == sk_num]
            q1w = q1w[q1w["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            q1k = q1k[q1k["store_num"].isin(d_nums)]
            q1f = q1f[q1f["store_num"].isin(d_nums)]
            q1w = q1w[q1w["store_num"].isin(d_nums)]

        st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Q1 2026 (Periods 1-3, Weeks 1-13) &nbsp;|&nbsp; {len(q1k)} stores KDS &nbsp;|&nbsp; {len(q1f)} stores forecast</p>', unsafe_allow_html=True)

        # ── KDS KPI Cards ──
        k1, k2, k3, k4, k5 = st.columns(5)
        if not q1k.empty:
            avg_sos = q1k["sos_min"].mean() if q1k["sos_min"].notna().any() else 0
            avg_pb = q1k["pre_bump"].mean() if q1k["pre_bump"].notna().any() else 0
            avg_adopt = q1k["bone_in_adopt"].mean() if q1k["bone_in_adopt"].notna().any() else 0
            avg_qv = q1k["bone_in_qty_var"].mean() if q1k["bone_in_qty_var"].notna().any() else 0
            avg_ma = q1k["make_ahead_rate"].mean() if q1k["make_ahead_rate"].notna().any() else 0
        else:
            avg_sos = avg_pb = avg_adopt = avg_qv = avg_ma = 0

        sos_c = "green" if avg_sos < 10 else ("orange" if avg_sos < 13 else "red")
        pb_c = "green" if avg_pb < 1 else ("orange" if avg_pb < 3 else "red")
        adopt_c = "green" if avg_adopt >= 97 else ("orange" if avg_adopt >= 90 else "red")
        qv_c = "green" if abs(avg_qv) < 3 else ("orange" if abs(avg_qv) < 6 else "red")
        ma_c = "green" if avg_ma >= 80 else ("orange" if avg_ma >= 50 else "red")

        k1.markdown(kpi_card("Avg SOS", f"{avg_sos:.1f} min", sos_c), unsafe_allow_html=True)
        k2.markdown(kpi_card("Pre-Bump Rate", f"{avg_pb:.2f}%", pb_c), unsafe_allow_html=True)
        k3.markdown(kpi_card("Bone-In Adoption", f"{avg_adopt:.1f}%", adopt_c), unsafe_allow_html=True)
        k4.markdown(kpi_card("Bone-In Qty Var", f"{avg_qv:+.2f}%", qv_c), unsafe_allow_html=True)
        k5.markdown(kpi_card("Make Ahead Rate", f"{avg_ma:.1f}%", ma_c), unsafe_allow_html=True)

        # ── Labor KPI Cards ──
        if not q1f.empty:
            st.markdown("")
            l1, l2, l3, l4 = st.columns(4)
            total_actual = q1f["actual_sales"].sum()
            total_forecast = q1f["forecast_sales"].sum()
            total_var = (total_actual - total_forecast) / total_forecast if total_forecast else 0
            avg_labor_var = q1f["labor_pct_variance"].mean() if q1f["labor_pct_variance"].notna().any() else 0
            avg_actual_labor = q1f["actual_labor_pct"].mean() if q1f["actual_labor_pct"].notna().any() else 0
            total_ovt = q1f["ovt_hours"].sum()

            sales_c = "green" if total_var >= 0 else "red"
            labor_c = "green" if avg_labor_var <= 0 else ("orange" if avg_labor_var < 0.02 else "red")

            l1.markdown(kpi_card("Q1 Actual Sales", f"${total_actual:,.0f}", sales_c), unsafe_allow_html=True)
            l2.markdown(kpi_card("Sales vs Forecast", f"{total_var:+.1%}", sales_c), unsafe_allow_html=True)
            l3.markdown(kpi_card("Avg Labor %", f"{avg_actual_labor:.1%}"), unsafe_allow_html=True)
            l4.markdown(kpi_card("Avg Labor Variance", f"{avg_labor_var:+.2%}", labor_c), unsafe_allow_html=True)

        st.markdown("")

        # ── SOS by Store ──
        if not q1k.empty:
            st.markdown('<div class="section-title">Q1 Speed of Service by Store</div>', unsafe_allow_html=True)
            sos_q1 = q1k[q1k["sos_min"].notna()].sort_values("sos_min")
            sos_colors = [RED if v > 12 else (ORANGE if v > 10 else TEAL) for v in sos_q1["sos_min"]]
            fig_sos_q1 = go.Figure(go.Bar(
                x=sos_q1["short_name"], y=sos_q1["sos_min"],
                marker_color=sos_colors,
                hovertemplate="%{x}<br>SOS: %{y:.1f} min<extra></extra>",
            ))
            fig_sos_q1.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1.5,
                                 annotation_text="10 min target", annotation_font=dict(color="#DC2626", size=10))
            fig_sos_q1.update_layout(**CHART_LAYOUT, height=380,
                                     yaxis_title="Minutes", xaxis_tickangle=-45)
            st.plotly_chart(fig_sos_q1, use_container_width=True, key="q1_sos", config=CHART_CONFIG)

            # ── Pre-Bump & Bone-In Adoption ──
            pb_l, pb_r = st.columns(2)
            with pb_l:
                st.markdown('<div class="section-title">Q1 Pre-Bump Rate</div>', unsafe_allow_html=True)
                pb_q1 = q1k[q1k["pre_bump"].notna()].sort_values("pre_bump", ascending=False)
                pb_colors = [RED if v > 3 else (ORANGE if v > 1 else TEAL) for v in pb_q1["pre_bump"]]
                fig_pb_q1 = go.Figure(go.Bar(
                    x=pb_q1["short_name"], y=pb_q1["pre_bump"],
                    marker_color=pb_colors,
                    hovertemplate="%{x}<br>Pre-Bump: %{y:.2f}%<extra></extra>",
                ))
                fig_pb_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Pre-Bump %", xaxis_tickangle=-45)
                st.plotly_chart(fig_pb_q1, use_container_width=True, key="q1_pb", config=CHART_CONFIG)

            with pb_r:
                st.markdown('<div class="section-title">Q1 Bone-In Adoption</div>', unsafe_allow_html=True)
                ad_q1 = q1k[q1k["bone_in_adopt"].notna()].sort_values("bone_in_adopt")
                ad_colors = [RED if v < 90 else (ORANGE if v < 97 else "#059669") for v in ad_q1["bone_in_adopt"]]
                fig_ad_q1 = go.Figure(go.Bar(
                    x=ad_q1["short_name"], y=ad_q1["bone_in_adopt"],
                    marker_color=ad_colors,
                    hovertemplate="%{x}<br>Adoption: %{y:.1f}%<extra></extra>",
                ))
                fig_ad_q1.add_hline(y=100, line_dash="dash", line_color=GREEN, line_width=1.5,
                                    annotation_text="100%", annotation_font=dict(color="#059669", size=10))
                fig_ad_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Adoption %", xaxis_tickangle=-45)
                st.plotly_chart(fig_ad_q1, use_container_width=True, key="q1_adopt", config=CHART_CONFIG)

            # ── Qty Variance & Make Ahead ──
            qv_l, qv_r = st.columns(2)
            with qv_l:
                st.markdown('<div class="section-title">Q1 Bone-In Qty Variance</div>', unsafe_allow_html=True)
                qv_q1 = q1k[q1k["bone_in_qty_var"].notna()].sort_values("bone_in_qty_var")
                qv_colors = [RED if abs(v) > 6 else (ORANGE if abs(v) > 3 else "#059669") for v in qv_q1["bone_in_qty_var"]]
                fig_qv_q1 = go.Figure(go.Bar(
                    x=qv_q1["short_name"], y=qv_q1["bone_in_qty_var"],
                    marker_color=qv_colors,
                    hovertemplate="%{x}<br>Qty Var: %{y:+.2f}%<extra></extra>",
                ))
                fig_qv_q1.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_qv_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Qty Variance %", xaxis_tickangle=-45)
                st.plotly_chart(fig_qv_q1, use_container_width=True, key="q1_qv", config=CHART_CONFIG)

            with qv_r:
                st.markdown('<div class="section-title">Q1 Make Ahead Rate</div>', unsafe_allow_html=True)
                ma_q1 = q1k[q1k["make_ahead_rate"].notna()].sort_values("make_ahead_rate")
                ma_colors = [RED if v < 50 else (ORANGE if v < 80 else "#059669") for v in ma_q1["make_ahead_rate"]]
                fig_ma_q1 = go.Figure(go.Bar(
                    x=ma_q1["short_name"], y=ma_q1["make_ahead_rate"],
                    marker_color=ma_colors,
                    hovertemplate="%{x}<br>Make Ahead: %{y:.1f}%<extra></extra>",
                ))
                fig_ma_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Make Ahead %", xaxis_tickangle=-45)
                st.plotly_chart(fig_ma_q1, use_container_width=True, key="q1_ma", config=CHART_CONFIG)

        # ── Labor Variance by Store ──
        if not q1f.empty:
            st.markdown('<div class="section-title">Q1 Labor Variance % by Store</div>', unsafe_allow_html=True)
            lv_q1 = q1f[q1f["labor_pct_variance"].notna()].sort_values("labor_pct_variance")
            lv_colors = [RED if v > 0 else ("#059669" if v < -0.02 else TEAL) for v in lv_q1["labor_pct_variance"]]
            fig_lv_q1 = go.Figure(go.Bar(
                x=lv_q1["short_name"],
                y=lv_q1["labor_pct_variance"] * 100,
                marker_color=lv_colors,
                hovertemplate="%{x}<br>Labor Var: %{y:+.2f}%<extra></extra>",
            ))
            fig_lv_q1.add_hline(y=0, line_color="#BDBDBD", line_width=1)
            fig_lv_q1.update_layout(**CHART_LAYOUT, height=400,
                                    yaxis_title="Labor Variance %", xaxis_tickangle=-45)
            st.plotly_chart(fig_lv_q1, use_container_width=True, key="q1_lv", config=CHART_CONFIG)

            # ── Sales Variance & Actual Labor % ──
            sv_l, sv_r = st.columns(2)
            with sv_l:
                st.markdown('<div class="section-title">Q1 Sales vs Forecast Variance</div>', unsafe_allow_html=True)
                sv_q1 = q1f.sort_values("sales_var_pct")
                sv_colors = [RED if v < -0.05 else (ORANGE if v < 0 else "#059669") for v in sv_q1["sales_var_pct"]]
                fig_sv_q1 = go.Figure(go.Bar(
                    x=sv_q1["short_name"],
                    y=sv_q1["sales_var_pct"] * 100,
                    marker_color=sv_colors,
                    hovertemplate="%{x}<br>Sales Var: %{y:+.1f}%<extra></extra>",
                ))
                fig_sv_q1.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_sv_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Sales Variance %", xaxis_tickangle=-45)
                st.plotly_chart(fig_sv_q1, use_container_width=True, key="q1_sv", config=CHART_CONFIG)

            with sv_r:
                st.markdown('<div class="section-title">Q1 Actual Labor % by Store</div>', unsafe_allow_html=True)
                al_q1 = q1f.sort_values("actual_labor_pct", ascending=False)
                al_colors = [RED if v > 0.20 else (ORANGE if v > 0.16 else TEAL) for v in al_q1["actual_labor_pct"]]
                fig_al_q1 = go.Figure(go.Bar(
                    x=al_q1["short_name"],
                    y=al_q1["actual_labor_pct"] * 100,
                    marker_color=al_colors,
                    hovertemplate="%{x}<br>Labor: %{y:.1f}%<extra></extra>",
                ))
                fig_al_q1.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Labor %", xaxis_tickangle=-45)
                st.plotly_chart(fig_al_q1, use_container_width=True, key="q1_al", config=CHART_CONFIG)

            # ── Weekly Labor Trend ──
            if not q1w.empty:
                st.markdown('<div class="section-title">Q1 Weekly Labor Variance Trend</div>', unsafe_allow_html=True)
                wk_agg = q1w.groupby("week_d").agg(
                    actual_labor=("actual_labor", "sum"),
                    actual_sales=("actual_sales", "sum"),
                    schedule_labor=("schedule_labor", "sum"),
                    forecast_sales=("forecast_sales", "sum"),
                ).reset_index()
                wk_agg["actual_labor_pct"] = wk_agg["actual_labor"] / wk_agg["actual_sales"]
                wk_agg["schedule_labor_pct"] = wk_agg["schedule_labor"] / wk_agg["forecast_sales"]

                fig_wk_q1 = go.Figure()
                fig_wk_q1.add_trace(go.Scatter(
                    x=wk_agg["week_d"], y=wk_agg["actual_labor_pct"] * 100,
                    name="Actual Labor %", mode="lines+markers",
                    line=dict(color=ORANGE, width=2), marker=dict(size=8),
                ))
                fig_wk_q1.add_trace(go.Scatter(
                    x=wk_agg["week_d"], y=wk_agg["schedule_labor_pct"] * 100,
                    name="Scheduled Labor %", mode="lines+markers",
                    line=dict(color=TEAL, width=2, dash="dash"), marker=dict(size=8),
                ))
                fig_wk_q1.update_layout(
                    **CHART_LAYOUT, height=350,
                    yaxis_title="Labor %",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(color="#374151")),
                )
                st.plotly_chart(fig_wk_q1, use_container_width=True, key="q1_wk", config=CHART_CONFIG)

            # ── Q1 Detail Table ──
            st.markdown('<div class="section-title">Q1 Store Details (Labor)</div>', unsafe_allow_html=True)
            tbl = q1f[["store", "config_district", "actual_sales", "forecast_sales",
                        "sales_var_pct", "actual_labor_pct", "schedule_labor_pct",
                        "labor_pct_variance", "ovt_hours", "weeks"]].copy()
            tbl.columns = ["Store", "District", "Actual Sales", "Forecast Sales",
                            "Sales Var %", "Actual Labor %", "Sched Labor %",
                            "Labor Variance %", "OT Hours", "Weeks"]
            tbl["Actual Sales"] = tbl["Actual Sales"].apply(lambda x: f"${x:,.0f}")
            tbl["Forecast Sales"] = tbl["Forecast Sales"].apply(lambda x: f"${x:,.0f}")
            tbl["Sales Var %"] = tbl["Sales Var %"].apply(lambda x: f"{x:+.1%}")
            tbl["Actual Labor %"] = tbl["Actual Labor %"].apply(lambda x: f"{x:.1%}")
            tbl["Sched Labor %"] = tbl["Sched Labor %"].apply(lambda x: f"{x:.1%}")
            tbl["Labor Variance %"] = tbl["Labor Variance %"].apply(lambda x: f"{x:+.2%}")
            tbl["OT Hours"] = tbl["OT Hours"].apply(lambda x: f"{x:.1f}")
            tbl = tbl.sort_values("Store")
            st.dataframe(tbl, use_container_width=True, hide_index=True)

        # ── Q1 KDS Detail Table ──
        if not q1k.empty:
            st.markdown('<div class="section-title">Q1 KDS Store Details</div>', unsafe_allow_html=True)
            detail = q1k[["short_name", "district", "sos_min", "pre_bump", "bone_in_adopt",
                           "bone_in_qty_var", "make_ahead_rate", "bone_in_accuracy",
                           "waste", "pct_7_10", "quadrant"]].copy()
            detail.columns = ["Store", "District", "SOS (min)", "Pre-Bump %", "BI Adoption %",
                              "BI Qty Var %", "Make Ahead %", "BI Accuracy %",
                              "Waste %", "% 7-10 min", "Quadrant"]
            detail = detail.sort_values("SOS (min)")
            st.dataframe(detail, use_container_width=True, hide_index=True)

# ════════════════════════════════
# Q2 PERFORMANCE
# ════════════════════════════════
elif selected_tab == "Q2 Performance":

    if kds_df_all.empty and q2_store.empty:
        st.warning("No Q2 data found. Place kds_detailed.xlsx and/or forecast.xlsm in the data/ folder.")
    else:
        # Filter Q2 data by sidebar selection
        q2k = kds_df_all.copy()
        q2f = q2_store.copy()
        q2w = q2_weekly.copy()
        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            q2k = q2k[q2k["store_num"] == sk_num]
            q2f = q2f[q2f["store_num"] == sk_num]
            q2w = q2w[q2w["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            q2k = q2k[q2k["store_num"].isin(d_nums)]
            q2f = q2f[q2f["store_num"].isin(d_nums)]
            q2w = q2w[q2w["store_num"].isin(d_nums)]

        weeks_covered = sorted(q2w["week_d"].unique()) if not q2w.empty else []
        st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Q2 2026 (Periods 4-6) &nbsp;|&nbsp; {len(weeks_covered)} weeks forecast &nbsp;|&nbsp; {len(q2k)} stores KDS &nbsp;|&nbsp; {len(q2f)} stores forecast</p>', unsafe_allow_html=True)

        # ── KDS KPI Cards ──
        k1, k2, k3, k4, k5 = st.columns(5)
        if not q2k.empty:
            avg_sos = q2k["sos_min"].mean() if q2k["sos_min"].notna().any() else 0
            avg_pb = q2k["pre_bump"].mean() if q2k["pre_bump"].notna().any() else 0
            avg_adopt = q2k["bone_in_adopt"].mean() if q2k["bone_in_adopt"].notna().any() else 0
            avg_qv = q2k["bone_in_qty_var"].mean() if q2k["bone_in_qty_var"].notna().any() else 0
            avg_ma = q2k["make_ahead_rate"].mean() if q2k["make_ahead_rate"].notna().any() else 0
        else:
            avg_sos = avg_pb = avg_adopt = avg_qv = avg_ma = 0

        sos_c = "green" if avg_sos < 10 else ("orange" if avg_sos < 13 else "red")
        pb_c = "green" if avg_pb < 1 else ("orange" if avg_pb < 3 else "red")
        adopt_c = "green" if avg_adopt >= 97 else ("orange" if avg_adopt >= 90 else "red")
        qv_c = "green" if abs(avg_qv) < 3 else ("orange" if abs(avg_qv) < 6 else "red")
        ma_c = "green" if avg_ma >= 80 else ("orange" if avg_ma >= 50 else "red")

        k1.markdown(kpi_card("Avg SOS", f"{avg_sos:.1f} min", sos_c), unsafe_allow_html=True)
        k2.markdown(kpi_card("Pre-Bump Rate", f"{avg_pb:.2f}%", pb_c), unsafe_allow_html=True)
        k3.markdown(kpi_card("Bone-In Adoption", f"{avg_adopt:.1f}%", adopt_c), unsafe_allow_html=True)
        k4.markdown(kpi_card("Bone-In Qty Var", f"{avg_qv:+.2f}%", qv_c), unsafe_allow_html=True)
        k5.markdown(kpi_card("Make Ahead Rate", f"{avg_ma:.1f}%", ma_c), unsafe_allow_html=True)

        # ── Labor KPI Cards ──
        if not q2f.empty:
            st.markdown("")
            l1, l2, l3, l4 = st.columns(4)
            total_actual = q2f["actual_sales"].sum()
            total_forecast = q2f["forecast_sales"].sum()
            total_var = (total_actual - total_forecast) / total_forecast if total_forecast else 0
            avg_labor_var = q2f["labor_pct_variance"].mean() if q2f["labor_pct_variance"].notna().any() else 0
            avg_actual_labor = q2f["actual_labor_pct"].mean() if q2f["actual_labor_pct"].notna().any() else 0
            total_ovt = q2f["ovt_hours"].sum()

            sales_c = "green" if total_var >= 0 else "red"
            labor_c = "green" if avg_labor_var <= 0 else ("orange" if avg_labor_var < 0.02 else "red")

            l1.markdown(kpi_card("Q2 Actual Sales", f"${total_actual:,.0f}", sales_c), unsafe_allow_html=True)
            l2.markdown(kpi_card("Sales vs Forecast", f"{total_var:+.1%}", sales_c), unsafe_allow_html=True)
            l3.markdown(kpi_card("Avg Labor %", f"{avg_actual_labor:.1%}"), unsafe_allow_html=True)
            l4.markdown(kpi_card("Avg Labor Variance", f"{avg_labor_var:+.2%}", labor_c), unsafe_allow_html=True)

        st.markdown("")

        # ── SOS by Store ──
        if not q2k.empty:
            st.markdown('<div class="section-title">Q2 Speed of Service by Store</div>', unsafe_allow_html=True)
            sos_q2 = q2k[q2k["sos_min"].notna()].sort_values("sos_min")
            sos_colors = [RED if v > 12 else (ORANGE if v > 10 else TEAL) for v in sos_q2["sos_min"]]
            fig_sos_q2 = go.Figure(go.Bar(
                x=sos_q2["short_name"], y=sos_q2["sos_min"],
                marker_color=sos_colors,
                hovertemplate="%{x}<br>SOS: %{y:.1f} min<extra></extra>",
            ))
            fig_sos_q2.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1.5,
                                 annotation_text="10 min target", annotation_font=dict(color="#DC2626", size=10))
            fig_sos_q2.update_layout(**CHART_LAYOUT, height=380,
                                     yaxis_title="Minutes", xaxis_tickangle=-45)
            st.plotly_chart(fig_sos_q2, use_container_width=True, key="q2_sos", config=CHART_CONFIG)

            # ── Pre-Bump & Bone-In Adoption ──
            pb_l, pb_r = st.columns(2)
            with pb_l:
                st.markdown('<div class="section-title">Q2 Pre-Bump Rate</div>', unsafe_allow_html=True)
                pb_q2 = q2k[q2k["pre_bump"].notna()].sort_values("pre_bump", ascending=False)
                pb_colors = [RED if v > 3 else (ORANGE if v > 1 else TEAL) for v in pb_q2["pre_bump"]]
                fig_pb_q2 = go.Figure(go.Bar(
                    x=pb_q2["short_name"], y=pb_q2["pre_bump"],
                    marker_color=pb_colors,
                    hovertemplate="%{x}<br>Pre-Bump: %{y:.2f}%<extra></extra>",
                ))
                fig_pb_q2.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Pre-Bump %", xaxis_tickangle=-45)
                st.plotly_chart(fig_pb_q2, use_container_width=True, key="q2_pb", config=CHART_CONFIG)

            with pb_r:
                st.markdown('<div class="section-title">Q2 Bone-In Adoption</div>', unsafe_allow_html=True)
                ad_q2 = q2k[q2k["bone_in_adopt"].notna()].sort_values("bone_in_adopt")
                ad_colors = [RED if v < 90 else (ORANGE if v < 97 else "#059669") for v in ad_q2["bone_in_adopt"]]
                fig_ad_q2 = go.Figure(go.Bar(
                    x=ad_q2["short_name"], y=ad_q2["bone_in_adopt"],
                    marker_color=ad_colors,
                    hovertemplate="%{x}<br>Adoption: %{y:.1f}%<extra></extra>",
                ))
                fig_ad_q2.add_hline(y=100, line_dash="dash", line_color=GREEN, line_width=1.5,
                                    annotation_text="100%", annotation_font=dict(color="#059669", size=10))
                fig_ad_q2.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Adoption %", xaxis_tickangle=-45)
                st.plotly_chart(fig_ad_q2, use_container_width=True, key="q2_adopt", config=CHART_CONFIG)

            # ── Qty Variance & Make Ahead ──
            qv_l, qv_r = st.columns(2)
            with qv_l:
                st.markdown('<div class="section-title">Q2 Bone-In Qty Variance</div>', unsafe_allow_html=True)
                qv_q2 = q2k[q2k["bone_in_qty_var"].notna()].sort_values("bone_in_qty_var")
                qv_colors = [RED if abs(v) > 6 else (ORANGE if abs(v) > 3 else "#059669") for v in qv_q2["bone_in_qty_var"]]
                fig_qv_q2 = go.Figure(go.Bar(
                    x=qv_q2["short_name"], y=qv_q2["bone_in_qty_var"],
                    marker_color=qv_colors,
                    hovertemplate="%{x}<br>Qty Var: %{y:+.2f}%<extra></extra>",
                ))
                fig_qv_q2.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_qv_q2.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Qty Variance %", xaxis_tickangle=-45)
                st.plotly_chart(fig_qv_q2, use_container_width=True, key="q2_qv", config=CHART_CONFIG)

            with qv_r:
                st.markdown('<div class="section-title">Q2 Make Ahead Rate</div>', unsafe_allow_html=True)
                ma_q2 = q2k[q2k["make_ahead_rate"].notna()].sort_values("make_ahead_rate")
                ma_colors = [RED if v < 50 else (ORANGE if v < 80 else "#059669") for v in ma_q2["make_ahead_rate"]]
                fig_ma_q2 = go.Figure(go.Bar(
                    x=ma_q2["short_name"], y=ma_q2["make_ahead_rate"],
                    marker_color=ma_colors,
                    hovertemplate="%{x}<br>Make Ahead: %{y:.1f}%<extra></extra>",
                ))
                fig_ma_q2.update_layout(**CHART_LAYOUT, height=370,
                                        yaxis_title="Make Ahead %", xaxis_tickangle=-45)
                st.plotly_chart(fig_ma_q2, use_container_width=True, key="q2_ma", config=CHART_CONFIG)

        # ── Labor Variance by Store ──
        if not q2f.empty:
            st.markdown('<div class="section-title">Q2 Labor Variance % by Store</div>', unsafe_allow_html=True)
            lv_df = q2f[q2f["labor_pct_variance"].notna()].sort_values("labor_pct_variance")
            lv_colors = [RED if v > 0 else ("#059669" if v < -0.02 else TEAL) for v in lv_df["labor_pct_variance"]]
            fig_lv = go.Figure(go.Bar(
                x=lv_df["short_name"],
                y=lv_df["labor_pct_variance"] * 100,
                marker_color=lv_colors,
                hovertemplate="%{x}<br>Labor Var: %{y:+.2f}%<extra></extra>",
            ))
            fig_lv.add_hline(y=0, line_color="#BDBDBD", line_width=1)
            fig_lv.update_layout(**CHART_LAYOUT, height=400,
                                 yaxis_title="Labor Variance %", xaxis_tickangle=-45)
            st.plotly_chart(fig_lv, use_container_width=True, key="q2_lv", config=CHART_CONFIG)

            # ── Sales Variance & Actual Labor % ──
            sv_l, sv_r = st.columns(2)
            with sv_l:
                st.markdown('<div class="section-title">Q2 Sales vs Forecast Variance</div>', unsafe_allow_html=True)
                sv_df = q2f.sort_values("sales_var_pct")
                sv_colors = [RED if v < -0.05 else (ORANGE if v < 0 else "#059669") for v in sv_df["sales_var_pct"]]
                fig_sv = go.Figure(go.Bar(
                    x=sv_df["short_name"],
                    y=sv_df["sales_var_pct"] * 100,
                    marker_color=sv_colors,
                    hovertemplate="%{x}<br>Sales Var: %{y:+.1f}%<extra></extra>",
                ))
                fig_sv.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_sv.update_layout(**CHART_LAYOUT, height=370,
                                     yaxis_title="Sales Variance %", xaxis_tickangle=-45)
                st.plotly_chart(fig_sv, use_container_width=True, key="q2_sv", config=CHART_CONFIG)

            with sv_r:
                st.markdown('<div class="section-title">Q2 Actual Labor % by Store</div>', unsafe_allow_html=True)
                al_df = q2f.sort_values("actual_labor_pct", ascending=False)
                al_colors = [RED if v > 0.20 else (ORANGE if v > 0.16 else TEAL) for v in al_df["actual_labor_pct"]]
                fig_al = go.Figure(go.Bar(
                    x=al_df["short_name"],
                    y=al_df["actual_labor_pct"] * 100,
                    marker_color=al_colors,
                    hovertemplate="%{x}<br>Labor: %{y:.1f}%<extra></extra>",
                ))
                fig_al.update_layout(**CHART_LAYOUT, height=370,
                                     yaxis_title="Labor %", xaxis_tickangle=-45)
                st.plotly_chart(fig_al, use_container_width=True, key="q2_al", config=CHART_CONFIG)

            # ── Weekly Labor Trend ──
            if not q2w.empty:
                st.markdown('<div class="section-title">Q2 Weekly Labor Variance Trend</div>', unsafe_allow_html=True)
                weekly_agg = q2w.groupby("week_d").agg(
                    actual_labor=("actual_labor", "sum"),
                    actual_sales=("actual_sales", "sum"),
                    schedule_labor=("schedule_labor", "sum"),
                    forecast_sales=("forecast_sales", "sum"),
                ).reset_index()
                weekly_agg["actual_labor_pct"] = weekly_agg["actual_labor"] / weekly_agg["actual_sales"]
                weekly_agg["schedule_labor_pct"] = weekly_agg["schedule_labor"] / weekly_agg["forecast_sales"]

                fig_wk = go.Figure()
                fig_wk.add_trace(go.Scatter(
                    x=weekly_agg["week_d"], y=weekly_agg["actual_labor_pct"] * 100,
                    name="Actual Labor %", mode="lines+markers",
                    line=dict(color=ORANGE, width=2), marker=dict(size=8),
                ))
                fig_wk.add_trace(go.Scatter(
                    x=weekly_agg["week_d"], y=weekly_agg["schedule_labor_pct"] * 100,
                    name="Scheduled Labor %", mode="lines+markers",
                    line=dict(color=TEAL, width=2, dash="dash"), marker=dict(size=8),
                ))
                fig_wk.update_layout(
                    **CHART_LAYOUT, height=350,
                    yaxis_title="Labor %",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(color="#374151")),
                )
                st.plotly_chart(fig_wk, use_container_width=True, key="q2_wk", config=CHART_CONFIG)

            # ── Q2 Detail Table (Labor) ──
            st.markdown('<div class="section-title">Q2 Store Details (Labor)</div>', unsafe_allow_html=True)
            tbl = q2f[["store", "config_district", "actual_sales", "forecast_sales",
                        "sales_var_pct", "actual_labor_pct", "schedule_labor_pct",
                        "labor_pct_variance", "ovt_hours", "weeks"]].copy()
            tbl.columns = ["Store", "District", "Actual Sales", "Forecast Sales",
                            "Sales Var %", "Actual Labor %", "Sched Labor %",
                            "Labor Variance %", "OT Hours", "Weeks"]
            tbl["Actual Sales"] = tbl["Actual Sales"].apply(lambda x: f"${x:,.0f}")
            tbl["Forecast Sales"] = tbl["Forecast Sales"].apply(lambda x: f"${x:,.0f}")
            tbl["Sales Var %"] = tbl["Sales Var %"].apply(lambda x: f"{x:+.1%}")
            tbl["Actual Labor %"] = tbl["Actual Labor %"].apply(lambda x: f"{x:.1%}")
            tbl["Sched Labor %"] = tbl["Sched Labor %"].apply(lambda x: f"{x:.1%}")
            tbl["Labor Variance %"] = tbl["Labor Variance %"].apply(lambda x: f"{x:+.2%}")
            tbl["OT Hours"] = tbl["OT Hours"].apply(lambda x: f"{x:.1f}")
            tbl = tbl.sort_values("Store")
            st.dataframe(tbl, use_container_width=True, hide_index=True)

        # ── Q2 KDS Detail Table ──
        if not q2k.empty:
            st.markdown('<div class="section-title">Q2 KDS Store Details</div>', unsafe_allow_html=True)
            detail = q2k[["short_name", "district", "sos_min", "pre_bump", "bone_in_adopt",
                           "bone_in_qty_var", "make_ahead_rate", "bone_in_accuracy",
                           "waste", "pct_7_10", "quadrant"]].copy()
            detail.columns = ["Store", "District", "SOS (min)", "Pre-Bump %", "BI Adoption %",
                              "BI Qty Var %", "Make Ahead %", "BI Accuracy %",
                              "Waste %", "% 7-10 min", "Quadrant"]
            detail = detail.sort_values("SOS (min)")
            st.dataframe(detail, use_container_width=True, hide_index=True)

# ════════════════════════════════
# SALES PERFORMANCE
# ════════════════════════════════
elif selected_tab == "Sales Performance":
    import numpy as np
    np.random.seed(42)

    all_stores = []
    for dist, stores in DISTRICTS.items():
        for s in stores:
            snum = s.split(" - ")[0].strip().lstrip("0")
            sname = s.split("-", 2)[2].strip()[:22] if len(s.split("-", 2)) >= 3 else s[:22]
            all_stores.append({"store": s, "store_num": snum, "short_name": sname, "district": dist})
    sales_df = pd.DataFrame(all_stores)

    sales_df["net_sales"] = np.random.uniform(28000, 65000, len(sales_df)).round(0)
    sales_df["transactions"] = np.random.randint(400, 1100, len(sales_df))
    sales_df["avg_ticket"] = (sales_df["net_sales"] / sales_df["transactions"]).round(2)
    sales_df["sales_ly"] = (sales_df["net_sales"] * np.random.uniform(0.88, 1.05, len(sales_df))).round(0)
    sales_df["sss_growth"] = ((sales_df["net_sales"] - sales_df["sales_ly"]) / sales_df["sales_ly"] * 100).round(1)
    sales_df["digital_pct"] = np.random.uniform(35, 72, len(sales_df)).round(1)

    if selected_store != "All Stores":
        sk_num = extract_store_number(selected_store)
        sales_df = sales_df[sales_df["store_num"] == sk_num]
    elif selected_district != "All Districts":
        d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
        sales_df = sales_df[sales_df["store_num"].isin(d_nums)]

    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Weekly Sales Performance &nbsp;|&nbsp; {len(sales_df)} stores &nbsp;|&nbsp; <span style="color:#D97706; font-weight:600;">Sample Data</span></p>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    total_sales = sales_df["net_sales"].sum()
    avg_sss = sales_df["sss_growth"].mean()
    avg_ticket = sales_df["avg_ticket"].mean()
    total_txn = sales_df["transactions"].sum()
    avg_digital = sales_df["digital_pct"].mean()

    sss_c = "green" if avg_sss >= 0 else "red"
    k1.markdown(kpi_card("Total Net Sales", f"${total_sales:,.0f}"), unsafe_allow_html=True)
    k2.markdown(kpi_card("SSS Growth", f"{avg_sss:+.1f}%", sss_c), unsafe_allow_html=True)
    k3.markdown(kpi_card("Avg Ticket", f"${avg_ticket:.2f}"), unsafe_allow_html=True)
    k4.markdown(kpi_card("Transactions", f"{total_txn:,}"), unsafe_allow_html=True)
    k5.markdown(kpi_card("Digital Mix", f"{avg_digital:.1f}%"), unsafe_allow_html=True)

    st.markdown("")

    st.markdown('<div class="section-title">Net Sales by Store</div>', unsafe_allow_html=True)
    s_sorted = sales_df.sort_values("net_sales", ascending=False)
    fig_ns = go.Figure(go.Bar(
        x=s_sorted["short_name"], y=s_sorted["net_sales"],
        marker_color=TEAL,
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    ))
    fig_ns.update_layout(**CHART_LAYOUT, height=380, yaxis_title="Net Sales ($)", xaxis_tickangle=-45)
    st.plotly_chart(fig_ns, use_container_width=True, key="sales_ns", config=CHART_CONFIG)

    sl, sr = st.columns(2)
    with sl:
        st.markdown('<div class="section-title">Same-Store Sales Growth %</div>', unsafe_allow_html=True)
        sss_sorted = sales_df.sort_values("sss_growth")
        sss_colors = [RED if v < -3 else (ORANGE if v < 0 else GREEN) for v in sss_sorted["sss_growth"]]
        fig_sss = go.Figure(go.Bar(
            x=sss_sorted["short_name"], y=sss_sorted["sss_growth"],
            marker_color=sss_colors,
            hovertemplate="%{x}<br>SSS: %{y:+.1f}%<extra></extra>",
        ))
        fig_sss.add_hline(y=0, line_color="#BDBDBD", line_width=1)
        fig_sss.update_layout(**CHART_LAYOUT, height=370, yaxis_title="SSS Growth %", xaxis_tickangle=-45)
        st.plotly_chart(fig_sss, use_container_width=True, key="sales_sss", config=CHART_CONFIG)

    with sr:
        st.markdown('<div class="section-title">Average Ticket by Store</div>', unsafe_allow_html=True)
        tk_sorted = sales_df.sort_values("avg_ticket", ascending=False)
        fig_tk = go.Figure(go.Bar(
            x=tk_sorted["short_name"], y=tk_sorted["avg_ticket"],
            marker_color=GOLD,
            hovertemplate="%{x}<br>Avg Ticket: $%{y:.2f}<extra></extra>",
        ))
        fig_tk.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Avg Ticket ($)", xaxis_tickangle=-45)
        st.plotly_chart(fig_tk, use_container_width=True, key="sales_tk", config=CHART_CONFIG)

    st.markdown('<div class="section-title">Sales Detail Table</div>', unsafe_allow_html=True)
    stbl = sales_df[["short_name", "district", "net_sales", "transactions", "avg_ticket", "sss_growth", "digital_pct"]].copy()
    stbl.columns = ["Store", "District", "Net Sales", "Transactions", "Avg Ticket", "SSS Growth %", "Digital %"]
    stbl["Net Sales"] = stbl["Net Sales"].apply(lambda x: f"${x:,.0f}")
    stbl["Avg Ticket"] = stbl["Avg Ticket"].apply(lambda x: f"${x:.2f}")
    stbl["SSS Growth %"] = stbl["SSS Growth %"].apply(lambda x: f"{x:+.1f}%")
    stbl["Digital %"] = stbl["Digital %"].apply(lambda x: f"{x:.1f}%")
    stbl = stbl.sort_values("Store")
    st.dataframe(stbl, use_container_width=True, hide_index=True)

# ════════════════════════════════
# LABOR DASHBOARD
# ════════════════════════════════
elif selected_tab == "Labor Dashboard":
    forecast_path = DATA_DIR / "forecast.xlsm"
    if not forecast_path.exists():
        st.warning("No forecast data found. Place forecast.xlsm in the data/ folder.")
    else:
        @st.cache_data(ttl=300)
        def load_labor_data():
            raw = pd.read_excel(DATA_DIR / "forecast.xlsm", sheet_name="Forecast_Data")
            return raw[raw["year"] == 2026].copy()

        labor_raw = load_labor_data()
        if labor_raw.empty:
            st.warning("No 2026 labor data found in forecast file.")
        else:
            available_periods = sorted(labor_raw["period"].unique())
            period_labels = {p: f"Period {p}" for p in available_periods}

            fq1, fq2, fq3 = st.columns(3)
            with fq1:
                quarter_options = ["All Quarters", "Q1 (P1-P3)", "Q2 (P4-P6)"]
                selected_quarter = st.selectbox("Quarter", quarter_options, key="labor_quarter")
            q_periods = {"Q1 (P1-P3)": [1, 2, 3], "Q2 (P4-P6)": [4, 5, 6]}
            if selected_quarter in q_periods:
                qtr_filtered = labor_raw[labor_raw["period"].isin(q_periods[selected_quarter])]
                qtr_available = sorted(p for p in available_periods if p in q_periods[selected_quarter])
            else:
                qtr_filtered = labor_raw
                qtr_available = available_periods

            with fq2:
                period_options = ["All Periods"] + qtr_available
                selected_period = st.selectbox(
                    "Period", period_options,
                    format_func=lambda p: "All Periods" if p == "All Periods" else period_labels.get(p, str(p)),
                    index=len(period_options) - 1,
                    key="labor_period",
                )
            with fq3:
                if selected_period == "All Periods":
                    week_choices = sorted(qtr_filtered["week_d"].unique())
                else:
                    week_choices = sorted(qtr_filtered[qtr_filtered["period"] == selected_period]["week_d"].unique())
                week_options = ["All Weeks"] + list(week_choices)
                selected_labor_week = st.selectbox("Week", week_options, key="labor_week")

            if selected_quarter in q_periods:
                lf = labor_raw[labor_raw["period"].isin(q_periods[selected_quarter])].copy()
            else:
                lf = labor_raw.copy()
            if selected_period != "All Periods":
                lf = lf[lf["period"] == selected_period]
            if selected_labor_week != "All Weeks":
                lf = lf[lf["week_d"] == selected_labor_week]

            lf["store_num"] = lf["store"].apply(forecast_store_num)
            lf["short_name"] = lf["store"].apply(forecast_short_name)
            lf["config_district"] = lf["store_num"].map(STORE_TO_DISTRICT)

            if selected_store != "All Stores":
                sk_num = extract_store_number(selected_store)
                lf = lf[lf["store_num"] == sk_num]
            elif selected_district != "All Districts":
                d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
                lf = lf[lf["store_num"].isin(d_nums)]

            labor_df = lf.groupby(["store_num", "short_name", "config_district"]).agg(
                forecast_sales=("forecast_sales", "sum"),
                actual_sales=("actual_sales", "sum"),
                guide_hours=("guide_hours", "sum"),
                scheduled_hours=("schedule_hours", "sum"),
                actual_hours=("actual_crew_hours", "sum"),
                overtime_hours=("ovt_hours", "sum"),
                schedule_labor=("schedule_labor", "sum"),
                actual_labor_cost=("actual_labor", "sum"),
            ).reset_index()

            labor_df["actual_labor_pct"] = labor_df["actual_labor_cost"] / labor_df["actual_sales"]
            labor_df["schedule_labor_pct"] = labor_df["schedule_labor"] / labor_df["forecast_sales"]
            labor_df["labor_variance"] = labor_df["actual_labor_pct"] - labor_df["schedule_labor_pct"]
            labor_df["hours_variance"] = labor_df["actual_hours"] - labor_df["guide_hours"]

            period_display = f"Period {selected_period}" if selected_period != "All Periods" else "All Periods"
            week_display = selected_labor_week if selected_labor_week != "All Weeks" else ""
            time_display = f"{period_display} {week_display}".strip()

            st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Labor Dashboard &nbsp;|&nbsp; {time_display} &nbsp;|&nbsp; {len(labor_df)} stores</p>', unsafe_allow_html=True)

            k1, k2, k3, k4, k5 = st.columns(5)
            avg_labor = labor_df["actual_labor_pct"].mean()
            avg_var = labor_df["labor_variance"].mean()
            total_ot = labor_df["overtime_hours"].sum()
            total_hours = labor_df["actual_hours"].sum()
            total_cost = labor_df["actual_labor_cost"].sum()

            labor_c = "green" if avg_labor <= 0.18 else ("orange" if avg_labor <= 0.20 else "red")
            var_c = "green" if avg_var <= 0 else ("orange" if avg_var < 0.02 else "red")
            ot_c = "green" if total_ot < 200 else ("orange" if total_ot < 400 else "red")

            k1.markdown(kpi_card("Avg Labor %", f"{avg_labor:.1%}", labor_c), unsafe_allow_html=True)
            k2.markdown(kpi_card("Labor Variance", f"{avg_var:+.2%}", var_c), unsafe_allow_html=True)
            k3.markdown(kpi_card("Total OT Hours", f"{total_ot:,.0f}", ot_c), unsafe_allow_html=True)
            k4.markdown(kpi_card("Total Crew Hours", f"{total_hours:,.0f}"), unsafe_allow_html=True)
            k5.markdown(kpi_card("Total Labor Cost", f"${total_cost:,.0f}"), unsafe_allow_html=True)

            st.markdown("")

            st.markdown('<div class="section-title">Labor % by Store (vs Schedule)</div>', unsafe_allow_html=True)
            lb_sorted = labor_df.sort_values("actual_labor_pct", ascending=False)
            lb_colors = [RED if v > 0.20 else (ORANGE if v > 0.18 else GREEN) for v in lb_sorted["actual_labor_pct"]]
            fig_lb = go.Figure(go.Bar(
                x=lb_sorted["short_name"], y=lb_sorted["actual_labor_pct"] * 100,
                marker_color=lb_colors,
                hovertemplate="%{x}<br>Labor: %{y:.1f}%<extra></extra>",
            ))
            fig_lb.add_hline(y=18, line_dash="dash", line_color=RED, line_width=1.5,
                             annotation_text="18% target", annotation_font=dict(color="#DC2626", size=10))
            fig_lb.update_layout(**CHART_LAYOUT, height=380, yaxis_title="Labor %", xaxis_tickangle=-45)
            st.plotly_chart(fig_lb, use_container_width=True, key="labor_pct", config=CHART_CONFIG)

            ll, lr = st.columns(2)
            with ll:
                st.markdown('<div class="section-title">Labor Variance % by Store</div>', unsafe_allow_html=True)
                lv_sorted = labor_df.sort_values("labor_variance", ascending=False)
                lv_colors = [RED if v > 0.02 else (ORANGE if v > 0 else GREEN) for v in lv_sorted["labor_variance"]]
                fig_lv = go.Figure(go.Bar(
                    x=lv_sorted["short_name"], y=lv_sorted["labor_variance"] * 100,
                    marker_color=lv_colors,
                    hovertemplate="%{x}<br>Variance: %{y:+.2f}%<extra></extra>",
                ))
                fig_lv.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_lv.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Labor Variance %", xaxis_tickangle=-45)
                st.plotly_chart(fig_lv, use_container_width=True, key="labor_var_chart", config=CHART_CONFIG)

            with lr:
                st.markdown('<div class="section-title">Overtime Hours by Store</div>', unsafe_allow_html=True)
                ot_sorted = labor_df.sort_values("overtime_hours", ascending=True)
                ot_colors = [RED if v > 25 else (ORANGE if v > 10 else GREEN) for v in ot_sorted["overtime_hours"]]
                fig_ot = go.Figure(go.Bar(
                    y=ot_sorted["short_name"], x=ot_sorted["overtime_hours"],
                    orientation="h", marker_color=ot_colors,
                    text=ot_sorted["overtime_hours"].apply(lambda x: f"{x:.1f}"),
                    textposition="outside", textfont=dict(size=10, color="#374151"),
                    hovertemplate="%{y}<br>OT: %{x:.1f} hrs<extra></extra>",
                ))
                ot_layout = {**CHART_LAYOUT, "margin": dict(l=100, r=40, t=10, b=30),
                             "yaxis": dict(gridcolor=GRID_COLOR, fixedrange=True, tickfont=dict(size=10))}
                fig_ot.update_layout(**ot_layout, height=max(370, len(ot_sorted) * 22), xaxis_title="OT Hours")
                st.plotly_chart(fig_ot, use_container_width=True, key="labor_ot", config=CHART_CONFIG)

            # Weekly labor trend
            if selected_period != "All Periods":
                wk_trend = lf.groupby("week_d").agg(
                    actual_labor=("actual_labor", "sum"),
                    actual_sales=("actual_sales", "sum"),
                    schedule_labor=("schedule_labor", "sum"),
                    forecast_sales=("forecast_sales", "sum"),
                ).reset_index()
                wk_trend["actual_pct"] = wk_trend["actual_labor"] / wk_trend["actual_sales"] * 100
                wk_trend["sched_pct"] = wk_trend["schedule_labor"] / wk_trend["forecast_sales"] * 100

                if len(wk_trend) > 1:
                    st.markdown('<div class="section-title">Weekly Labor % Trend</div>', unsafe_allow_html=True)
                    fig_wt = go.Figure()
                    fig_wt.add_trace(go.Scatter(
                        x=wk_trend["week_d"], y=wk_trend["actual_pct"],
                        name="Actual Labor %", mode="lines+markers",
                        line=dict(color=ORANGE, width=2), marker=dict(size=8),
                    ))
                    fig_wt.add_trace(go.Scatter(
                        x=wk_trend["week_d"], y=wk_trend["sched_pct"],
                        name="Scheduled Labor %", mode="lines+markers",
                        line=dict(color=TEAL, width=2, dash="dash"), marker=dict(size=8),
                    ))
                    fig_wt.update_layout(
                        **CHART_LAYOUT, height=350, yaxis_title="Labor %",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                    font=dict(color="#374151")),
                    )
                    st.plotly_chart(fig_wt, use_container_width=True, key="labor_trend", config=CHART_CONFIG)

            st.markdown('<div class="section-title">Labor Detail Table</div>', unsafe_allow_html=True)
            ltbl = labor_df[["short_name", "config_district", "actual_sales", "actual_labor_pct", "schedule_labor_pct",
                             "labor_variance", "guide_hours", "scheduled_hours", "actual_hours", "overtime_hours", "actual_labor_cost"]].copy()
            ltbl.columns = ["Store", "District", "Actual Sales", "Labor %", "Sched Labor %",
                            "Variance", "Guide Hrs", "Sched Hrs", "Actual Hrs", "OT Hrs", "Labor Cost"]
            ltbl["Actual Sales"] = ltbl["Actual Sales"].apply(lambda x: f"${x:,.0f}")
            ltbl["Labor %"] = ltbl["Labor %"].apply(lambda x: f"{x:.1%}")
            ltbl["Sched Labor %"] = ltbl["Sched Labor %"].apply(lambda x: f"{x:.1%}")
            ltbl["Variance"] = ltbl["Variance"].apply(lambda x: f"{x:+.2%}")
            ltbl["Labor Cost"] = ltbl["Labor Cost"].apply(lambda x: f"${x:,.0f}")
            ltbl["OT Hrs"] = ltbl["OT Hrs"].apply(lambda x: f"{x:.1f}")
            ltbl = ltbl.sort_values("Store")
            st.dataframe(ltbl, use_container_width=True, hide_index=True)

# ════════════════════════════════
# SMG (GUEST SATISFACTION)
# ════════════════════════════════
elif selected_tab == "SMG (Guest Satisfaction)":
    @st.cache_data(ttl=300)
    def load_smg_file(filename):
        path = DATA_DIR / filename
        if not path.exists():
            return pd.DataFrame()
        raw = pd.read_excel(path, header=None, skiprows=2)
        raw.columns = ["Store", "Measure", "Current", "LastYear", "Difference", "Count", "Count_Current", "Count_LastYear"]
        raw = raw[(raw["Measure"] != "Measure") & (raw["Store"] != "Combined")].copy()
        raw["Current"] = pd.to_numeric(raw["Current"], errors="coerce")
        raw["LastYear"] = pd.to_numeric(raw["LastYear"], errors="coerce")
        raw["Difference"] = pd.to_numeric(raw["Difference"], errors="coerce")
        raw["Count"] = pd.to_numeric(raw["Count"], errors="coerce")
        store_pat = raw["Store"].str.extract(r"^(\d+)\s*-\s*(.*)")
        raw["store_num"] = store_pat[0].str.lstrip("0")
        raw["store_name"] = store_pat[1].str.strip()
        raw["short_name"] = raw["store_name"].str.replace(r"^FL-", "", regex=True).str.strip().str[:22]
        return raw

    smg_q1_exists = (DATA_DIR / "smg_q1.xlsx").exists()
    smg_q2_exists = (DATA_DIR / "smg_q2.xlsx").exists()
    smg_quarter_options = []
    if smg_q1_exists:
        smg_quarter_options.append("Q1")
    if smg_q2_exists:
        smg_quarter_options.append("Q2")

    if not smg_quarter_options:
        st.warning("No SMG data found. Place smg_q1.xlsx or smg_q2.xlsx in the data/ folder.")
    else:
        smg_sel_quarter = st.selectbox("Quarter", smg_quarter_options, key="smg_quarter")
        smg_file = "smg_q1.xlsx" if smg_sel_quarter == "Q1" else "smg_q2.xlsx"
        smg_raw = load_smg_file(smg_file)

    if not smg_quarter_options or smg_raw.empty:
        if smg_quarter_options:
            st.warning(f"No data in {smg_file}.")
    else:
        dissat = smg_raw[smg_raw["Measure"] == "Dissatisfaction"].copy()
        qsc = smg_raw[smg_raw["Measure"] == "QSC Score"].copy()
        accuracy = smg_raw[smg_raw["Measure"] == "What Went Wrong - Accurate"].copy()

        smg_df = dissat[["store_num", "short_name", "Count"]].copy()
        smg_df = smg_df.rename(columns={"Count": "responses"})
        smg_df["satisfaction"] = (1 - dissat["Current"].values) * 100
        smg_df["dissat_pct"] = dissat["Current"].values * 100
        smg_df["dissat_ly"] = dissat["LastYear"].values * 100
        smg_df["dissat_diff"] = dissat["Difference"].values * 100
        qsc_map = dict(zip(qsc["store_num"], qsc["Current"]))
        smg_df["qsc_score"] = smg_df["store_num"].map(qsc_map)
        acc_map = dict(zip(accuracy["store_num"], accuracy["Current"]))
        smg_df["inaccuracy_pct"] = smg_df["store_num"].map(acc_map).apply(lambda x: x * 100 if pd.notna(x) else None)
        smg_df["accuracy_pct"] = 100 - smg_df["inaccuracy_pct"]

        smg_df["config_district"] = smg_df["store_num"].map(STORE_TO_DISTRICT)

        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            smg_df = smg_df[smg_df["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            smg_df = smg_df[smg_df["store_num"].isin(d_nums)]

        qtr_label = "Q1 (12/28/2025 - 3/28/2026)" if smg_sel_quarter == "Q1" else "Q2 (3/29/2026 - 6/27/2026)"
        st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Guest Satisfaction (SMG) &nbsp;|&nbsp; {qtr_label} &nbsp;|&nbsp; {len(smg_df)} stores &nbsp;|&nbsp; <span style="color:#059669; font-weight:600;">Real Data</span></p>', unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        avg_sat = smg_df["satisfaction"].mean()
        avg_dissat = smg_df["dissat_pct"].mean()
        avg_qsc = smg_df["qsc_score"].mean() if smg_df["qsc_score"].notna().any() else 0
        avg_acc = smg_df["accuracy_pct"].mean() if smg_df["accuracy_pct"].notna().any() else 0
        total_responses = smg_df["responses"].sum()

        sat_c = "green" if avg_sat >= 95 else ("orange" if avg_sat >= 90 else "red")
        dissat_c = "green" if avg_dissat <= 5 else ("orange" if avg_dissat <= 8 else "red")
        qsc_c = "green" if avg_qsc >= 4.5 else ("orange" if avg_qsc >= 4 else "red")
        acc_c = "green" if avg_acc >= 97 else ("orange" if avg_acc >= 95 else "red")

        k1.markdown(kpi_card("Satisfaction", f"{avg_sat:.1f}%", sat_c), unsafe_allow_html=True)
        k2.markdown(kpi_card("Dissatisfaction", f"{avg_dissat:.1f}%", dissat_c), unsafe_allow_html=True)
        k3.markdown(kpi_card("QSC Score", f"{avg_qsc:.2f}/5", qsc_c), unsafe_allow_html=True)
        k4.markdown(kpi_card("Order Accuracy", f"{avg_acc:.1f}%", acc_c), unsafe_allow_html=True)

        st.markdown("")

        st.markdown('<div class="section-title">Dissatisfaction % by Store (lower is better)</div>', unsafe_allow_html=True)
        dis_sorted = smg_df.sort_values("dissat_pct", ascending=False)
        dis_colors = [RED if v > 8 else (ORANGE if v > 5 else GREEN) for v in dis_sorted["dissat_pct"]]
        fig_dis = go.Figure(go.Bar(
            x=dis_sorted["short_name"], y=dis_sorted["dissat_pct"],
            marker_color=dis_colors,
            hovertemplate="%{x}<br>Dissat: %{y:.1f}%<extra></extra>",
        ))
        fig_dis.add_hline(y=5, line_dash="dash", line_color=RED, line_width=1.5,
                          annotation_text="5% target", annotation_font=dict(color="#DC2626", size=10))
        fig_dis.update_layout(**CHART_LAYOUT, height=380, yaxis_title="Dissatisfaction %", xaxis_tickangle=-45)
        st.plotly_chart(fig_dis, use_container_width=True, key="smg_dissat", config=CHART_CONFIG)

        sl, sr = st.columns(2)
        with sl:
            st.markdown('<div class="section-title">QSC Score by Store</div>', unsafe_allow_html=True)
            qsc_sorted = smg_df[smg_df["qsc_score"].notna()].sort_values("qsc_score")
            qsc_colors = [RED if v < 4 else (ORANGE if v < 4.5 else GREEN) for v in qsc_sorted["qsc_score"]]
            fig_qsc = go.Figure(go.Bar(
                x=qsc_sorted["short_name"], y=qsc_sorted["qsc_score"],
                marker_color=qsc_colors,
                hovertemplate="%{x}<br>QSC: %{y:.2f}<extra></extra>",
            ))
            fig_qsc.add_hline(y=4.5, line_dash="dash", line_color=GREEN, line_width=1.5,
                              annotation_text="4.5 target", annotation_font=dict(color="#059669", size=10))
            fig_qsc.update_layout(**CHART_LAYOUT, height=370, yaxis_title="QSC Score", xaxis_tickangle=-45)
            st.plotly_chart(fig_qsc, use_container_width=True, key="smg_qsc", config=CHART_CONFIG)

        with sr:
            st.markdown('<div class="section-title">Order Accuracy % by Store</div>', unsafe_allow_html=True)
            acc_sorted = smg_df[smg_df["accuracy_pct"].notna()].sort_values("accuracy_pct")
            acc_colors = [RED if v < 95 else (ORANGE if v < 97 else GREEN) for v in acc_sorted["accuracy_pct"]]
            fig_acc = go.Figure(go.Bar(
                x=acc_sorted["short_name"], y=acc_sorted["accuracy_pct"],
                marker_color=acc_colors,
                hovertemplate="%{x}<br>Accuracy: %{y:.1f}%<extra></extra>",
            ))
            fig_acc.add_hline(y=97, line_dash="dash", line_color=GREEN, line_width=1.5,
                              annotation_text="97% target", annotation_font=dict(color="#059669", size=10))
            fig_acc.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Accuracy %", xaxis_tickangle=-45)
            st.plotly_chart(fig_acc, use_container_width=True, key="smg_accuracy", config=CHART_CONFIG)

        st.markdown('<div class="section-title">Year-over-Year Dissatisfaction Change</div>', unsafe_allow_html=True)
        yoy_sorted = smg_df.sort_values("dissat_diff", ascending=False)
        yoy_colors = [RED if v > 0 else GREEN for v in yoy_sorted["dissat_diff"]]
        fig_yoy = go.Figure(go.Bar(
            x=yoy_sorted["short_name"], y=yoy_sorted["dissat_diff"],
            marker_color=yoy_colors,
            hovertemplate="%{x}<br>Change: %{y:+.2f}pp<extra></extra>",
        ))
        fig_yoy.add_hline(y=0, line_color="#BDBDBD", line_width=1)
        fig_yoy.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Dissat Change (pp)", xaxis_tickangle=-45)
        st.plotly_chart(fig_yoy, use_container_width=True, key="smg_yoy", config=CHART_CONFIG)

        st.markdown('<div class="section-title">SMG Detail Table</div>', unsafe_allow_html=True)
        smg_tbl = smg_df[["short_name", "config_district", "satisfaction", "dissat_pct", "dissat_ly", "dissat_diff", "qsc_score", "accuracy_pct", "responses"]].copy()
        smg_tbl.columns = ["Store", "District", "Satisfaction %", "Dissat %", "Dissat LY %", "Dissat Change", "QSC Score", "Accuracy %", "Responses"]
        smg_tbl["Satisfaction %"] = smg_tbl["Satisfaction %"].apply(lambda x: f"{x:.1f}%")
        smg_tbl["Dissat %"] = smg_tbl["Dissat %"].apply(lambda x: f"{x:.1f}%")
        smg_tbl["Dissat LY %"] = smg_tbl["Dissat LY %"].apply(lambda x: f"{x:.1f}%")
        smg_tbl["Dissat Change"] = smg_tbl["Dissat Change"].apply(lambda x: f"{x:+.2f}pp")
        smg_tbl["QSC Score"] = smg_tbl["QSC Score"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        smg_tbl["Accuracy %"] = smg_tbl["Accuracy %"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        smg_tbl["Responses"] = smg_tbl["Responses"].apply(lambda x: f"{x:,.0f}")
        smg_tbl = smg_tbl.sort_values("Store")
        st.dataframe(smg_tbl, use_container_width=True, hide_index=True)

# ════════════════════════════════
# DISTRICT COMPARISON
# ════════════════════════════════
elif selected_tab == "District Comparison":
    import numpy as np

    all_stores = []
    for dist, stores in DISTRICTS.items():
        for s in stores:
            snum = s.split(" - ")[0].strip().lstrip("0")
            sname = s.split("-", 2)[2].strip()[:22] if len(s.split("-", 2)) >= 3 else s[:22]
            all_stores.append({"store": s, "store_num": snum, "short_name": sname, "district": dist})
    comp_df = pd.DataFrame(all_stores)

    # Real labor data from forecast
    forecast_path = DATA_DIR / "forecast.xlsm"
    has_labor = False
    if forecast_path.exists():
        @st.cache_data(ttl=300)
        def load_district_labor():
            raw = pd.read_excel(forecast_path, sheet_name="Forecast_Data")
            return raw[raw["year"] == 2026].copy()
        dc_labor_raw = load_district_labor()
        if not dc_labor_raw.empty:
            has_labor = True
            dc_available_periods = sorted(dc_labor_raw["period"].unique())
            dc_period_labels = {p: f"Period {p}" for p in dc_available_periods}

            dcq1, dcq2, dcq3 = st.columns(3)
            with dcq1:
                dc_quarter_options = ["All Quarters", "Q1 (P1-P3)", "Q2 (P4-P6)"]
                dc_selected_quarter = st.selectbox("Quarter", dc_quarter_options, key="dc_quarter")
            dc_q_periods = {"Q1 (P1-P3)": [1, 2, 3], "Q2 (P4-P6)": [4, 5, 6]}
            if dc_selected_quarter in dc_q_periods:
                dc_qtr_filtered = dc_labor_raw[dc_labor_raw["period"].isin(dc_q_periods[dc_selected_quarter])]
                dc_qtr_available = sorted(p for p in dc_available_periods if p in dc_q_periods[dc_selected_quarter])
            else:
                dc_qtr_filtered = dc_labor_raw
                dc_qtr_available = dc_available_periods

            with dcq2:
                dc_period_options = ["All Periods"] + dc_qtr_available
                dc_selected_period = st.selectbox(
                    "Period", dc_period_options,
                    format_func=lambda p: "All Periods" if p == "All Periods" else dc_period_labels.get(p, str(p)),
                    index=len(dc_period_options) - 1,
                    key="dc_period",
                )
            with dcq3:
                if dc_selected_period == "All Periods":
                    dc_week_choices = sorted(dc_qtr_filtered["week_d"].unique())
                else:
                    dc_week_choices = sorted(dc_qtr_filtered[dc_qtr_filtered["period"] == dc_selected_period]["week_d"].unique())
                dc_week_options = ["All Weeks"] + list(dc_week_choices)
                dc_selected_week = st.selectbox("Week", dc_week_options, key="dc_week")

            dc_labor = dc_labor_raw.copy()
            if dc_selected_quarter in dc_q_periods:
                dc_labor = dc_labor[dc_labor["period"].isin(dc_q_periods[dc_selected_quarter])]
            if dc_selected_period != "All Periods":
                dc_labor = dc_labor[dc_labor["period"] == dc_selected_period]
            if dc_selected_week != "All Weeks":
                dc_labor = dc_labor[dc_labor["week_d"] == dc_selected_week]

            dc_labor["store_num"] = dc_labor["store"].apply(forecast_store_num)
            labor_agg = dc_labor.groupby("store_num").agg(
                actual_sales=("actual_sales", "sum"),
                forecast_sales=("forecast_sales", "sum"),
                actual_labor=("actual_labor", "sum"),
                schedule_labor=("schedule_labor", "sum"),
                ovt_hours=("ovt_hours", "sum"),
            ).reset_index()
            labor_agg["labor_pct"] = labor_agg["actual_labor"] / labor_agg["actual_sales"]
            labor_agg["sched_labor_pct"] = labor_agg["schedule_labor"] / labor_agg["forecast_sales"]
            labor_agg["labor_variance"] = labor_agg["labor_pct"] - labor_agg["sched_labor_pct"]
            labor_map = dict(zip(labor_agg["store_num"].astype(str), labor_agg["labor_pct"]))
            lv_map = dict(zip(labor_agg["store_num"].astype(str), labor_agg["labor_variance"]))
            ot_map = dict(zip(labor_agg["store_num"].astype(str), labor_agg["ovt_hours"]))
            comp_df["labor_pct"] = comp_df["store_num"].map(labor_map)
            comp_df["labor_variance"] = comp_df["store_num"].map(lv_map)
            comp_df["overtime"] = comp_df["store_num"].map(ot_map).fillna(0)

    if not has_labor:
        comp_df["labor_pct"] = None
        comp_df["labor_variance"] = None
        comp_df["overtime"] = 0

    # Real KDS data
    if not daily_df_all.empty:
        latest_date = daily_df_all["data_date"].max()
        daily_latest = daily_df_all[daily_df_all["data_date"] == latest_date]
        sos_map = dict(zip(daily_latest["store_num"].astype(str), daily_latest["sos_min"]))
        comp_df["sos_min"] = comp_df["store_num"].map(sos_map)
    else:
        comp_df["sos_min"] = None

    # Sales & SMG still sample until real data provided
    np.random.seed(42)
    comp_df["net_sales"] = np.random.uniform(28000, 65000, len(comp_df)).round(0)
    comp_df["sss_growth"] = np.random.uniform(-5, 15, len(comp_df)).round(1)
    np.random.seed(77)
    comp_df["osat"] = np.random.uniform(55, 95, len(comp_df)).round(1)

    district_agg = comp_df.groupby("district").agg(
        stores=("store", "count"),
        total_sales=("net_sales", "sum"),
        avg_sales=("net_sales", "mean"),
        avg_sss=("sss_growth", "mean"),
        avg_labor=("labor_pct", "mean"),
        avg_labor_var=("labor_variance", "mean"),
        total_ot=("overtime", "sum"),
        avg_osat=("osat", "mean"),
        avg_sos=("sos_min", "mean"),
    ).reset_index()
    district_agg = district_agg.sort_values("district")

    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">District Comparison &nbsp;|&nbsp; {len(district_agg)} districts &nbsp;|&nbsp; <span style="color:#059669; font-weight:600;">Labor &amp; KDS: Real Data</span> &nbsp;|&nbsp; <span style="color:#D97706; font-weight:600;">Sales &amp; SMG: Sample</span></p>', unsafe_allow_html=True)

    dist_colors = [GREEN, TEAL, GOLD, ORANGE, "#7C3AED", "#0EA5E9"]

    st.markdown('<div class="section-title">Total Sales by District</div>', unsafe_allow_html=True)
    fig_ds = go.Figure(go.Bar(
        x=district_agg["district"], y=district_agg["total_sales"],
        marker_color=dist_colors[:len(district_agg)],
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    ))
    fig_ds.update_layout(**CHART_LAYOUT, height=350, yaxis_title="Total Sales ($)")
    st.plotly_chart(fig_ds, use_container_width=True, key="dist_sales", config=CHART_CONFIG)

    dl, dlv, dm, dr = st.columns(4)
    with dl:
        st.markdown('<div class="section-title">Avg Labor % by District</div>', unsafe_allow_html=True)
        lb_colors = [RED if v > 0.20 else (ORANGE if v > 0.18 else GREEN) for v in district_agg["avg_labor"]]
        fig_dl = go.Figure(go.Bar(
            x=district_agg["district"], y=district_agg["avg_labor"] * 100,
            marker_color=lb_colors,
            hovertemplate="%{x}<br>Labor: %{y:.1f}%<extra></extra>",
        ))
        fig_dl.add_hline(y=18, line_dash="dash", line_color=RED, line_width=1.5)
        fig_dl.update_layout(**CHART_LAYOUT, height=350, yaxis_title="Labor %")
        st.plotly_chart(fig_dl, use_container_width=True, key="dist_labor", config=CHART_CONFIG)

    with dlv:
        st.markdown('<div class="section-title">Labor Variance % by District</div>', unsafe_allow_html=True)
        lv_colors = [RED if v > 0.02 else (ORANGE if v > 0 else GREEN) for v in district_agg["avg_labor_var"]]
        fig_dlv = go.Figure(go.Bar(
            x=district_agg["district"], y=district_agg["avg_labor_var"] * 100,
            marker_color=lv_colors,
            hovertemplate="%{x}<br>Variance: %{y:+.2f}%<extra></extra>",
        ))
        fig_dlv.add_hline(y=0, line_color="#BDBDBD", line_width=1)
        fig_dlv.update_layout(**CHART_LAYOUT, height=350, yaxis_title="Labor Variance %")
        st.plotly_chart(fig_dlv, use_container_width=True, key="dist_labor_var", config=CHART_CONFIG)

    with dm:
        st.markdown('<div class="section-title">Avg OSAT by District</div>', unsafe_allow_html=True)
        osat_colors = [RED if v < 70 else (ORANGE if v < 80 else GREEN) for v in district_agg["avg_osat"]]
        fig_do = go.Figure(go.Bar(
            x=district_agg["district"], y=district_agg["avg_osat"],
            marker_color=osat_colors,
            hovertemplate="%{x}<br>OSAT: %{y:.1f}%<extra></extra>",
        ))
        fig_do.add_hline(y=80, line_dash="dash", line_color=GREEN, line_width=1.5)
        fig_do.update_layout(**CHART_LAYOUT, height=350, yaxis_title="OSAT %")
        st.plotly_chart(fig_do, use_container_width=True, key="dist_osat", config=CHART_CONFIG)

    with dr:
        st.markdown('<div class="section-title">Avg SOS by District</div>', unsafe_allow_html=True)
        sos_colors = [RED if v > 12 else (ORANGE if v > 10 else GREEN) for v in district_agg["avg_sos"]]
        fig_dsos = go.Figure(go.Bar(
            x=district_agg["district"], y=district_agg["avg_sos"],
            marker_color=sos_colors,
            hovertemplate="%{x}<br>SOS: %{y:.1f} min<extra></extra>",
        ))
        fig_dsos.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1.5)
        fig_dsos.update_layout(**CHART_LAYOUT, height=350, yaxis_title="SOS (min)")
        st.plotly_chart(fig_dsos, use_container_width=True, key="dist_sos", config=CHART_CONFIG)

    st.markdown('<div class="section-title">District Summary Table</div>', unsafe_allow_html=True)
    dtbl = district_agg.copy()
    dtbl.columns = ["District", "Stores", "Total Sales", "Avg Sales/Store", "Avg SSS %", "Avg Labor %", "Labor Variance %", "Total OT Hrs", "Avg OSAT %", "Avg SOS (min)"]
    dtbl["Total Sales"] = dtbl["Total Sales"].apply(lambda x: f"${x:,.0f}")
    dtbl["Avg Sales/Store"] = dtbl["Avg Sales/Store"].apply(lambda x: f"${x:,.0f}")
    dtbl["Avg SSS %"] = dtbl["Avg SSS %"].apply(lambda x: f"{x:+.1f}%")
    dtbl["Avg Labor %"] = dtbl["Avg Labor %"].apply(lambda x: f"{x:.1%}")
    dtbl["Labor Variance %"] = dtbl["Labor Variance %"].apply(lambda x: f"{x:+.2%}" if pd.notna(x) else "—")
    dtbl["Total OT Hrs"] = dtbl["Total OT Hrs"].apply(lambda x: f"{x:.0f}")
    dtbl["Avg OSAT %"] = dtbl["Avg OSAT %"].apply(lambda x: f"{x:.1f}%")
    dtbl["Avg SOS (min)"] = dtbl["Avg SOS (min)"].apply(lambda x: f"{x:.1f}")
    st.dataframe(dtbl, use_container_width=True, hide_index=True)

# ════════════════════════════════
# SCORECARD
# ════════════════════════════════
elif selected_tab == "Scorecard":
    import numpy as np

    all_stores = []
    for dist, stores in DISTRICTS.items():
        for s in stores:
            snum = s.split(" - ")[0].strip().lstrip("0")
            sname = s.split("-", 2)[2].strip()[:22] if len(s.split("-", 2)) >= 3 else s[:22]
            all_stores.append({"store_num": snum, "short_name": sname, "district": dist})
    sc_df = pd.DataFrame(all_stores)

    # KDS data (latest date)
    if not daily_df_all.empty:
        latest = daily_df_all[daily_df_all["data_date"] == daily_df_all["data_date"].max()]
        kds_map = latest.set_index("store_num")[["sos_min", "pre_bump", "bone_in_adopt", "make_ahead_rate", "waste"]].to_dict("index")
        for col in ["sos_min", "pre_bump", "bone_in_adopt", "make_ahead_rate", "waste"]:
            sc_df[col] = sc_df["store_num"].map(lambda s, c=col: kds_map.get(s, {}).get(c))

    # Labor data
    forecast_path = DATA_DIR / "forecast.xlsm"
    if forecast_path.exists():
        @st.cache_data(ttl=300)
        def load_sc_labor():
            raw = pd.read_excel(forecast_path, sheet_name="Forecast_Data")
            return raw[raw["year"] == 2026].copy()
        sc_labor = load_sc_labor()
        if not sc_labor.empty:
            sc_labor["store_num"] = sc_labor["store"].apply(forecast_store_num)
            la = sc_labor.groupby("store_num").agg(
                actual_sales=("actual_sales", "sum"), forecast_sales=("forecast_sales", "sum"),
                actual_labor=("actual_labor", "sum"), schedule_labor=("schedule_labor", "sum"),
                ovt_hours=("ovt_hours", "sum"),
            ).reset_index()
            la["labor_pct"] = la["actual_labor"] / la["actual_sales"]
            la["sched_labor_pct"] = la["schedule_labor"] / la["forecast_sales"]
            la["labor_var"] = la["labor_pct"] - la["sched_labor_pct"]
            for col in ["labor_pct", "labor_var", "ovt_hours"]:
                sc_df[col] = sc_df["store_num"].map(dict(zip(la["store_num"].astype(str), la[col])))

    # SMG data
    smg_path = DATA_DIR / "smg_q1.xlsx"
    if smg_path.exists():
        @st.cache_data(ttl=300)
        def load_sc_smg():
            raw = pd.read_excel(smg_path, header=None, skiprows=2)
            raw.columns = ["Store", "Measure", "Current", "LastYear", "Difference", "Count", "Count_Current", "Count_LastYear"]
            raw = raw[(raw["Measure"] != "Measure") & (raw["Store"] != "Combined")].copy()
            raw["Current"] = pd.to_numeric(raw["Current"], errors="coerce")
            store_pat = raw["Store"].str.extract(r"^(\d+)\s*-\s*(.*)")
            raw["store_num"] = store_pat[0].str.lstrip("0")
            return raw
        sc_smg = load_sc_smg()
        dissat = sc_smg[sc_smg["Measure"] == "Dissatisfaction"]
        sc_df["dissat_pct"] = sc_df["store_num"].map(dict(zip(dissat["store_num"], dissat["Current"] * 100)))

    # Scoring: each metric gets 0-100 points
    def score_sos(v):
        if pd.isna(v): return None
        if v < 10: return 100
        if v < 13: return 70
        return max(0, 100 - (v - 10) * 10)

    def score_lower_better(v, good, bad):
        if pd.isna(v): return None
        if v <= good: return 100
        if v >= bad: return 0
        return max(0, 100 - (v - good) / (bad - good) * 100)

    def score_higher_better(v, bad, good):
        if pd.isna(v): return None
        if v >= good: return 100
        if v <= bad: return 0
        return (v - bad) / (good - bad) * 100

    sc_df["score_sos"] = sc_df["sos_min"].apply(score_sos) if "sos_min" in sc_df.columns else None
    sc_df["score_prebump"] = sc_df["pre_bump"].apply(lambda v: score_lower_better(v, 0.5, 3)) if "pre_bump" in sc_df.columns else None
    sc_df["score_adopt"] = sc_df["bone_in_adopt"].apply(lambda v: score_higher_better(v, 70, 95)) if "bone_in_adopt" in sc_df.columns else None
    sc_df["score_waste"] = sc_df["waste"].apply(lambda v: score_lower_better(v, 2, 8)) if "waste" in sc_df.columns else None
    sc_df["score_labor"] = sc_df["labor_pct"].apply(lambda v: score_lower_better(v * 100, 18, 24) if pd.notna(v) else None) if "labor_pct" in sc_df.columns else None
    sc_df["score_dissat"] = sc_df["dissat_pct"].apply(lambda v: score_lower_better(v, 3, 12)) if "dissat_pct" in sc_df.columns else None

    score_cols = [c for c in sc_df.columns if c.startswith("score_")]
    sc_df["composite"] = sc_df[score_cols].mean(axis=1)
    sc_df["rank"] = sc_df["composite"].rank(ascending=False, method="min").astype("Int64")
    sc_df = sc_df.sort_values("composite", ascending=False)

    if selected_store != "All Stores":
        sk_num = extract_store_number(selected_store)
        sc_df = sc_df[sc_df["store_num"] == sk_num]
    elif selected_district != "All Districts":
        d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
        sc_df = sc_df[sc_df["store_num"].isin(d_nums)]

    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Store Scorecard &nbsp;|&nbsp; {len(sc_df)} stores &nbsp;|&nbsp; Composite score across KDS, Labor &amp; SMG</p>', unsafe_allow_html=True)

    # Top 5 / Bottom 5
    if len(sc_df) > 5:
        t5, b5 = st.columns(2)
        with t5:
            st.markdown('<div class="section-title">Top 5 Stores</div>', unsafe_allow_html=True)
            top5 = sc_df.head(5)
            for _, row in top5.iterrows():
                score = row["composite"]
                color = GREEN if score >= 75 else (ORANGE if score >= 50 else RED)
                st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0.8rem; margin:0.3rem 0; background:#FFFFFF; border-left:4px solid {color}; border-radius:4px; border:1px solid #E8ECF0;">'
                            f'<span style="color:#1F2937; font-weight:600;">#{int(row["rank"])} {row["short_name"]}</span>'
                            f'<span style="color:{color}; font-weight:700; font-size:1.1rem;">{score:.0f}</span></div>', unsafe_allow_html=True)
        with b5:
            st.markdown('<div class="section-title">Bottom 5 Stores</div>', unsafe_allow_html=True)
            bot5 = sc_df.tail(5).iloc[::-1]
            for _, row in bot5.iterrows():
                score = row["composite"]
                color = GREEN if score >= 75 else (ORANGE if score >= 50 else RED)
                st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0.8rem; margin:0.3rem 0; background:#FFFFFF; border-left:4px solid {color}; border-radius:4px; border:1px solid #E8ECF0;">'
                            f'<span style="color:#1F2937; font-weight:600;">#{int(row["rank"])} {row["short_name"]}</span>'
                            f'<span style="color:{color}; font-weight:700; font-size:1.1rem;">{score:.0f}</span></div>', unsafe_allow_html=True)

    # Composite score chart
    st.markdown('<div class="section-title">Composite Score by Store</div>', unsafe_allow_html=True)
    sc_colors = [GREEN if v >= 75 else (ORANGE if v >= 50 else RED) for v in sc_df["composite"]]
    fig_sc = go.Figure(go.Bar(
        x=sc_df["short_name"], y=sc_df["composite"],
        marker_color=sc_colors,
        text=sc_df["composite"].apply(lambda x: f"{x:.0f}"),
        textposition="outside", textfont=dict(size=9, color="#374151"),
        hovertemplate="%{x}<br>Score: %{y:.1f}<extra></extra>",
    ))
    sc_layout = {**CHART_LAYOUT, "yaxis": dict(range=[0, 110], gridcolor=GRID_COLOR, fixedrange=True)}
    fig_sc.update_layout(**sc_layout, height=400, yaxis_title="Composite Score", xaxis_tickangle=-45)
    st.plotly_chart(fig_sc, use_container_width=True, key="sc_composite", config=CHART_CONFIG)

    # Stoplight table
    st.markdown('<div class="section-title">Scorecard Detail</div>', unsafe_allow_html=True)

    def stoplight(val, good, warn_fn="lower"):
        if pd.isna(val): return "—"
        if warn_fn == "lower":
            color = GREEN if val <= good else (ORANGE if val <= good * 1.3 else RED)
        else:
            color = GREEN if val >= good else (ORANGE if val >= good * 0.85 else RED)
        return f'<span style="color:{color}; font-weight:600;">{val:.1f}</span>'

    sc_tbl = sc_df[["rank", "short_name", "district"]].copy()
    sc_tbl["Composite"] = sc_df["composite"].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "—")
    sc_tbl["SOS"] = sc_df["sos_min"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—") if "sos_min" in sc_df.columns else "—"
    sc_tbl["Pre-Bump"] = sc_df["pre_bump"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—") if "pre_bump" in sc_df.columns else "—"
    sc_tbl["Adoption"] = sc_df["bone_in_adopt"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—") if "bone_in_adopt" in sc_df.columns else "—"
    sc_tbl["Waste"] = sc_df["waste"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—") if "waste" in sc_df.columns else "—"
    sc_tbl["Labor %"] = sc_df["labor_pct"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "—") if "labor_pct" in sc_df.columns else "—"
    sc_tbl["Dissat %"] = sc_df["dissat_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—") if "dissat_pct" in sc_df.columns else "—"
    sc_tbl.columns = ["Rank", "Store", "District", "Score", "SOS (min)", "Pre-Bump %", "Adoption %", "Waste %", "Labor %", "Dissat %"]
    st.dataframe(sc_tbl, use_container_width=True, hide_index=True)

    # District scorecard
    if len(sc_df) > 5:
        st.markdown('<div class="section-title">District Average Scores</div>', unsafe_allow_html=True)
        dist_sc = sc_df.groupby("district")["composite"].mean().reset_index()
        dist_sc = dist_sc.sort_values("composite", ascending=False)
        dist_sc.columns = ["District", "Avg Score"]
        dist_colors = [GREEN if v >= 75 else (ORANGE if v >= 50 else RED) for v in dist_sc["Avg Score"]]
        fig_dsc = go.Figure(go.Bar(
            x=dist_sc["District"], y=dist_sc["Avg Score"],
            marker_color=dist_colors,
            text=dist_sc["Avg Score"].apply(lambda x: f"{x:.0f}"),
            textposition="outside", textfont=dict(size=11, color="#374151"),
            hovertemplate="%{x}<br>Score: %{y:.1f}<extra></extra>",
        ))
        dsc_layout = {**CHART_LAYOUT, "yaxis": dict(range=[0, 110], gridcolor=GRID_COLOR, fixedrange=True)}
        fig_dsc.update_layout(**dsc_layout, height=350, yaxis_title="Avg Composite Score")
        st.plotly_chart(fig_dsc, use_container_width=True, key="sc_district", config=CHART_CONFIG)

# ════════════════════════════════
# WATCH LIST
# ════════════════════════════════
elif selected_tab == "Watch List":
    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Watch List &nbsp;|&nbsp; Stores exceeding key thresholds &nbsp;|&nbsp; Auto-generated alerts</p>', unsafe_allow_html=True)

    alerts = []

    # KDS alerts
    if not daily_df_all.empty:
        latest_date = daily_df_all["data_date"].max()
        latest = daily_df_all[daily_df_all["data_date"] == latest_date].copy()
        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            latest = latest[latest["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            latest = latest[latest["store_num"].isin(d_nums)]

        sos_fail = latest[latest["sos_min"] >= 13]
        for _, r in sos_fail.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "SOS", "Value": f"{r['sos_min']:.1f} min", "Threshold": ">= 13 min", "Severity": "Critical"})

        sos_warn = latest[(latest["sos_min"] >= 10) & (latest["sos_min"] < 13)]
        for _, r in sos_warn.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "SOS", "Value": f"{r['sos_min']:.1f} min", "Threshold": "10-13 min", "Severity": "Warning"})

        waste_fail = latest[latest["waste"] > 5]
        for _, r in waste_fail.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "Waste", "Value": f"{r['waste']:.2f}%", "Threshold": "> 5%", "Severity": "Critical"})

        adopt_fail = latest[latest["bone_in_adopt"] < 85]
        for _, r in adopt_fail.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "Bone-In Adoption", "Value": f"{r['bone_in_adopt']:.1f}%", "Threshold": "< 85%", "Severity": "Critical"})

        ma_fail = latest[latest["make_ahead_rate"] > 10]
        for _, r in ma_fail.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "Make Ahead", "Value": f"{r['make_ahead_rate']:.1f}%", "Threshold": "> 10%", "Severity": "Critical"})

        pb_crit = latest[latest["pre_bump"] > 1.5]
        for _, r in pb_crit.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "Pre-Bump", "Value": f"{r['pre_bump']:.2f}%", "Threshold": "> 1.5%", "Severity": "Critical"})

        pb_warn = latest[(latest["pre_bump"] > 0.5) & (latest["pre_bump"] <= 1.5)]
        for _, r in pb_warn.iterrows():
            alerts.append({"Store": r["short_name"], "District": r.get("district", ""), "Metric": "Pre-Bump", "Value": f"{r['pre_bump']:.2f}%", "Threshold": "0.5-1.5%", "Severity": "Warning"})

    # Labor alerts
    forecast_path = DATA_DIR / "forecast.xlsm"
    if forecast_path.exists():
        @st.cache_data(ttl=300)
        def load_wl_labor():
            raw = pd.read_excel(forecast_path, sheet_name="Forecast_Data")
            return raw[raw["year"] == 2026].copy()
        wl_labor = load_wl_labor()
        if not wl_labor.empty:
            wl_labor["store_num"] = wl_labor["store"].apply(forecast_store_num)
            wl_labor["short_name"] = wl_labor["store"].apply(forecast_short_name)
            wl_labor["config_district"] = wl_labor["store_num"].map(STORE_TO_DISTRICT)
            la = wl_labor.groupby(["store_num", "short_name", "config_district"]).agg(
                actual_sales=("actual_sales", "sum"), forecast_sales=("forecast_sales", "sum"),
                actual_labor=("actual_labor", "sum"), schedule_labor=("schedule_labor", "sum"),
                ovt_hours=("ovt_hours", "sum"),
            ).reset_index()
            la["labor_pct"] = la["actual_labor"] / la["actual_sales"]
            la["labor_var"] = la["labor_pct"] - (la["schedule_labor"] / la["forecast_sales"])

            if selected_store != "All Stores":
                sk_num = extract_store_number(selected_store)
                la = la[la["store_num"] == sk_num]
            elif selected_district != "All Districts":
                d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
                la = la[la["store_num"].isin(d_nums)]

            labor_high = la[la["labor_pct"] > 0.20]
            for _, r in labor_high.iterrows():
                alerts.append({"Store": r["short_name"], "District": r.get("config_district", ""), "Metric": "Labor %", "Value": f"{r['labor_pct']:.1%}", "Threshold": "> 20%", "Severity": "Critical"})

            labor_warn = la[(la["labor_pct"] > 0.18) & (la["labor_pct"] <= 0.20)]
            for _, r in labor_warn.iterrows():
                alerts.append({"Store": r["short_name"], "District": r.get("config_district", ""), "Metric": "Labor %", "Value": f"{r['labor_pct']:.1%}", "Threshold": "18-20%", "Severity": "Warning"})

            var_high = la[la["labor_var"] > 0.02]
            for _, r in var_high.iterrows():
                alerts.append({"Store": r["short_name"], "District": r.get("config_district", ""), "Metric": "Labor Variance", "Value": f"{r['labor_var']:+.2%}", "Threshold": "> +2%", "Severity": "Critical"})

            ot_high = la[la["ovt_hours"] > 25]
            for _, r in ot_high.iterrows():
                alerts.append({"Store": r["short_name"], "District": r.get("config_district", ""), "Metric": "Overtime", "Value": f"{r['ovt_hours']:.1f} hrs", "Threshold": "> 25 hrs", "Severity": "Warning"})

    if not alerts:
        st.success("All stores within thresholds. No alerts.")
    else:
        alert_df = pd.DataFrame(alerts)

        critical_count = len(alert_df[alert_df["Severity"] == "Critical"])
        warning_count = len(alert_df[alert_df["Severity"] == "Warning"])
        stores_flagged = alert_df["Store"].nunique()
        total_stores = len(STORE_TO_DISTRICT)

        wk1, wk2, wk3 = st.columns(3)
        wk1.markdown(kpi_card("Critical", str(critical_count), "red"), unsafe_allow_html=True)
        wk2.markdown(kpi_card("Warnings", str(warning_count), "orange"), unsafe_allow_html=True)
        wk3.markdown(kpi_card("Stores Flagged", f"{stores_flagged} / {total_stores}"), unsafe_allow_html=True)

        st.markdown("")

        # Group by store — show each store as a card with its issues
        st.markdown('<div class="section-title">Stores Needing Attention</div>', unsafe_allow_html=True)
        store_groups = alert_df.groupby(["Store", "District"])
        store_severity = alert_df.groupby("Store")["Severity"].apply(lambda x: "Critical" if "Critical" in x.values else "Warning")
        store_order = store_severity.sort_values(ascending=True).index.tolist()

        for store_name in store_order:
            store_alerts = alert_df[alert_df["Store"] == store_name]
            district = store_alerts["District"].iloc[0]
            has_critical = "Critical" in store_alerts["Severity"].values
            border_color = RED if has_critical else ORANGE
            badge_color = RED if has_critical else ORANGE
            badge_text = "CRITICAL" if has_critical else "WARNING"

            issues_html = ""
            for _, row in store_alerts.iterrows():
                sev_color = RED if row["Severity"] == "Critical" else ORANGE
                dot = f'<span style="color:{sev_color};">&#9679;</span>'
                issues_html += f'<div style="padding:0.2rem 0; font-size:0.82rem; color:#374151;">{dot} <strong>{row["Metric"]}</strong>: {row["Value"]} <span style="color:#9CA3AF;">(threshold: {row["Threshold"]})</span></div>'

            st.markdown(
                f'<div style="border-left:4px solid {border_color}; background:#FFFFFF; border:1px solid #E8ECF0; border-left:4px solid {border_color}; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.6rem;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">'
                f'<span style="color:#1F2937; font-weight:700; font-size:0.95rem;">{store_name}</span>'
                f'<div><span style="color:#6B7280; font-size:0.75rem; margin-right:0.6rem;">{district}</span>'
                f'<span style="background:{badge_color}; color:white; font-size:0.65rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:10px;">{badge_text}</span></div>'
                f'</div>{issues_html}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Summary: how many stores fail each metric
        st.markdown('<div class="section-title">Threshold Summary</div>', unsafe_allow_html=True)
        thresholds_info = [
            ("SOS", ">= 13 min", "Critical"), ("SOS", "10-13 min", "Warning"),
            ("Bone-In Adoption", "< 85%", "Critical"), ("Make Ahead", "> 10%", "Critical"),
            ("Waste", "> 5%", "Critical"), ("Pre-Bump", "> 1.5%", "Critical"), ("Pre-Bump", "0.5-1.5%", "Warning"),
            ("Labor %", "> 20%", "Critical"), ("Labor %", "18-20%", "Warning"),
            ("Labor Variance", "> +2%", "Critical"), ("Overtime", "> 25 hrs", "Warning"),
        ]
        summary_rows = []
        for metric, threshold, severity in thresholds_info:
            matching = alert_df[(alert_df["Metric"] == metric) & (alert_df["Severity"] == severity)]
            count = len(matching)
            if count > 0:
                store_names = ", ".join(sorted(matching["Store"].unique())[:5])
                if len(matching["Store"].unique()) > 5:
                    store_names += f" +{len(matching['Store'].unique()) - 5} more"
                summary_rows.append({"Metric": metric, "Threshold": threshold, "Severity": severity, "Count": count, "Stores": store_names})

        if summary_rows:
            sum_df = pd.DataFrame(summary_rows)
            st.dataframe(sum_df, use_container_width=True, hide_index=True)

# ════════════════════════════════
# TRENDS
# ════════════════════════════════
elif selected_tab == "Trends":
    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Trends &nbsp;|&nbsp; Week-over-week metric movement</p>', unsafe_allow_html=True)

    if daily_df_all.empty:
        st.warning("No KDS history data available for trends.")
    else:
        trend_data = daily_df_all.copy()
        if selected_store != "All Stores":
            sk_num = extract_store_number(selected_store)
            trend_data = trend_data[trend_data["store_num"] == sk_num]
        elif selected_district != "All Districts":
            d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
            trend_data = trend_data[trend_data["store_num"].isin(d_nums)]

        daily_avg = trend_data.groupby("data_date").agg(
            sos_min=("sos_min", "mean"),
            pre_bump=("pre_bump", "mean"),
            bone_in_adopt=("bone_in_adopt", "mean"),
            make_ahead_rate=("make_ahead_rate", "mean"),
            waste=("waste", "mean"),
        ).reset_index()
        daily_avg = daily_avg.sort_values("data_date")
        daily_avg["date_str"] = daily_avg["data_date"].apply(lambda d: d.strftime("%m/%d") if hasattr(d, "strftime") else str(d)[-5:])

        # SOS Trend
        st.markdown('<div class="section-title">Speed of Service Trend</div>', unsafe_allow_html=True)
        fig_sos_t = go.Figure()
        fig_sos_t.add_trace(go.Scatter(
            x=daily_avg["date_str"], y=daily_avg["sos_min"],
            mode="lines+markers", name="Avg SOS",
            line=dict(color=TEAL, width=3), marker=dict(size=8),
            hovertemplate="%{x}<br>SOS: %{y:.1f} min<extra></extra>",
        ))
        fig_sos_t.add_hline(y=10, line_dash="dash", line_color=ORANGE, line_width=1.5, annotation_text="10 min target", annotation_font=dict(color=ORANGE, size=10))
        fig_sos_t.add_hline(y=13, line_dash="dash", line_color=RED, line_width=1.5, annotation_text="13 min critical", annotation_font=dict(color=RED, size=10))
        fig_sos_t.update_layout(**CHART_LAYOUT, height=350, yaxis_title="Minutes")
        st.plotly_chart(fig_sos_t, use_container_width=True, key="trend_sos", config=CHART_CONFIG)

        # Pre-bump & Waste trends
        tl, tr = st.columns(2)
        with tl:
            st.markdown('<div class="section-title">Pre-Bump Rate Trend</div>', unsafe_allow_html=True)
            fig_pb_t = go.Figure()
            fig_pb_t.add_trace(go.Scatter(
                x=daily_avg["date_str"], y=daily_avg["pre_bump"],
                mode="lines+markers", name="Pre-Bump %",
                line=dict(color=ORANGE, width=3), marker=dict(size=8),
            ))
            fig_pb_t.add_hline(y=0.5, line_dash="dash", line_color=ORANGE, line_width=1)
            fig_pb_t.add_hline(y=1.5, line_dash="dash", line_color=RED, line_width=1)
            fig_pb_t.update_layout(**CHART_LAYOUT, height=320, yaxis_title="Pre-Bump %")
            st.plotly_chart(fig_pb_t, use_container_width=True, key="trend_pb", config=CHART_CONFIG)

        with tr:
            st.markdown('<div class="section-title">Waste % Trend</div>', unsafe_allow_html=True)
            fig_w_t = go.Figure()
            fig_w_t.add_trace(go.Scatter(
                x=daily_avg["date_str"], y=daily_avg["waste"],
                mode="lines+markers", name="Waste %",
                line=dict(color=RED, width=3), marker=dict(size=8),
            ))
            fig_w_t.add_hline(y=5, line_dash="dash", line_color=RED, line_width=1, annotation_text="5% threshold", annotation_font=dict(color=RED, size=10))
            fig_w_t.update_layout(**CHART_LAYOUT, height=320, yaxis_title="Waste %")
            st.plotly_chart(fig_w_t, use_container_width=True, key="trend_waste", config=CHART_CONFIG)

        # Adoption & Make Ahead trends
        al, ar = st.columns(2)
        with al:
            st.markdown('<div class="section-title">Bone-In Adoption Trend</div>', unsafe_allow_html=True)
            fig_ad_t = go.Figure()
            fig_ad_t.add_trace(go.Scatter(
                x=daily_avg["date_str"], y=daily_avg["bone_in_adopt"],
                mode="lines+markers", name="Adoption %",
                line=dict(color=GREEN, width=3), marker=dict(size=8),
            ))
            fig_ad_t.add_hline(y=85, line_dash="dash", line_color=RED, line_width=1, annotation_text="85% minimum", annotation_font=dict(color=RED, size=10))
            fig_ad_t.update_layout(**CHART_LAYOUT, height=320, yaxis_title="Adoption %")
            st.plotly_chart(fig_ad_t, use_container_width=True, key="trend_adopt", config=CHART_CONFIG)

        with ar:
            st.markdown('<div class="section-title">Make Ahead Rate Trend</div>', unsafe_allow_html=True)
            fig_ma_t = go.Figure()
            fig_ma_t.add_trace(go.Scatter(
                x=daily_avg["date_str"], y=daily_avg["make_ahead_rate"],
                mode="lines+markers", name="Make Ahead %",
                line=dict(color=GOLD, width=3), marker=dict(size=8),
            ))
            fig_ma_t.add_hline(y=10, line_dash="dash", line_color=RED, line_width=1, annotation_text="10% max", annotation_font=dict(color=RED, size=10))
            fig_ma_t.update_layout(**CHART_LAYOUT, height=320, yaxis_title="Make Ahead %")
            st.plotly_chart(fig_ma_t, use_container_width=True, key="trend_ma", config=CHART_CONFIG)

        # Store-level SOS trend (top 5 worst)
        if selected_store == "All Stores":
            st.markdown('<div class="section-title">SOS Trend — Top 5 Worst Stores</div>', unsafe_allow_html=True)
            latest_date = trend_data["data_date"].max()
            worst5 = trend_data[trend_data["data_date"] == latest_date].nlargest(5, "sos_min")["store_num"].tolist()
            worst_trend = trend_data[trend_data["store_num"].isin(worst5)].copy()
            worst_trend["date_str"] = worst_trend["data_date"].apply(lambda d: d.strftime("%m/%d") if hasattr(d, "strftime") else str(d)[-5:])

            fig_w5 = go.Figure()
            colors = [RED, ORANGE, GOLD, TEAL, DARK]
            for i, snum in enumerate(worst5):
                sdata = worst_trend[worst_trend["store_num"] == snum].sort_values("data_date")
                name = sdata["short_name"].iloc[0] if len(sdata) > 0 else snum
                fig_w5.add_trace(go.Scatter(
                    x=sdata["date_str"], y=sdata["sos_min"],
                    mode="lines+markers", name=name,
                    line=dict(color=colors[i % len(colors)], width=2), marker=dict(size=6),
                ))
            fig_w5.add_hline(y=13, line_dash="dash", line_color=RED, line_width=1)
            fig_w5.update_layout(**CHART_LAYOUT, height=380, yaxis_title="SOS (min)",
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#374151")))
            st.plotly_chart(fig_w5, use_container_width=True, key="trend_worst5", config=CHART_CONFIG)

        # Labor trend by period
        forecast_path = DATA_DIR / "forecast.xlsm"
        if forecast_path.exists():
            @st.cache_data(ttl=300)
            def load_trend_labor():
                raw = pd.read_excel(forecast_path, sheet_name="Forecast_Data")
                return raw[raw["year"] == 2026].copy()
            tr_labor = load_trend_labor()
            if not tr_labor.empty:
                tr_labor["store_num"] = tr_labor["store"].apply(forecast_store_num)
                tr_labor["config_district"] = tr_labor["store_num"].map(STORE_TO_DISTRICT)

                if selected_store != "All Stores":
                    sk_num = extract_store_number(selected_store)
                    tr_labor = tr_labor[tr_labor["store_num"] == sk_num]
                elif selected_district != "All Districts":
                    d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
                    tr_labor = tr_labor[tr_labor["store_num"].isin(d_nums)]

                period_trend = tr_labor.groupby("week_d").agg(
                    actual_labor=("actual_labor", "sum"),
                    actual_sales=("actual_sales", "sum"),
                    schedule_labor=("schedule_labor", "sum"),
                    forecast_sales=("forecast_sales", "sum"),
                ).reset_index()
                period_trend["actual_pct"] = period_trend["actual_labor"] / period_trend["actual_sales"] * 100
                period_trend["sched_pct"] = period_trend["schedule_labor"] / period_trend["forecast_sales"] * 100
                period_trend = period_trend.sort_values("week_d")

                st.markdown('<div class="section-title">Labor % Trend by Week</div>', unsafe_allow_html=True)
                fig_lt = go.Figure()
                fig_lt.add_trace(go.Scatter(
                    x=period_trend["week_d"], y=period_trend["actual_pct"],
                    name="Actual Labor %", mode="lines+markers",
                    line=dict(color=ORANGE, width=3), marker=dict(size=8),
                ))
                fig_lt.add_trace(go.Scatter(
                    x=period_trend["week_d"], y=period_trend["sched_pct"],
                    name="Scheduled Labor %", mode="lines+markers",
                    line=dict(color=TEAL, width=2, dash="dash"), marker=dict(size=6),
                ))
                fig_lt.add_hline(y=18, line_dash="dash", line_color=RED, line_width=1)
                fig_lt.update_layout(**CHART_LAYOUT, height=380, yaxis_title="Labor %",
                                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#374151")))
                st.plotly_chart(fig_lt, use_container_width=True, key="trend_labor", config=CHART_CONFIG)

# ════════════════════════════════
# WING WORM
# ════════════════════════════════
elif selected_tab == "Wing Worm":
    st.markdown('<div class="section-title">Wing Worm</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6B7280; font-size:0.85rem;">Guide the worm to eat boneless wings! Use arrow keys or WASD to move.</p>', unsafe_allow_html=True)

    import streamlit.components.v1 as components
    game_html = """
    <div id="game-wrapper" style="display:flex; flex-direction:column; align-items:center;">
        <div style="display:flex; justify-content:space-between; width:400px; margin-bottom:8px;">
            <span id="score" style="color:#1F2937; font-weight:700; font-size:1rem;">Score: 0</span>
            <span id="high-score" style="color:#059669; font-weight:700; font-size:1rem;">Best: 0</span>
        </div>
        <canvas id="game" width="400" height="400" style="border:2px solid #0D5C3F; border-radius:8px; background:#0A4A32;"></canvas>
        <div id="game-over" style="display:none; margin-top:12px; text-align:center;">
            <p style="color:#DC2626; font-weight:700; font-size:1.2rem; margin:0;">Game Over!</p>
            <p style="color:#6B7280; font-size:0.85rem; margin:4px 0;">Press Space or tap to restart</p>
        </div>
        <div id="start-msg" style="margin-top:12px; text-align:center;">
            <p style="color:#059669; font-weight:600; font-size:0.95rem; margin:0;">Press any arrow key or tap to start!</p>
        </div>
    </div>
    <script>
    (function() {
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        const GRID = 20;
        const COLS = canvas.width / GRID;
        const ROWS = canvas.height / GRID;

        let snake, dir, nextDir, food, score, highScore, gameOver, started, interval, lastTime, accumulator;

        highScore = parseInt(localStorage.getItem('wingworm_high') || '0');
        document.getElementById('high-score').textContent = 'Best: ' + highScore;

        function init() {
            snake = [{x:10, y:10}, {x:9, y:10}, {x:8, y:10}];
            dir = {x:1, y:0};
            nextDir = {x:1, y:0};
            score = 0;
            gameOver = false;
            started = false;
            interval = 120;
            lastTime = 0;
            accumulator = 0;
            placeFood();
            updateScore();
            document.getElementById('game-over').style.display = 'none';
            document.getElementById('start-msg').style.display = 'block';
            draw();
        }

        function placeFood() {
            do {
                food = {x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS)};
            } while (snake.some(s => s.x === food.x && s.y === food.y));
        }

        function updateScore() {
            document.getElementById('score').textContent = 'Score: ' + score;
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('wingworm_high', highScore);
                document.getElementById('high-score').textContent = 'Best: ' + highScore;
            }
        }

        function drawRoundRect(x, y, w, h, r, color) {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(x+r, y);
            ctx.arcTo(x+w, y, x+w, y+h, r);
            ctx.arcTo(x+w, y+h, x, y+h, r);
            ctx.arcTo(x, y+h, x, y, r);
            ctx.arcTo(x, y, x+w, y, r);
            ctx.closePath();
            ctx.fill();
        }

        function draw() {
            // Dark green gradient background
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, '#0A4A32');
            grad.addColorStop(1, '#0D5C3F');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Subtle grid
            ctx.strokeStyle = 'rgba(255,255,255,0.06)';
            ctx.lineWidth = 0.5;
            for (let i = 0; i < COLS; i++) {
                ctx.beginPath(); ctx.moveTo(i*GRID, 0); ctx.lineTo(i*GRID, canvas.height); ctx.stroke();
            }
            for (let i = 0; i < ROWS; i++) {
                ctx.beginPath(); ctx.moveTo(0, i*GRID); ctx.lineTo(canvas.width, i*GRID); ctx.stroke();
            }

            // Food (boneless wing) with glow
            const fx = food.x * GRID, fy = food.y * GRID;
            ctx.shadowColor = '#F59E0B';
            ctx.shadowBlur = 10;
            ctx.fillStyle = '#D97706';
            ctx.beginPath();
            ctx.ellipse(fx + GRID/2, fy + GRID/2, GRID/2.2, GRID/2.8, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#F59E0B';
            ctx.beginPath();
            ctx.ellipse(fx + GRID/2, fy + GRID/2.5, GRID/3.5, GRID/4, 0, 0, Math.PI*2);
            ctx.fill();

            // Snake with glow on head
            snake.forEach((seg, i) => {
                if (i === 0) {
                    ctx.shadowColor = '#34D399';
                    ctx.shadowBlur = 8;
                }
                const color = i === 0 ? '#10B981' : (i % 2 === 0 ? '#059669' : '#0D9488');
                drawRoundRect(seg.x * GRID + 1, seg.y * GRID + 1, GRID - 2, GRID - 2, 4, color);
                if (i === 0) ctx.shadowBlur = 0;
            });

            // Eyes on head
            const head = snake[0];
            const eyeSize = 3;
            ctx.fillStyle = '#FFFFFF';
            if (dir.x === 1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+15, head.y*GRID+6, eyeSize, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+15, head.y*GRID+14, eyeSize, 0, Math.PI*2); ctx.fill();
            } else if (dir.x === -1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+5, head.y*GRID+6, eyeSize, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+5, head.y*GRID+14, eyeSize, 0, Math.PI*2); ctx.fill();
            } else if (dir.y === -1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+6, head.y*GRID+5, eyeSize, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+14, head.y*GRID+5, eyeSize, 0, Math.PI*2); ctx.fill();
            } else {
                ctx.beginPath(); ctx.arc(head.x*GRID+6, head.y*GRID+15, eyeSize, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+14, head.y*GRID+15, eyeSize, 0, Math.PI*2); ctx.fill();
            }
            ctx.fillStyle = '#0A4A32';
            if (dir.x === 1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+16, head.y*GRID+6, 1.5, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+16, head.y*GRID+14, 1.5, 0, Math.PI*2); ctx.fill();
            } else if (dir.x === -1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+4, head.y*GRID+6, 1.5, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+4, head.y*GRID+14, 1.5, 0, Math.PI*2); ctx.fill();
            } else if (dir.y === -1) {
                ctx.beginPath(); ctx.arc(head.x*GRID+6, head.y*GRID+4, 1.5, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+14, head.y*GRID+4, 1.5, 0, Math.PI*2); ctx.fill();
            } else {
                ctx.beginPath(); ctx.arc(head.x*GRID+6, head.y*GRID+16, 1.5, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(head.x*GRID+14, head.y*GRID+16, 1.5, 0, Math.PI*2); ctx.fill();
            }
        }

        function step() {
            if (gameOver) return;
            dir = nextDir;
            const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};

            if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) { die(); return; }
            if (snake.some(s => s.x === head.x && s.y === head.y)) { die(); return; }

            snake.unshift(head);
            if (head.x === food.x && head.y === food.y) {
                score++;
                updateScore();
                placeFood();
                if (interval > 60) interval -= 2;
            } else {
                snake.pop();
            }
            draw();
        }

        function gameLoop(timestamp) {
            if (!started || gameOver) return;
            if (!lastTime) lastTime = timestamp;
            const delta = timestamp - lastTime;
            lastTime = timestamp;
            accumulator += delta;
            while (accumulator >= interval) {
                step();
                accumulator -= interval;
                if (gameOver) break;
            }
            requestAnimationFrame(gameLoop);
        }

        function die() {
            gameOver = true;
            document.getElementById('game-over').style.display = 'block';
            draw();
            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 28px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Game Over!', canvas.width/2, canvas.height/2 - 10);
            ctx.font = '16px sans-serif';
            ctx.fillText('Score: ' + score + '  |  Wings eaten!', canvas.width/2, canvas.height/2 + 20);
        }

        function startGame() {
            if (!started) {
                started = true;
                lastTime = 0;
                accumulator = 0;
                document.getElementById('start-msg').style.display = 'none';
                requestAnimationFrame(gameLoop);
            }
        }

        document.addEventListener('keydown', function(e) {
            if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','w','a','s','d',' '].includes(e.key)) {
                e.preventDefault();
            }
            if (gameOver && (e.key === ' ' || e.key === 'Enter')) { init(); return; }
            if (e.key === 'ArrowUp' || e.key === 'w') { if (dir.y !== 1) { nextDir = {x:0,y:-1}; startGame(); } }
            else if (e.key === 'ArrowDown' || e.key === 's') { if (dir.y !== -1) { nextDir = {x:0,y:1}; startGame(); } }
            else if (e.key === 'ArrowLeft' || e.key === 'a') { if (dir.x !== 1) { nextDir = {x:-1,y:0}; startGame(); } }
            else if (e.key === 'ArrowRight' || e.key === 'd') { if (dir.x !== -1) { nextDir = {x:1,y:0}; startGame(); } }
        });

        let touchStart = null;
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            if (gameOver) { init(); return; }
            touchStart = {x: e.touches[0].clientX, y: e.touches[0].clientY};
            startGame();
        });
        canvas.addEventListener('touchmove', function(e) {
            e.preventDefault();
            if (!touchStart) return;
            const dx = e.touches[0].clientX - touchStart.x;
            const dy = e.touches[0].clientY - touchStart.y;
            if (Math.abs(dx) > Math.abs(dy)) {
                if (dx > 20 && dir.x !== -1) nextDir = {x:1, y:0};
                else if (dx < -20 && dir.x !== 1) nextDir = {x:-1, y:0};
            } else {
                if (dy > 20 && dir.y !== -1) nextDir = {x:0, y:1};
                else if (dy < -20 && dir.y !== 1) nextDir = {x:0, y:-1};
            }
            touchStart = {x: e.touches[0].clientX, y: e.touches[0].clientY};
        });

        canvas.addEventListener('click', function() {
            if (gameOver) init();
            else startGame();
        });

        init();
    })();
    </script>
    """
    components.html(game_html, height=500)

st.markdown("---")
st.markdown('<p style="color:#999999; font-size:0.75rem; text-align:center;">FL Wingmen Dashboard &nbsp;|&nbsp; Smart Kitchen Performance &amp; Forecast Data</p>', unsafe_allow_html=True)
