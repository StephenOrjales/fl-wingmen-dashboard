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

    .stDataFrame { border-radius: 8px; overflow: hidden; }

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

    nav_options = ["Daily KDS Snapshot", "Sales Performance", "Labor Dashboard", "SMG (Guest Satisfaction)", "District Comparison", "Q1 Performance", "Q2 Performance"]
    selected_tab = st.radio("Navigation", nav_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Filters**")

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
        pb_c = "green" if avg_prebump < 1 else ("orange" if avg_prebump < 3 else "red")
        adopt_c = "green" if avg_adopt >= 97 else ("orange" if avg_adopt >= 90 else "red")
        ma_c = "green" if avg_make >= 80 else ("orange" if avg_make >= 50 else "red")
        waste_c = "green" if avg_waste < 2 else ("orange" if avg_waste < 5 else "red")

        k1.markdown(kpi_card("Avg SOS", f"{avg_sos:.1f} min", sos_c), unsafe_allow_html=True)
        k2.markdown(kpi_card("Pre-Bump Rate", f"{avg_prebump:.2f}%", pb_c), unsafe_allow_html=True)
        k3.markdown(kpi_card("Cook Adoption", f"{avg_adopt:.1f}%", adopt_c), unsafe_allow_html=True)
        k4.markdown(kpi_card("Make Ahead Rate", f"{avg_make:.1f}%", ma_c), unsafe_allow_html=True)
        k5.markdown(kpi_card("Waste", f"{avg_waste:.2f}%", waste_c), unsafe_allow_html=True)

        st.markdown("")

        # ── SOS Overall by Store ──
        st.markdown('<div class="section-title">Speed of Service (Overall) by Store</div>', unsafe_allow_html=True)
        sos_kds = kds[kds["sos_min"].notna()].sort_values("sos_min")
        sos_colors = [RED if v > 12 else (ORANGE if v > 10 else TEAL) for v in sos_kds["sos_min"]]
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
            pb_colors = [RED if v > 3 else (ORANGE if v > 1 else TEAL) for v in pb_kds["pre_bump"]]
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
            ad_colors = [RED if v < 90 else (ORANGE if v < 97 else "#059669") for v in ad_kds["bone_in_adopt"]]
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
            ma_colors = [RED if v < 50 else (ORANGE if v < 80 else "#059669") for v in ma_kds["make_ahead_rate"]]
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
            w_colors = [RED if v > 5 else (ORANGE if v > 2 else TEAL) for v in w_kds["waste"]]
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
                st.markdown('<div class="section-title">Overtime Hours by Store</div>', unsafe_allow_html=True)
                ot_sorted = labor_df.sort_values("overtime_hours", ascending=False)
                ot_colors = [RED if v > 25 else (ORANGE if v > 10 else GREEN) for v in ot_sorted["overtime_hours"]]
                fig_ot = go.Figure(go.Bar(
                    x=ot_sorted["short_name"], y=ot_sorted["overtime_hours"],
                    marker_color=ot_colors,
                    hovertemplate="%{x}<br>OT: %{y:.1f} hrs<extra></extra>",
                ))
                fig_ot.update_layout(**CHART_LAYOUT, height=370, yaxis_title="OT Hours", xaxis_tickangle=-45)
                st.plotly_chart(fig_ot, use_container_width=True, key="labor_ot", config=CHART_CONFIG)

            with lr:
                st.markdown('<div class="section-title">Actual vs Guide Hours</div>', unsafe_allow_html=True)
                hv_sorted = labor_df.sort_values("hours_variance")
                hv_colors = [RED if v > 20 else (ORANGE if v > 0 else GREEN) for v in hv_sorted["hours_variance"]]
                fig_hv = go.Figure(go.Bar(
                    x=hv_sorted["short_name"], y=hv_sorted["hours_variance"],
                    marker_color=hv_colors,
                    hovertemplate="%{x}<br>Var: %{y:+.0f} hrs<extra></extra>",
                ))
                fig_hv.add_hline(y=0, line_color="#BDBDBD", line_width=1)
                fig_hv.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Hours vs Guide", xaxis_tickangle=-45)
                st.plotly_chart(fig_hv, use_container_width=True, key="labor_hv", config=CHART_CONFIG)

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
    import numpy as np
    np.random.seed(77)

    all_stores = []
    for dist, stores in DISTRICTS.items():
        for s in stores:
            snum = s.split(" - ")[0].strip().lstrip("0")
            sname = s.split("-", 2)[2].strip()[:22] if len(s.split("-", 2)) >= 3 else s[:22]
            all_stores.append({"store": s, "store_num": snum, "short_name": sname, "district": dist})
    smg_df = pd.DataFrame(all_stores)

    smg_df["osat"] = np.random.uniform(55, 95, len(smg_df)).round(1)
    smg_df["food_quality"] = np.random.uniform(60, 96, len(smg_df)).round(1)
    smg_df["speed_of_service"] = np.random.uniform(40, 90, len(smg_df)).round(1)
    smg_df["friendliness"] = np.random.uniform(65, 98, len(smg_df)).round(1)
    smg_df["order_accuracy"] = np.random.uniform(70, 99, len(smg_df)).round(1)
    smg_df["cleanliness"] = np.random.uniform(55, 95, len(smg_df)).round(1)
    smg_df["responses"] = np.random.randint(8, 85, len(smg_df))

    if selected_store != "All Stores":
        sk_num = extract_store_number(selected_store)
        smg_df = smg_df[smg_df["store_num"] == sk_num]
    elif selected_district != "All Districts":
        d_nums = {s.split(" - ")[0].strip().lstrip("0") for s in DISTRICTS.get(selected_district, [])}
        smg_df = smg_df[smg_df["store_num"].isin(d_nums)]

    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">Guest Satisfaction (SMG) &nbsp;|&nbsp; {len(smg_df)} stores &nbsp;|&nbsp; <span style="color:#D97706; font-weight:600;">Sample Data</span></p>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    avg_osat = smg_df["osat"].mean()
    avg_food = smg_df["food_quality"].mean()
    avg_speed = smg_df["speed_of_service"].mean()
    avg_friend = smg_df["friendliness"].mean()
    avg_accuracy = smg_df["order_accuracy"].mean()

    osat_c = "green" if avg_osat >= 80 else ("orange" if avg_osat >= 70 else "red")
    food_c = "green" if avg_food >= 80 else ("orange" if avg_food >= 70 else "red")
    speed_c = "green" if avg_speed >= 75 else ("orange" if avg_speed >= 60 else "red")

    k1.markdown(kpi_card("Overall OSAT", f"{avg_osat:.1f}%", osat_c), unsafe_allow_html=True)
    k2.markdown(kpi_card("Food Quality", f"{avg_food:.1f}%", food_c), unsafe_allow_html=True)
    k3.markdown(kpi_card("Speed of Service", f"{avg_speed:.1f}%", speed_c), unsafe_allow_html=True)
    k4.markdown(kpi_card("Friendliness", f"{avg_friend:.1f}%"), unsafe_allow_html=True)
    k5.markdown(kpi_card("Order Accuracy", f"{avg_accuracy:.1f}%"), unsafe_allow_html=True)

    st.markdown("")

    st.markdown('<div class="section-title">Overall OSAT by Store</div>', unsafe_allow_html=True)
    osat_sorted = smg_df.sort_values("osat")
    osat_colors = [RED if v < 70 else (ORANGE if v < 80 else GREEN) for v in osat_sorted["osat"]]
    fig_osat = go.Figure(go.Bar(
        x=osat_sorted["short_name"], y=osat_sorted["osat"],
        marker_color=osat_colors,
        hovertemplate="%{x}<br>OSAT: %{y:.1f}%<extra></extra>",
    ))
    fig_osat.add_hline(y=80, line_dash="dash", line_color=GREEN, line_width=1.5,
                       annotation_text="80% target", annotation_font=dict(color="#059669", size=10))
    fig_osat.update_layout(**CHART_LAYOUT, height=380, yaxis_title="OSAT %", xaxis_tickangle=-45)
    st.plotly_chart(fig_osat, use_container_width=True, key="smg_osat", config=CHART_CONFIG)

    sl, sr = st.columns(2)
    with sl:
        st.markdown('<div class="section-title">Food Quality Score</div>', unsafe_allow_html=True)
        fq_sorted = smg_df.sort_values("food_quality")
        fq_colors = [RED if v < 70 else (ORANGE if v < 80 else GREEN) for v in fq_sorted["food_quality"]]
        fig_fq = go.Figure(go.Bar(
            x=fq_sorted["short_name"], y=fq_sorted["food_quality"],
            marker_color=fq_colors,
            hovertemplate="%{x}<br>Food: %{y:.1f}%<extra></extra>",
        ))
        fig_fq.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Food Quality %", xaxis_tickangle=-45)
        st.plotly_chart(fig_fq, use_container_width=True, key="smg_food", config=CHART_CONFIG)

    with sr:
        st.markdown('<div class="section-title">Speed of Service Score</div>', unsafe_allow_html=True)
        sp_sorted = smg_df.sort_values("speed_of_service")
        sp_colors = [RED if v < 60 else (ORANGE if v < 75 else GREEN) for v in sp_sorted["speed_of_service"]]
        fig_sp = go.Figure(go.Bar(
            x=sp_sorted["short_name"], y=sp_sorted["speed_of_service"],
            marker_color=sp_colors,
            hovertemplate="%{x}<br>Speed: %{y:.1f}%<extra></extra>",
        ))
        fig_sp.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Speed Score %", xaxis_tickangle=-45)
        st.plotly_chart(fig_sp, use_container_width=True, key="smg_speed", config=CHART_CONFIG)

    cl, cr = st.columns(2)
    with cl:
        st.markdown('<div class="section-title">Friendliness Score</div>', unsafe_allow_html=True)
        fr_sorted = smg_df.sort_values("friendliness")
        fig_fr = go.Figure(go.Bar(
            x=fr_sorted["short_name"], y=fr_sorted["friendliness"],
            marker_color=TEAL,
            hovertemplate="%{x}<br>Friendliness: %{y:.1f}%<extra></extra>",
        ))
        fig_fr.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Friendliness %", xaxis_tickangle=-45)
        st.plotly_chart(fig_fr, use_container_width=True, key="smg_friend", config=CHART_CONFIG)

    with cr:
        st.markdown('<div class="section-title">Order Accuracy Score</div>', unsafe_allow_html=True)
        oa_sorted = smg_df.sort_values("order_accuracy")
        fig_oa = go.Figure(go.Bar(
            x=oa_sorted["short_name"], y=oa_sorted["order_accuracy"],
            marker_color=TEAL,
            hovertemplate="%{x}<br>Accuracy: %{y:.1f}%<extra></extra>",
        ))
        fig_oa.update_layout(**CHART_LAYOUT, height=370, yaxis_title="Accuracy %", xaxis_tickangle=-45)
        st.plotly_chart(fig_oa, use_container_width=True, key="smg_accuracy", config=CHART_CONFIG)

    st.markdown('<div class="section-title">SMG Detail Table</div>', unsafe_allow_html=True)
    smg_tbl = smg_df[["short_name", "district", "osat", "food_quality", "speed_of_service", "friendliness", "order_accuracy", "cleanliness", "responses"]].copy()
    smg_tbl.columns = ["Store", "District", "OSAT %", "Food %", "Speed %", "Friendly %", "Accuracy %", "Clean %", "Responses"]
    smg_tbl = smg_tbl.sort_values("OSAT %", ascending=False)
    st.dataframe(smg_tbl, use_container_width=True, hide_index=True)

# ════════════════════════════════
# DISTRICT COMPARISON
# ════════════════════════════════
elif selected_tab == "District Comparison":
    import numpy as np
    np.random.seed(42)

    all_stores = []
    for dist, stores in DISTRICTS.items():
        for s in stores:
            snum = s.split(" - ")[0].strip().lstrip("0")
            sname = s.split("-", 2)[2].strip()[:22] if len(s.split("-", 2)) >= 3 else s[:22]
            all_stores.append({"store": s, "store_num": snum, "short_name": sname, "district": dist})
    comp_df = pd.DataFrame(all_stores)

    np.random.seed(42)
    comp_df["net_sales"] = np.random.uniform(28000, 65000, len(comp_df)).round(0)
    comp_df["sss_growth"] = np.random.uniform(-5, 15, len(comp_df)).round(1)
    np.random.seed(99)
    comp_df["labor_pct"] = np.random.uniform(0.14, 0.24, len(comp_df))
    comp_df["overtime"] = np.random.uniform(0, 35, len(comp_df)).round(1)
    np.random.seed(77)
    comp_df["osat"] = np.random.uniform(55, 95, len(comp_df)).round(1)

    if not daily_df_all.empty:
        latest_date = daily_df_all["data_date"].max()
        daily_latest = daily_df_all[daily_df_all["data_date"] == latest_date]
        sos_map = dict(zip(daily_latest["store_num"].astype(str), daily_latest["sos_min"]))
        comp_df["sos_min"] = comp_df["store_num"].map(sos_map)
    else:
        comp_df["sos_min"] = np.random.uniform(7, 18, len(comp_df)).round(1)

    district_agg = comp_df.groupby("district").agg(
        stores=("store", "count"),
        total_sales=("net_sales", "sum"),
        avg_sales=("net_sales", "mean"),
        avg_sss=("sss_growth", "mean"),
        avg_labor=("labor_pct", "mean"),
        total_ot=("overtime", "sum"),
        avg_osat=("osat", "mean"),
        avg_sos=("sos_min", "mean"),
    ).reset_index()
    district_agg = district_agg.sort_values("district")

    st.markdown(f'<p style="color:#6B7280; font-size:0.85rem;">District Comparison &nbsp;|&nbsp; {len(district_agg)} districts &nbsp;|&nbsp; <span style="color:#D97706; font-weight:600;">Sample Data (Sales, Labor, SMG)</span></p>', unsafe_allow_html=True)

    dist_colors = [GREEN, TEAL, GOLD, ORANGE, "#7C3AED", "#0EA5E9"]

    st.markdown('<div class="section-title">Total Sales by District</div>', unsafe_allow_html=True)
    fig_ds = go.Figure(go.Bar(
        x=district_agg["district"], y=district_agg["total_sales"],
        marker_color=dist_colors[:len(district_agg)],
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    ))
    fig_ds.update_layout(**CHART_LAYOUT, height=350, yaxis_title="Total Sales ($)")
    st.plotly_chart(fig_ds, use_container_width=True, key="dist_sales", config=CHART_CONFIG)

    dl, dm, dr = st.columns(3)
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
    dtbl.columns = ["District", "Stores", "Total Sales", "Avg Sales/Store", "Avg SSS %", "Avg Labor %", "Total OT Hrs", "Avg OSAT %", "Avg SOS (min)"]
    dtbl["Total Sales"] = dtbl["Total Sales"].apply(lambda x: f"${x:,.0f}")
    dtbl["Avg Sales/Store"] = dtbl["Avg Sales/Store"].apply(lambda x: f"${x:,.0f}")
    dtbl["Avg SSS %"] = dtbl["Avg SSS %"].apply(lambda x: f"{x:+.1f}%")
    dtbl["Avg Labor %"] = dtbl["Avg Labor %"].apply(lambda x: f"{x:.1%}")
    dtbl["Total OT Hrs"] = dtbl["Total OT Hrs"].apply(lambda x: f"{x:.0f}")
    dtbl["Avg OSAT %"] = dtbl["Avg OSAT %"].apply(lambda x: f"{x:.1f}%")
    dtbl["Avg SOS (min)"] = dtbl["Avg SOS (min)"].apply(lambda x: f"{x:.1f}")
    st.dataframe(dtbl, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown('<p style="color:#999999; font-size:0.75rem; text-align:center;">FL Wingmen Dashboard &nbsp;|&nbsp; Smart Kitchen Performance &amp; Forecast Data</p>', unsafe_allow_html=True)
