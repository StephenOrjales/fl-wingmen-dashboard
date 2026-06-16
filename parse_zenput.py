"""
Parse a Zenput Time/Temperature Log Submissions export into a compact
per-store-per-day report-count grid for the dashboard "Zenput" tab.

Standard cadence: 3 reports per store per day.
Window: the 30 full days ending the day BEFORE the export's last calendar
date. The export day itself is a same-morning partial pull (only the opening
report is in by export time), so it is excluded.

Output: data/zenput_daily.csv  ->  Store No, Date, Reports
        (every config store x every day in the window; 0 where nothing filed)

Usage:
  python parse_zenput.py [path_to_export.xlsx]
  (no arg -> newest TimeTemperature_Log_Submissions-*.xlsx in Downloads)
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import timedelta

HERE = Path(__file__).parent
EXPECTED_PER_DAY = 3
WINDOW_DAYS = 30

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    cands = sorted(Path(r'C:\Users\sorja\Downloads').glob('TimeTemperature_Log_Submissions-*.xlsx'),
                   key=os.path.getmtime)
    if not cands:
        raise SystemExit('No TimeTemperature_Log_Submissions-*.xlsx found in Downloads')
    src = str(cands[-1])
print(f'Source: {src}')

# Franchise store list from config (so a store with ZERO submissions still shows 0%)
cfg = json.loads((HERE / 'config.json').read_text())
stores = sorted({s.split(' - ')[0].strip().lstrip('0')
                 for sl in cfg['stores'].values() for s in sl}, key=int)

df = pd.read_excel(src, sheet_name='Submissions', usecols=['Location', 'Date Submitted'])
df['Store No'] = df['Location'].astype(str).str.strip().str.lstrip('0')
df['ts'] = pd.to_datetime(df['Date Submitted'], errors='coerce')
df = df.dropna(subset=['ts'])
df['date'] = df['ts'].dt.normalize()

# Window: drop the last (partial) calendar day, then 30 days ending the day before
max_date = df['date'].max()
window_end = max_date - timedelta(days=1)
window_start = window_end - timedelta(days=WINDOW_DAYS - 1)
dates = pd.date_range(window_start, window_end, freq='D')
win = df[(df['date'] >= window_start) & (df['date'] <= window_end)]

# Per-store-per-day submission counts, expanded to the full store x date grid (0 where none)
counts = win.groupby(['Store No', 'date']).size().rename('Reports').reset_index()
grid = pd.MultiIndex.from_product([stores, dates], names=['Store No', 'date']).to_frame(index=False)
grid = grid.merge(counts, on=['Store No', 'date'], how='left')
grid['Reports'] = grid['Reports'].fillna(0).astype(int)
grid['Date'] = grid['date'].dt.strftime('%Y-%m-%d')
grid = grid[['Store No', 'Date', 'Reports']].sort_values(['Store No', 'Date'])

out = HERE / 'data' / 'zenput_daily.csv'
grid.to_csv(out, index=False)

# Summary (completion = reports done, capped at 3/day, / expected)
expected_total = WINDOW_DAYS * EXPECTED_PER_DAY
capped = grid.copy()
capped['capped'] = capped['Reports'].clip(upper=EXPECTED_PER_DAY)
per_store_capped = capped.groupby('Store No')['capped'].sum()
completion = (per_store_capped / expected_total * 100).round(1)
missing_days = grid[grid['Reports'] < EXPECTED_PER_DAY].groupby('Store No').size()

print(f'Window: {window_start.date()} .. {window_end.date()} ({len(dates)} days) | '
      f'expected {expected_total} reports/store')
print(f'Stores: {len(stores)} | grid rows: {len(grid)} | total reports in window: {int(win.shape[0])}')
print(f'Fleet completion: {completion.mean():.1f}%')
print('Lowest 5 stores (completion %):')
print(completion.sort_values().head(5).to_string())
print('Most missing days (store: # days under 3):')
print(missing_days.sort_values(ascending=False).head(5).to_string())
