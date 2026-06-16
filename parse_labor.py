"""
Rebuild data/forecast.xlsm (Forecast_Data) from an "Actual vs Forecast*.xlsm" export.

The export's Forecast_Data sheet is the authoritative master (all history + new
weeks, with actuals that finalize over time). In-progress weeks are dropped so a
partially-elapsed week doesn't distort labor % — a week is considered incomplete
when its total actual sales are under 50% of total forecast sales.

Usage:
  python parse_labor.py [path_to_export.xlsm]
  (no arg -> newest "Actual vs Forecast*.xlsm" in Downloads)
"""
import sys
import os
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
INCOMPLETE_RATIO = 0.5

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    cands = sorted(Path(r'C:\Users\sorja\Downloads').glob('Actual vs Forecast*.xls*'), key=os.path.getmtime)
    if not cands:
        raise SystemExit('No "Actual vs Forecast*.xlsm" found in Downloads')
    src = str(cands[-1])
print(f'Source: {src}')

df = pd.read_excel(src, sheet_name='Forecast_Data')

# Drop in-progress weeks (week-level actual sales < 50% of forecast)
wk = df.groupby('week_d').agg(a=('actual_sales', 'sum'), f=('forecast_sales', 'sum'))
ratio = wk['a'] / wk['f']
incomplete = sorted(ratio[ratio < INCOMPLETE_RATIO].index.tolist())
if incomplete:
    print(f'Dropping incomplete week(s) (actuals < {INCOMPLETE_RATIO:.0%} of forecast): {incomplete}')
    df = df[~df['week_d'].isin(incomplete)].copy()

out = HERE / 'data' / 'forecast.xlsm'
with pd.ExcelWriter(out, engine='openpyxl') as w:
    df.to_excel(w, sheet_name='Forecast_Data', index=False)

weeks_2026 = sorted(df[df['year'] == 2026]['week_d'].unique())
print(f'Wrote {len(df)} rows to {out}')
print(f'2026 weeks: {weeks_2026[0]} .. {weeks_2026[-1]} ({len(weeks_2026)} weeks)')
