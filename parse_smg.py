"""
Regenerate data/smg_q2.csv from an SMG "ComparisonReport" export.

Only the CURRENT-period columns are used — last-year and difference columns
are intentionally ignored. Column layout (0-indexed) in the source:
  0 Store   1 Count
  2 Dissatisfaction(Current Score)   7 What Went Wrong-Accurate(Current Score)
  12 Greeted with a smile(Current Score)

Usage:
  python parse_smg.py [path_to_ComparisonReport.csv]
  (no arg -> newest ComparisonReport*.csv in Downloads)
"""
import sys
import os
import re
import pandas as pd
from pathlib import Path

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    cands = sorted(Path(r'C:\Users\sorja\Downloads').glob('ComparisonReport*.csv'), key=os.path.getmtime)
    if not cands:
        raise SystemExit('No ComparisonReport*.csv found in Downloads')
    src = str(cands[-1])
print(f'Source: {src}')

raw = pd.read_csv(src, header=None, dtype=str)


def pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.split(r'\s', str(v).strip())[0].replace('%', '')
    try:
        return float(s)
    except ValueError:
        return None


store_re = re.compile(r'^\s*(\d+)\s*-\s*FL-(.+)$')
rows = []
for _, r in raw.iterrows():
    c0 = str(r[0]).strip() if pd.notna(r[0]) else ''
    m = store_re.match(c0)
    if not m:
        continue  # skips Combined row, headers, metadata
    try:
        count = int(float(str(r[1]).replace(',', '')))
    except (ValueError, TypeError):
        count = None
    rows.append({
        'Store No': int(m.group(1)),
        'Store Name': m.group(2).strip(),
        'Survey Count': count,
        'Dissatisfaction %': pct(r[2]),
        'Inaccurate Order %': pct(r[7]),
        'Greeted with Smile %': pct(r[12]),
    })

out_df = pd.DataFrame(rows).sort_values('Store No').reset_index(drop=True)
out = Path(__file__).parent / 'data' / 'smg_q2.csv'
out_df.to_csv(out, index=False)
print(f'Wrote {len(out_df)} stores | {out_df["Survey Count"].sum():,} surveys')
wd = (out_df['Dissatisfaction %'] * out_df['Survey Count']).sum() / out_df['Survey Count'].sum()
print(f'Weighted dissatisfaction: {wd:.2f}%')
