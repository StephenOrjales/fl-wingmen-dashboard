"""
Regenerate SMG per-quarter CSVs from an SMG "ComparisonReport" export.

The report has two date-range columns per metric (a "current" range and a
comparison range), each as [Score, n]. Newer exports put the *current*
quarter first and a *custom* prior-quarter range second, e.g.:
  current = 6/28/2026-9/26/2026 (Q3),  custom = 3/29/2026-6/27/2026 (Q2).

This parser reads the date-range header row and maps each recognized range
to its quarter file, so each quarter is saved from the correct columns
regardless of position. Only stores with data for that quarter are written
(stores showing "**" for a quarter are skipped).

Metric blocks (first column of each [Score, n, Score, n, Difference] group):
  Dissatisfaction = col 2, What Went Wrong-Accurate = col 7, Greeted = col 12.
Survey Count for a quarter = the n beside that quarter's Dissatisfaction score.

Usage:
  python parse_smg.py [path_to_ComparisonReport.csv]
  (no arg -> newest ComparisonReport*.csv in Downloads)
"""
import sys
import os
import re
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent

# Recognized quarter date ranges -> output file
QUARTER_FILES = {
    "12/28/2025 - 3/28/2026": "smg_q1.csv",
    "3/29/2026 - 6/27/2026": "smg_q2.csv",
    "6/28/2026 - 9/26/2026": "smg_q3.csv",
}
BLOCKS = {"dissat": 2, "inacc": 7, "greet": 12}  # first column of each metric group

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    cands = sorted(Path(r'C:\Users\sorja\Downloads').glob('ComparisonReport*.csv'), key=os.path.getmtime)
    if not cands:
        raise SystemExit('No ComparisonReport*.csv found in Downloads')
    src = str(cands[-1])
print(f'Source: {src}')

raw = pd.read_csv(src, header=None, dtype=str)


def canon(s):
    """Canonicalize a date-range string: ' - ' separator, single spaces, plain hyphen."""
    s = str(s).strip().replace('–', '-').replace('—', '-')
    s = re.sub(r'\s*-\s*', ' - ', s)
    return re.sub(r'\s+', ' ', s)


def pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.split(r'\s', str(v).strip())[0].replace('%', '')
    try:
        return float(s)
    except ValueError:
        return None


# Find the date-range header row (contains "M/D/YYYY - M/D/YYYY" cells)
date_row = None
for i in range(min(8, len(raw))):
    vals = [canon(x) for x in raw.iloc[i].tolist()]
    if any(re.match(r'\d+/\d+/\d+ - \d+/\d+/\d+', v) for v in vals):
        date_row = [canon(x) for x in raw.iloc[i].tolist()]
        break
if date_row is None:
    raise SystemExit('Could not find the date-range header row in the report.')

QUARTER_FILES_C = {canon(k): v for k, v in QUARTER_FILES.items()}


def col_for(block_start, target):
    """Within a metric block, return the Score-column index whose header == target range."""
    for c in (block_start, block_start + 2):
        if c < len(date_row) and date_row[c] == target:
            return c
    return None


store_re = re.compile(r'^\s*(\d+)\s*-\s*FL-(.+)$')
written = []
for target, outfile in QUARTER_FILES_C.items():
    dcol = col_for(BLOCKS["dissat"], target)
    if dcol is None:
        continue  # this quarter isn't in the report
    icol = col_for(BLOCKS["inacc"], target)
    gcol = col_for(BLOCKS["greet"], target)
    ncol = dcol + 1  # survey count sits beside the dissatisfaction score

    rows = []
    for _, r in raw.iterrows():
        m = store_re.match(str(r[0]).strip())
        if not m:
            continue  # skip Combined / headers / metadata
        dis = pct(r[dcol])
        cnt_raw = str(r[ncol]).strip()
        if dis is None or cnt_raw in ('**', '', 'nan'):
            continue  # no data for this quarter at this store
        try:
            cnt = int(float(cnt_raw.replace(',', '')))
        except ValueError:
            continue
        rows.append({
            'Store No': int(m.group(1)),
            'Store Name': m.group(2).strip(),
            'Survey Count': cnt,
            'Dissatisfaction %': dis,
            'Inaccurate Order %': pct(r[icol]),
            'Greeted with Smile %': pct(r[gcol]),
        })

    df = pd.DataFrame(rows).sort_values('Store No').reset_index(drop=True)
    out = HERE / 'data' / outfile
    df.to_csv(out, index=False)
    total = df['Survey Count'].sum()
    wd = (df['Dissatisfaction %'] * df['Survey Count']).sum() / total if total else 0
    print(f'{outfile}: {len(df)} stores | {total:,} surveys | weighted dissat {wd:.2f}%')
    written.append(outfile)

if not written:
    print('No recognized quarter date ranges found in the report.')
