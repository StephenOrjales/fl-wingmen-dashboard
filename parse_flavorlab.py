"""
Regenerate data/flavorlab.csv from a FlavorLab "Courses Count Per User Report" export.

Methodology (must stay consistent run-to-run):
  - One row per employee; above-store staff (blank Stores) are dropped.
  - Multi-store managers are assigned to their FIRST listed store.
  - Avg_Completion_Rate = mean of each employee's own completion rate (NOT weighted).
  - Incomplete = sum(Total Courses) - sum(Completions).

Usage:
  python parse_flavorlab.py [path_to_export.csv]
  (no arg -> newest Courses_Count_Per_User_Report_*.csv in Downloads)
"""
import sys
import os
import re
import pandas as pd
from pathlib import Path

if len(sys.argv) > 1:
    src = sys.argv[1]
else:
    cands = sorted(Path(r'C:\Users\sorja\Downloads').glob('Courses_Count_Per_User_Report_*.csv'),
                   key=os.path.getmtime)
    if not cands:
        raise SystemExit('No Courses_Count_Per_User_Report_*.csv found in Downloads')
    src = str(cands[-1])
print(f'Source: {src}')

df = pd.read_csv(src, skiprows=7)

# Drop above-store employees (blank Stores)
df = df[df['Stores'].notna() & (df['Stores'].astype(str).str.strip() != '')].copy()

# First store for multi-store employees
df['first_store'] = df['Stores'].astype(str).str.split(',').str[0].str.strip()


def parse_num(s):
    m = re.match(r'0*(\d+)', s)
    return m.group(1) if m else None


def parse_name(s):
    parts = s.split(' - ', 1)
    nm = parts[1].strip() if len(parts) == 2 else s
    nm = re.sub(r'^FL-', '', nm)
    return nm[:30]


df['Store No'] = df['first_store'].apply(parse_num)
df['Store Name'] = df['first_store'].apply(parse_name)
df = df[df['Store No'].notna()]

df['Completion Rate'] = pd.to_numeric(df['Completion Rate'], errors='coerce')
df['Total Courses'] = pd.to_numeric(df['Total Courses'], errors='coerce')
df['Completions'] = pd.to_numeric(df['Completions'], errors='coerce')
# Source occasionally credits an employee with more completions than assigned courses
# (retired/reassigned courses). Cap per-employee so store Incomplete can't go negative.
df['Completions'] = df[['Completions', 'Total Courses']].min(axis=1)

agg = df.groupby('Store No').agg(
    Store_Name=('Store Name', 'first'),
    Employees=('Completion Rate', 'count'),
    Total_Courses=('Total Courses', 'sum'),
    Completions=('Completions', 'sum'),
    Avg_Completion_Rate=('Completion Rate', 'mean'),
).reset_index()

agg['Incomplete'] = (agg['Total_Courses'] - agg['Completions']).astype(int)
agg['Avg_Completion_Rate'] = agg['Avg_Completion_Rate'].round(1)
agg['Total_Courses'] = agg['Total_Courses'].astype(int)
agg['Completions'] = agg['Completions'].astype(int)
agg = agg.rename(columns={'Store_Name': 'Store Name'})
agg = agg[['Store No', 'Store Name', 'Employees', 'Total_Courses', 'Completions',
           'Avg_Completion_Rate', 'Incomplete']]
agg['_s'] = agg['Store No'].astype(int)
agg = agg.sort_values('_s').drop(columns='_s').reset_index(drop=True)

out = Path(__file__).parent / 'data' / 'flavorlab.csv'
agg.to_csv(out, index=False)
print(f'Wrote {len(agg)} stores | {agg["Employees"].sum()} employees | '
      f'fleet avg {agg["Avg_Completion_Rate"].mean():.1f}%')
print(f'Stores < 95%: {sorted(agg[agg["Avg_Completion_Rate"] < 95]["Store No"].astype(int).tolist())}')
