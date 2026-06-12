"""
District Report PPT Generator for FL Wingmen Dashboard.
Generates a branded PowerPoint deck per district for weekly DM meetings.
"""
import io
import pandas as pd
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

DATA_DIR = Path(__file__).parent / "data"

# ── Brand colors ──
DARK_GREEN = RGBColor(0x1A, 0x3C, 0x34)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF8, 0xFA, 0xFC)
GRAY_TEXT = RGBColor(0x6B, 0x72, 0x80)
RED = RGBColor(0xDC, 0x26, 0x26)
GREEN = RGBColor(0x05, 0x96, 0x69)
ORANGE = RGBColor(0xD9, 0x77, 0x06)
BLACK = RGBColor(0x1F, 0x29, 0x37)

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)


def _add_title_bar(slide, title_text, subtitle_text=""):
    """Add a dark green title bar at the top of the slide."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, Inches(1.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = DARK_GREEN
    bar.line.fill.background()

    tf = bar.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.LEFT
    tf.margin_left = Inches(0.5)
    tf.margin_top = Inches(0.15)

    if subtitle_text:
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.size = Pt(13)
        p2.font.color.rgb = RGBColor(0xBB, 0xCC, 0xBB)
        p2.alignment = PP_ALIGN.LEFT


def _add_table(slide, df, left, top, width, height, header_color=DARK_GREEN):
    """Add a styled table to the slide."""
    rows, cols = len(df) + 1, len(df.columns)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Set column widths evenly
    col_w = int(width / cols)
    for i in range(cols):
        table.columns[i].width = col_w

    # Header row
    for j, col_name in enumerate(df.columns):
        cell = table.cell(0, j)
        cell.text = str(col_name)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Data rows
    for i, (_, row) in enumerate(df.iterrows()):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = str(val) if pd.notna(val) else "—"
            bg = LIGHT_GRAY if i % 2 == 0 else WHITE
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9)
                p.font.color.rgb = BLACK
                p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    return table_shape


def _add_callouts(slide, callouts, top):
    """Add a 'Key Callouts' box."""
    left = Inches(0.5)
    width = SLIDE_WIDTH - Inches(1)
    height = Inches(0.3 + 0.25 * len(callouts))

    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0xFE, 0xF3, 0xC7)  # light yellow
    box.line.color.rgb = RGBColor(0xF5, 0x9E, 0x0B)
    box.line.width = Pt(1)

    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.1)

    p = tf.paragraphs[0]
    p.text = "Key Callouts"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x92, 0x40, 0x0E)

    for c in callouts:
        p2 = tf.add_paragraph()
        p2.text = f"• {c}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = BLACK


def _fmt_sos(minutes):
    if pd.isna(minutes):
        return "—"
    m = int(minutes)
    s = int(round((minutes - m) * 60))
    return f"{m}:{s:02d}"


def _get_district_stores(district, store_to_district):
    """Get list of store numbers for a district."""
    return [snum for snum, d in store_to_district.items() if d == district]


def generate_district_ppt(district, store_to_district, districts_config):
    """Generate a complete PPT for the given district. Returns bytes."""
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]  # blank

    d_stores = _get_district_stores(district, store_to_district)

    # ════════════════════════════════════════
    # SLIDE 1: TITLE / SUMMARY
    # ════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    # Full green background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_GREEN
    bg.line.fill.background()

    # Title
    txBox = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "FL Wingmen"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.LEFT

    p2 = tf.add_paragraph()
    p2.text = f"{district} — Weekly Operations Report"
    p2.font.size = Pt(28)
    p2.font.color.rgb = RGBColor(0xFF, 0xD7, 0x00)
    p2.alignment = PP_ALIGN.LEFT

    # Summary stats
    summary_items = []

    # KDS adherence
    kds_path = DATA_DIR / "kds_dinner.csv"
    if kds_path.exists():
        kds = pd.read_csv(kds_path)
        kds["Store No"] = kds["Store No"].astype(str)
        latest_kds = sorted(kds["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
        kds_d = kds[(kds["Period"] == latest_kds) & (kds["Store No"].isin(d_stores))]
        if not kds_d.empty:
            avg_adh = kds_d["Adherence %"].mean()
            summary_items.append(f"KDS Adherence ({latest_kds}): {avg_adh:.0f}%")

    # FlavorLab
    fl_path = DATA_DIR / "flavorlab.csv"
    if fl_path.exists():
        fl = pd.read_csv(fl_path)
        fl["Store No"] = fl["Store No"].astype(str)
        fl_d = fl[fl["Store No"].isin(d_stores)]
        if not fl_d.empty:
            fl_avg = fl_d["Avg_Completion_Rate"].mean()
            summary_items.append(f"FlavorLab Completion: {fl_avg:.0f}%")

    # SMG
    smg_path = DATA_DIR / "smg_q2.csv"
    if smg_path.exists():
        smg = pd.read_csv(smg_path)
        smg["Store No"] = smg["Store No"].astype(str)
        smg_d = smg[smg["Store No"].isin(d_stores)]
        if not smg_d.empty:
            w_dissat = (smg_d["Dissatisfaction %"] * smg_d["Survey Count"]).sum() / smg_d["Survey Count"].sum()
            summary_items.append(f"SMG Dissatisfaction (Q2): {w_dissat:.2f}%")

    summary_items.append(f"Stores: {len(d_stores)}")

    txBox2 = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(11), Inches(3))
    tf2 = txBox2.text_frame
    for item in summary_items:
        p = tf2.add_paragraph()
        p.text = f"▸  {item}"
        p.font.size = Pt(18)
        p.font.color.rgb = WHITE
        p.space_after = Pt(8)

    # ════════════════════════════════════════
    # SLIDE 2: SALES PERFORMANCE
    # ════════════════════════════════════════
    sales_path = DATA_DIR / "sales_journal.csv"
    if sales_path.exists():
        sales = pd.read_csv(sales_path)
        sales["Store No"] = sales["Store No"].astype(str)
        latest_sales = sorted(sales["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
        sales_d = sales[(sales["Period"] == latest_sales) & (sales["Store No"].isin(d_stores))].copy()
        if not sales_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, f"Sales Performance — {latest_sales}", f"{district} · {len(sales_d)} stores")

            sales_d["Online %"] = (sales_d["Online Sales"] / sales_d["Gross Sales"] * 100).round(1)
            tbl = sales_d[["Store No", "Gross Sales", "Net Sales", "Online Sales", "Online %",
                           "Check Avg", "Cash Over/Short"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["Gross Sales"] = tbl["Gross Sales"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
            tbl["Net Sales"] = tbl["Net Sales"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
            tbl["Online Sales"] = tbl["Online Sales"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
            tbl["Online %"] = tbl["Online %"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
            tbl["Check Avg"] = tbl["Check Avg"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "—")
            tbl["Cash Over/Short"] = tbl["Cash Over/Short"].apply(lambda x: f"${x:+,.2f}" if pd.notna(x) else "—")
            tbl.columns = ["Store #", "Gross Sales", "Net Sales", "Online $", "Online %", "Check Avg", "Cash O/S"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), SLIDE_WIDTH - Inches(1), Inches(0.3 * (len(tbl) + 1)))

            # Callouts
            callouts = []
            raw = sales_d
            total_gross = raw["Gross Sales"].sum()
            callouts.append(f"Total gross sales: ${total_gross:,.0f}")
            cos_bad = raw[raw["Cash Over/Short"].abs() > 2]
            for _, r in cos_bad.iterrows():
                callouts.append(f"Store {r['Store No']} cash O/S: ${r['Cash Over/Short']:+,.2f} (off guide ±$2)")
            top_table_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_table_h)

    # ════════════════════════════════════════
    # SLIDE 3: KDS DASHBOARD
    # ════════════════════════════════════════
    if kds_path.exists():
        kds = pd.read_csv(kds_path)
        kds["Store No"] = kds["Store No"].astype(str)
        latest_kds = sorted(kds["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
        kds_d = kds[(kds["Period"] == latest_kds) & (kds["Store No"].isin(d_stores))].copy()
        if not kds_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, f"KDS Dashboard — {latest_kds}", f"{district} · Fri & Sat Dinner Only")

            tbl = kds_d[["Store No", "Store Name", "SOS", "Adoption %", "Make Ahead %",
                         "Waste %", "Pre-Bump %", "Adherence %"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["SOS"] = tbl["SOS"].apply(_fmt_sos)
            tbl["Adoption %"] = tbl["Adoption %"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
            tbl["Make Ahead %"] = tbl["Make Ahead %"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
            tbl["Waste %"] = tbl["Waste %"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
            tbl["Pre-Bump %"] = tbl["Pre-Bump %"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
            tbl["Adherence %"] = tbl["Adherence %"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "—")
            tbl.columns = ["Store #", "Store Name", "SOS", "Adoption %", "Make Ahead %", "Waste %", "Pre-Bump %", "Adherence %"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), SLIDE_WIDTH - Inches(1), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            raw_kds = kds_d
            slow = raw_kds[raw_kds["SOS"] > 10]
            for _, r in slow.iterrows():
                callouts.append(f"Store {r['Store No']} SOS: {_fmt_sos(r['SOS'])} (target < 10:00)")
            low_adopt = raw_kds[raw_kds["Adoption %"] < 85]
            for _, r in low_adopt.iterrows():
                callouts.append(f"Store {r['Store No']} adoption: {r['Adoption %']:.1f}% (target ≥ 85%)")
            low_adh = raw_kds[raw_kds["Adherence %"] < 85]
            for _, r in low_adh.iterrows():
                callouts.append(f"Store {r['Store No']} adherence: {r['Adherence %']:.0f}%")
            if not callouts:
                callouts.append("All stores within KDS targets ✓")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 4: SCHEDULE GUIDE
    # ════════════════════════════════════════
    sched_path = DATA_DIR / "schedule_guide.csv"
    if sched_path.exists():
        sched = pd.read_csv(sched_path)
        sched["Store No"] = sched["Store No"].astype(str)
        latest_sched = sorted(sched["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
        sched_d = sched[(sched["Period"] == latest_sched) & (sched["Store No"].isin(d_stores))].copy()
        if not sched_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, f"Schedule Guide — {latest_sched}", f"{district} · Weekly forecast & staffing")

            tbl = sched_d[["Store No", "Store Name", "Sales Forecast", "Hours Guide"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["Sales Forecast"] = tbl["Sales Forecast"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
            tbl["Hours Guide"] = tbl["Hours Guide"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")
            tbl.columns = ["Store #", "Store Name", "Sales Forecast", "Hours Guide"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), Inches(8), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            total_fc = sched_d["Sales Forecast"].sum()
            total_hrs = sched_d["Hours Guide"].sum()
            callouts.append(f"Total forecast: ${total_fc:,.0f} | Total hours: {total_hrs:,.0f}")
            top_store = sched_d.loc[sched_d["Sales Forecast"].idxmax()]
            callouts.append(f"Highest forecast: Store {top_store['Store No']} — ${top_store['Sales Forecast']:,.0f}")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts, top_h)

    # ════════════════════════════════════════
    # SLIDE 5: INTERNAL QSC EVALS
    # ════════════════════════════════════════
    qsc_path = DATA_DIR / "qsc_evals.csv"
    if qsc_path.exists():
        qsc = pd.read_csv(qsc_path)
        qsc["Store No"] = qsc["Store No"].astype(str)
        latest_qsc = sorted(qsc["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
        qsc_d = qsc[(qsc["Period"] == latest_qsc) & (qsc["Store No"].isin(d_stores))].copy()
        if not qsc_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, f"Internal QSC Evals — {latest_qsc}", f"{district} · {len(qsc_d)} evaluations")

            tbl = qsc_d[["Store No", "City", "Date", "Score", "Stars", "Rating"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["Stars"] = tbl["Stars"].apply(lambda x: f"{'★' * int(x)}" if pd.notna(x) and x > 0 else "—")
            tbl.columns = ["Store #", "City", "Date", "Findings", "Stars", "Rating"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), SLIDE_WIDTH - Inches(1), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            five_star = qsc_d[qsc_d["Stars"] == 5]
            callouts.append(f"{len(five_star)}/{len(qsc_d)} evaluations achieved 5 stars")
            below_4 = qsc_d[qsc_d["Stars"] < 4]
            for _, r in below_4.iterrows():
                callouts.append(f"Store {r['Store No']}: {int(r['Stars'])} stars — {r['Rating']}")
            if not below_4.empty:
                pass
            else:
                callouts.append("No stores below 4 stars ✓")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 6: LABOR DASHBOARD (QTD)
    # ════════════════════════════════════════
    forecast_path = DATA_DIR / "forecast.xlsm"
    if forecast_path.exists():
        raw_labor = pd.read_excel(forecast_path, sheet_name="Forecast_Data")
        r26 = raw_labor[raw_labor["year"] == 2026]
        # Current quarter
        latest_p = r26["period"].max()
        qtr_periods = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}
        current_qtr = 2
        for q, ps in qtr_periods.items():
            if latest_p in ps:
                current_qtr = q
                break
        qtr_ps = qtr_periods[current_qtr]
        labor_qtr = r26[r26["period"].isin(qtr_ps)].copy()
        labor_qtr["store_num"] = labor_qtr["store"].apply(lambda x: str(int(x.split("-")[0].strip().lstrip("0"))) if "-" in str(x) else str(x))
        labor_d = labor_qtr[labor_qtr["store_num"].isin(d_stores)]

        if not labor_d.empty:
            la = labor_d.groupby("store_num").agg(
                forecast_sales=("forecast_sales", "sum"),
                actual_sales=("actual_sales", "sum"),
                actual_labor=("actual_labor", "sum"),
                schedule_labor=("schedule_labor", "sum"),
                guide_hours=("guide_hours", "sum"),
                actual_hours=("actual_crew_hours", "sum"),
                ovt_hours=("ovt_hours", "sum"),
            ).reset_index()
            la["labor_pct"] = (la["actual_labor"] / la["actual_sales"] * 100)
            la["sched_pct"] = (la["schedule_labor"] / la["forecast_sales"] * 100)
            la["variance"] = la["labor_pct"] - la["sched_pct"]

            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, f"Labor Dashboard — Q{current_qtr} QTD", f"{district} · {len(la)} stores")

            tbl = la[["store_num", "actual_sales", "labor_pct", "sched_pct", "variance", "actual_hours", "ovt_hours"]].copy()
            tbl = tbl.sort_values("store_num", key=lambda x: x.astype(int))
            tbl["actual_sales"] = tbl["actual_sales"].apply(lambda x: f"${x:,.0f}")
            tbl["labor_pct"] = tbl["labor_pct"].apply(lambda x: f"{x:.1f}%")
            tbl["sched_pct"] = tbl["sched_pct"].apply(lambda x: f"{x:.1f}%")
            tbl["variance"] = tbl["variance"].apply(lambda x: f"{x:+.1f}%")
            tbl["actual_hours"] = tbl["actual_hours"].apply(lambda x: f"{x:,.0f}")
            tbl["ovt_hours"] = tbl["ovt_hours"].apply(lambda x: f"{x:,.1f}")
            tbl.columns = ["Store #", "Actual Sales", "Labor %", "Sched %", "Variance", "Hours", "OT Hours"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), Inches(10), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            avg_labor = la["labor_pct"].mean() if "labor_pct" in la.columns else 0
            # recalculate for raw number
            avg_labor_raw = (la["actual_labor"].sum() / la["actual_sales"].sum() * 100)
            callouts.append(f"District avg labor: {avg_labor_raw:.1f}%")
            high_var = la[la["variance"] > 1.5]
            for _, r in high_var.iterrows():
                callouts.append(f"Store {r['store_num']} variance: {r['variance']:+.1f}% (target ≤ 1.5%)")
            total_ot = la["ovt_hours"].sum()
            if total_ot > 0:
                callouts.append(f"Total overtime: {total_ot:,.1f} hours")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 7: COGS VARIANCE (QTD)
    # ════════════════════════════════════════
    cogs_path = DATA_DIR / "cogs_variance.csv"
    if cogs_path.exists():
        cogs = pd.read_csv(cogs_path)
        cogs["Store No"] = cogs["Store No"].astype(str)
        cogs["_p"] = cogs["Period"].str.extract(r"P(\d+)").astype(int)
        cogs_qtr = cogs[cogs["_p"].isin(qtr_ps)] if "qtr_ps" in dir() else cogs
        cogs_d = cogs_qtr[cogs_qtr["Store No"].isin(d_stores)]
        if not cogs_d.empty:
            cogs_avg = cogs_d.groupby(["Store No", "Store Name"]).agg(
                nbo_actual=("NBO Actual %", "mean"),
                food_theo=("Food Theoretical %", "mean"),
                cogs_actual=("COGS Actual %", "mean"),
                cogs_var=("COGS Variance %", "mean"),
            ).reset_index()

            slide = prs.slides.add_slide(blank_layout)
            cogs_periods = sorted(cogs_qtr["Period"].unique())
            _add_title_bar(slide, f"COGS Variance — {', '.join(cogs_periods)}", f"{district} · QTD")

            tbl = cogs_avg[["Store No", "Store Name", "food_theo", "cogs_actual", "cogs_var"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["food_theo"] = tbl["food_theo"].apply(lambda x: f"{x:.2f}%")
            tbl["cogs_actual"] = tbl["cogs_actual"].apply(lambda x: f"{x:.2f}%")
            tbl["cogs_var"] = tbl["cogs_var"].apply(lambda x: f"{x:+.2f}%")
            tbl.columns = ["Store #", "Store Name", "Food Theo %", "COGS Actual %", "COGS Variance %"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), Inches(9), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            avg_var = cogs_avg["cogs_var"].mean()
            callouts.append(f"District avg COGS variance: {avg_var:+.2f}%")
            high_cogs = cogs_avg[cogs_avg["cogs_var"] > 1]
            for _, r in high_cogs.iterrows():
                callouts.append(f"Store {r['Store No']}: COGS variance {r['cogs_var']:+.2f}% (target ≤ 1%)")
            if high_cogs.empty:
                callouts.append("All stores within COGS target ✓")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 8: SMG (QTD)
    # ════════════════════════════════════════
    if smg_path.exists():
        smg = pd.read_csv(smg_path)
        smg["Store No"] = smg["Store No"].astype(str)
        smg_d = smg[smg["Store No"].isin(d_stores)].copy()
        if not smg_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, "SMG — Guest Satisfaction (Q2 QTD)", f"{district} · {smg_d['Survey Count'].sum():,} surveys")

            tbl = smg_d[["Store No", "Store Name", "Survey Count", "Dissatisfaction %",
                         "Inaccurate Order %", "Greeted with Smile %"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["Dissatisfaction %"] = tbl["Dissatisfaction %"].apply(lambda x: f"{x:.2f}%")
            tbl["Inaccurate Order %"] = tbl["Inaccurate Order %"].apply(lambda x: f"{x:.2f}%")
            tbl["Greeted with Smile %"] = tbl["Greeted with Smile %"].apply(lambda x: f"{x:.1f}%")
            tbl.columns = ["Store #", "Store Name", "Surveys", "Dissat %", "Inaccurate %", "Greeted %"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), Inches(10), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            w_dissat = (smg_d["Dissatisfaction %"].astype(float) * smg_d["Survey Count"]).sum() / smg_d["Survey Count"].sum()
            callouts.append(f"District weighted dissatisfaction: {w_dissat:.2f}% (target ≤ 3%)")
            high_dissat = smg_d[smg_d["Dissatisfaction %"].astype(float) > 5]
            for _, r in high_dissat.iterrows():
                callouts.append(f"Store {r['Store No']}: {r['Dissatisfaction %']}% dissatisfaction")
            if high_dissat.empty:
                callouts.append("All stores below 5% dissatisfaction ✓")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 9: FLAVORLAB
    # ════════════════════════════════════════
    if fl_path.exists():
        fl = pd.read_csv(fl_path)
        fl["Store No"] = fl["Store No"].astype(str)
        fl_d = fl[fl["Store No"].isin(d_stores)].copy()
        if not fl_d.empty:
            slide = prs.slides.add_slide(blank_layout)
            _add_title_bar(slide, "FlavorLab — Training Completion", f"{district} · {fl_d['Employees'].sum()} employees")

            tbl = fl_d[["Store No", "Store Name", "Employees", "Total_Courses",
                        "Completions", "Incomplete", "Avg_Completion_Rate"]].copy()
            tbl = tbl.sort_values("Store No", key=lambda x: x.astype(int))
            tbl["Avg_Completion_Rate"] = tbl["Avg_Completion_Rate"].apply(lambda x: f"{x:.1f}%")
            tbl.columns = ["Store #", "Store Name", "Employees", "Courses", "Completed", "Incomplete", "Completion %"]

            _add_table(slide, tbl, Inches(0.5), Inches(1.4), Inches(10), Inches(0.3 * (len(tbl) + 1)))

            callouts = []
            avg_fl = fl_d["Avg_Completion_Rate"].mean()
            callouts.append(f"District avg completion: {avg_fl:.1f}% (target 100%)")
            low_fl = fl_d[fl_d["Avg_Completion_Rate"] < 95]
            for _, r in low_fl.iterrows():
                callouts.append(f"Store {r['Store No']}: {r['Avg_Completion_Rate']:.1f}% — {int(r['Incomplete'])} incomplete courses")
            if low_fl.empty:
                callouts.append("All stores above 95% completion ✓")
            top_h = Inches(1.4 + 0.3 * (len(tbl) + 1) + 0.2)
            _add_callouts(slide, callouts[:5], top_h)

    # ════════════════════════════════════════
    # SLIDE 10: SCORECARD (QTD ADHERENCE)
    # ════════════════════════════════════════
    # Build mini scorecard
    qsc_insp_path = DATA_DIR / "qsc_inspection.csv"

    scorecard_checks = []
    sc_data = {}

    # Gather all check data per store
    for snum in d_stores:
        checks_passed = 0
        checks_total = 0

        # KDS checks (latest week)
        if kds_path.exists():
            kds = pd.read_csv(kds_path)
            kds["Store No"] = kds["Store No"].astype(str)
            latest_kds = sorted(kds["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))[-1]
            sk = kds[(kds["Period"] == latest_kds) & (kds["Store No"] == snum)]
            if not sk.empty:
                r = sk.iloc[0]
                for val, cond in [(r.get("SOS"), lambda v: v < 10),
                                  (r.get("Adoption %"), lambda v: v >= 85),
                                  (r.get("Make Ahead %"), lambda v: v <= 10),
                                  (r.get("Pre-Bump %"), lambda v: v <= 0.5)]:
                    if pd.notna(val):
                        checks_total += 1
                        if cond(val):
                            checks_passed += 1

        # SMG
        if smg_path.exists():
            smg = pd.read_csv(smg_path)
            smg["Store No"] = smg["Store No"].astype(str)
            sk = smg[smg["Store No"] == snum]
            if not sk.empty:
                r = sk.iloc[0]
                for val, cond in [(r.get("Dissatisfaction %"), lambda v: v <= 3),
                                  (r.get("Inaccurate Order %"), lambda v: v <= 3)]:
                    if pd.notna(val):
                        checks_total += 1
                        if cond(val):
                            checks_passed += 1

        # FlavorLab
        if fl_path.exists():
            fl = pd.read_csv(fl_path)
            fl["Store No"] = fl["Store No"].astype(str)
            sk = fl[fl["Store No"] == snum]
            if not sk.empty:
                val = sk.iloc[0].get("Avg_Completion_Rate")
                if pd.notna(val):
                    checks_total += 1
                    if val >= 95:
                        checks_passed += 1

        # QSC Inspection
        if qsc_insp_path.exists():
            qi = pd.read_csv(qsc_insp_path)
            qi["Store No"] = qi["Store No"].astype(str)
            sk = qi[qi["Store No"] == snum]
            if not sk.empty:
                val = sk.iloc[0].get("QSC Stars")
                if pd.notna(val):
                    checks_total += 1
                    if val >= 5:
                        checks_passed += 1

        adh_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
        sc_data[snum] = {"passed": checks_passed, "total": checks_total, "adherence": adh_pct}

    if sc_data:
        slide = prs.slides.add_slide(blank_layout)
        _add_title_bar(slide, "Scorecard — Q2 QTD Adherence", f"{district} · {len(sc_data)} stores")

        sc_rows = []
        for snum in sorted(sc_data.keys(), key=int):
            d = sc_data[snum]
            sc_rows.append({
                "Store #": snum,
                "Passed": f"{d['passed']}/{d['total']}",
                "Adherence %": f"{d['adherence']:.0f}%",
            })
        sc_tbl = pd.DataFrame(sc_rows)
        _add_table(slide, sc_tbl, Inches(0.5), Inches(1.4), Inches(5), Inches(0.3 * (len(sc_tbl) + 1)))

        callouts = []
        avg_sc = sum(d["adherence"] for d in sc_data.values()) / len(sc_data)
        callouts.append(f"District avg adherence: {avg_sc:.0f}%")
        low_sc = {s: d for s, d in sc_data.items() if d["adherence"] < 70}
        for s, d in sorted(low_sc.items(), key=lambda x: x[1]["adherence"]):
            callouts.append(f"Store {s}: {d['adherence']:.0f}% ({d['passed']}/{d['total']} checks)")
        if not low_sc:
            callouts.append("All stores above 70% adherence ✓")
        top_h = Inches(1.4 + 0.3 * (len(sc_tbl) + 1) + 0.2)
        _add_callouts(slide, callouts[:5], top_h)

    # ── Save to bytes ──
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.getvalue()
