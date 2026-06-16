"""
Parse Zenput submission exports into compact per-store-per-day report-count
grids for the dashboard "Zenput" tab. Handles multiple Zenput tasks.

Each report -> data/<out>.csv with columns: Store No, Date, Reports
(every config store x every day in the window; 0 where nothing filed).

Window: the 30 full days ending the day BEFORE the export's last calendar
date (the export day is a same-day partial pull and is excluded).

Cadence (3 logs/day vs 1 check/day) is applied in the dashboard, not here —
the grid is just raw daily counts.

Usage:
  python parse_zenput.py            # regenerate every report from newest export in Downloads
  python parse_zenput.py <file>     # use this file for whichever report its name matches
"""
import sys
import os
import json
import fnmatch
import pandas as pd
from pathlib import Path
from datetime import timedelta

HERE = Path(__file__).parent
DOWNLOADS = Path(r'C:\Users\sorja\Downloads')
WINDOW_DAYS = 30


def _store_from_location(df):
    # Time/Temp export: store number is the "Location" column (e.g. 1771)
    return df['Location'].astype(str).str.strip().str.lstrip('0')


def _store_from_submitted_by(df):
    # Morning checklist export: store is in "Submitted By" as "Store 1677"
    return df['Submitted By'].astype(str).str.extract(r'(\d+)')[0].str.lstrip('0')


REPORTS = [
    {'name': 'Time/Temp Logs',
     'glob': 'TimeTemperature_Log_Submissions-*.xlsx',
     'cols': ['Location', 'Date Submitted'], 'store_fn': _store_from_location,
     'out': 'zenput_daily.csv'},
    {'name': 'Morning Manager Checklist',
     'glob': 'Daily_Morning_Manager_Checklist_Submissions-*.xlsx',
     'cols': ['Submitted By', 'Date Submitted'], 'store_fn': _store_from_submitted_by,
     'out': 'zenput_morning_daily.csv'},
]

# Franchise store list (so a store with ZERO submissions still shows 0%)
cfg = json.loads((HERE / 'config.json').read_text())
stores = sorted({s.split(' - ')[0].strip().lstrip('0')
                 for sl in cfg['stores'].values() for s in sl}, key=int)

explicit = sys.argv[1] if len(sys.argv) > 1 else None


def build(report, src):
    df = pd.read_excel(src, sheet_name='Submissions', usecols=report['cols'])
    df['Store No'] = report['store_fn'](df)
    df = df[df['Store No'].notna() & df['Store No'].isin(stores)]
    df['ts'] = pd.to_datetime(df['Date Submitted'], errors='coerce')
    df = df.dropna(subset=['ts'])
    df['date'] = df['ts'].dt.normalize()

    max_date = df['date'].max()
    window_end = max_date - timedelta(days=1)
    window_start = window_end - timedelta(days=WINDOW_DAYS - 1)
    dates = pd.date_range(window_start, window_end, freq='D')
    win = df[(df['date'] >= window_start) & (df['date'] <= window_end)]

    counts = win.groupby(['Store No', 'date']).size().rename('Reports').reset_index()
    grid = pd.MultiIndex.from_product([stores, dates], names=['Store No', 'date']).to_frame(index=False)
    grid = grid.merge(counts, on=['Store No', 'date'], how='left')
    grid['Reports'] = grid['Reports'].fillna(0).astype(int)
    grid['Date'] = grid['date'].dt.strftime('%Y-%m-%d')
    grid = grid[['Store No', 'Date', 'Reports']].sort_values(['Store No', 'Date'])
    grid.to_csv(HERE / 'data' / report['out'], index=False)
    return grid, dates, len(win)


for report in REPORTS:
    if explicit and fnmatch.fnmatch(Path(explicit).name, report['glob']):
        src = explicit
    else:
        cands = sorted(DOWNLOADS.glob(report['glob']), key=os.path.getmtime)
        if not cands:
            print(f"[skip] {report['name']}: no matching export in Downloads")
            continue
        src = str(cands[-1])

    grid, dates, n_win = build(report, src)
    zero_stores = sorted(grid.groupby('Store No')['Reports'].sum().loc[lambda s: s == 0].index, key=int)
    print(f"{report['name']}  <-  {Path(src).name}")
    print(f"  window {dates[0].date()}..{dates[-1].date()} ({len(dates)}d) | "
          f"{n_win} submissions | stores with ZERO: {zero_stores or 'none'}")
