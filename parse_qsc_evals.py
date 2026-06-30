import pandas as pd
import re
from pathlib import Path

eval_dir = Path(r'C:\Users\sorja\flwingmen.com\Daymara Vidaurre - Quality Control and Evaluations\RSM Reporting\Internal QSC Eval\Q2 2026')

def _period_key(name):
    """(period, week) tuple from a filename, or None."""
    m = re.search(r'P(\d)W(\d)', name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _has_district_overview(path):
    try:
        return 'District Overview' in pd.ExcelFile(path).sheet_names
    except Exception:
        return False


files = sorted(eval_dir.glob('Evaluations *.xlsx'))
# Also pick up newer eval weeks sitting in Downloads that haven't been filed into the
# quarter folder yet. Only weeks LATER than the folder's latest (so we don't pull in
# prior-quarter files that live elsewhere), and only files that are real QSC overviews.
folder_keys = [_period_key(f.name) for f in files if _period_key(f.name)]
latest_folder = max(folder_keys) if folder_keys else (0, 0)
downloads_dir = Path(r'C:\Users\sorja\Downloads')
have_keys = set(folder_keys)
for f in downloads_dir.glob('Evaluations *.xlsx'):
    k = _period_key(f.name)
    if k and k > latest_folder and k not in have_keys and _has_district_overview(f):
        files.append(f)
        have_keys.add(k)
files = sorted(files, key=lambda f: _period_key(f.name) or (99, 99))
_found_periods = [f"P{_period_key(f.name)[0]}W{_period_key(f.name)[1]}" for f in files if _period_key(f.name)]
print(f'Found {len(files)} eval files: {_found_periods}')

all_rows = []
for f in files:
    # Extract period from filename like "Evaluations P5W3 5.10.26 - 5.16.26.xlsx"
    fname = f.stem
    m = re.search(r'(P\dW\d)', fname)
    period = m.group(1) if m else fname

    # Extract date range
    dm = re.search(r'(\d+\.\d+\.\d+)\s*-\s*(\d+\.\d+\.\d+)', fname)
    if dm:
        start_date = dm.group(1).replace('.', '/')
        end_date = dm.group(2).replace('.', '/')
    else:
        start_date = end_date = ''

    df = pd.read_excel(f, sheet_name='District Overview', header=None)
    # Row 0 is headers: Store #, City, Address, Date, MOD, # Findings, Score, Rating, Duration, Leave Behind Report

    current_district = ''
    district_status = ''
    for idx, row in df.iterrows():
        if idx == 0:
            continue  # skip header

        val0 = str(row[0]).strip() if pd.notna(row[0]) else ''

        # District header row like "DISTRICT 1  —  6/6 stores completed"
        if val0.startswith('DISTRICT'):
            current_district = re.match(r'(DISTRICT \d+)', val0).group(1) if re.match(r'(DISTRICT \d+)', val0) else val0
            # Extract completion status
            cm = re.search(r'(\d+/\d+)\s+stores\s+completed', val0)
            district_status = cm.group(1) if cm else ''
            continue

        # Store row
        try:
            store_no = int(float(val0))
        except (ValueError, TypeError):
            continue

        city = str(row[1]).strip() if pd.notna(row[1]) else ''
        address = str(row[2]).strip() if pd.notna(row[2]) else ''
        date_val = row[3]
        mod_val = str(row[4]).strip() if pd.notna(row[4]) else ''

        # Skip RSM-completed evals (shown in green, marked "(RSM SO)" by the name).
        # These are RSM assessments, not the GM internal self-assessment we track.
        if 'RSM' in mod_val.upper():
            continue

        # Check for NO EVALUATION COMPLETED - also catch blank rows with no date/score/rating
        no_eval = ('NO EVALUATION' in mod_val.upper()
                   or (pd.isna(row[3]) and pd.isna(row[5]) and pd.isna(row[6])))

        findings = row[5] if pd.notna(row[5]) else None
        score = row[6] if pd.notna(row[6]) else None
        rating = str(row[7]).strip() if pd.notna(row[7]) else ''
        duration = str(row[8]).strip() if pd.notna(row[8]) else ''

        # Parse duration to minutes
        dur_minutes = None
        if duration and duration != 'nan':
            hm = re.match(r'(\d+)h\s*(\d+)m', duration)
            mm = re.match(r'(\d+)\s*min', duration)
            if hm:
                dur_minutes = int(hm.group(1)) * 60 + int(hm.group(2))
            elif mm:
                dur_minutes = int(mm.group(1))

        # Determine star rating
        stars = 0
        if '5 Stars' in rating:
            stars = 5
        elif '4 Stars' in rating:
            stars = 4
        elif '3 Stars' in rating:
            stars = 3
        elif '2 Stars' in rating:
            stars = 2
        elif '1 Star' in rating:
            stars = 1

        # Flag: red = score 0 OR duration < 60 min (not taking it seriously)
        is_red = False
        if not no_eval:
            if score is not None and float(score) == 0:
                is_red = True
            if dur_minutes is not None and dur_minutes < 60:
                is_red = True

        all_rows.append({
            'Period': period,
            'Start Date': start_date,
            'End Date': end_date,
            'District': current_district,
            'Store No': store_no,
            'City': city,
            'Date': str(date_val)[:10] if pd.notna(date_val) else '',
            'MOD': mod_val if not no_eval else '',
            'Findings': int(findings) if pd.notna(findings) else None,
            'Score': int(float(score)) if pd.notna(score) else None,
            'Rating': rating,
            'Stars': stars,
            'Duration': duration,
            'Duration Min': dur_minutes,
            'No Eval': no_eval,
            'Red Flag': is_red,
        })

df = pd.DataFrame(all_rows)

# One eval per store per week: keep the latest dated eval; if a store has only
# blank/No-Eval rows, keep one. (Handles red duplicates like 2042's repeated entries.)
df['_dt'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.sort_values(['Period', 'Store No', '_dt'], na_position='first')
df = (df.groupby(['Period', 'Store No'], as_index=False, sort=False)
        .tail(1).drop(columns='_dt').reset_index(drop=True))

print(f'Total rows: {len(df)}')
print(f'Periods: {df["Period"].unique().tolist()}')
print(f'No Eval count: {df["No Eval"].sum()}')
print(f'Red Flag count: {df["Red Flag"].sum()}')
print(f'\nStores with NO EVAL:')
print(df[df['No Eval']][['Period','Store No','District']].to_string(index=False))
print(f'\nRed Flag stores (score=0 or <1hr):')
red = df[df['Red Flag']][['Period','Store No','Score','Duration','Duration Min']].copy()
print(red.to_string(index=False))

out = Path(r'C:\Users\sorja\Downloads\Wingstop Data\data\qsc_evals.csv')
df.to_csv(out, index=False)
print(f'\nSaved to {out}')
