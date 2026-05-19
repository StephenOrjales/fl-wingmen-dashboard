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

    nav_options = ["Daily KDS Snapshot", "Q1 Performance", "Q2 Performance"]
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

st.markdown("---")
st.markdown('<p style="color:#999999; font-size:0.75rem; text-align:center;">FL Wingmen Dashboard &nbsp;|&nbsp; Smart Kitchen Performance &amp; Forecast Data</p>', unsafe_allow_html=True)
