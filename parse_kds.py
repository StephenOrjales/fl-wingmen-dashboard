import pandas as pd
import re
from pathlib import Path

kds_dir = Path(r'C:\Users\sorja\flwingmen.com\Daymara Vidaurre - Quality Control and Evaluations\Smart Kitchen Performance (KDS)\Weekly Reports')

files = sorted(kds_dir.glob('Weekly KDS P*W* Friday.Saturday.Dinner.xlsx'))
# Also check Downloads for any KDS files not in the SharePoint folder
downloads_dir = Path(r'C:\Users\sorja\Downloads')
for f in downloads_dir.glob('Weekly KDS P*W* Friday.Saturday.Dinner.xlsx'):
    # Only add if this period isn't already covered
    period_m = re.search(r'(P\dW\d)', f.name)
    if period_m:
        existing_periods = {re.search(r'(P\dW\d)', ef.name).group(1) for ef in files if re.search(r'(P\dW\d)', ef.name)}
        if period_m.group(1) not in existing_periods:
            files.append(f)
files = sorted(files, key=lambda f: f.name)
print(f'Found {len(files)} KDS files')


def parse_time(t):
    """Convert HH:MM or MM:SS string to minutes."""
    if pd.isna(t) or t == '-':
        return None
    s = str(t).strip()
    m = re.match(r'(\d+):(\d+)', s)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    return None


def parse_pct(v):
    """Convert decimal (0.85) or percentage string to float percent."""
    if pd.isna(v):
        return None
    try:
        val = float(v)
        if val <= 1.5:  # it's a decimal like 0.85 = 85%
            return val * 100
        return val
    except (ValueError, TypeError):
        return None


all_rows = []
for f in files:
    p = Path(f)
    # Extract period from filename: "Weekly KDS P6W1 Friday..."
    m = re.search(r'(P\dW\d)', p.name)
    period = m.group(1) if m else p.stem

    xl = pd.ExcelFile(f)
    sheet = xl.sheet_names[0]
    df = pd.read_excel(f, sheet_name=sheet, header=None, skiprows=2)
    df.columns = [str(c).strip() for c in df.iloc[0]]
    df = df.iloc[1:].reset_index(drop=True)
    # Drop columns that are all NaN or named 'nan'
    df = df.loc[:, [str(c).strip().lower() != 'nan' for c in df.columns]]
    df.columns = [str(c).strip() for c in df.columns]
    print(f'  {period}: columns = {list(df.columns[:4])}')
    # Find the store name column
    store_col = None
    for c in df.columns:
        if 'store' in c.lower():
            store_col = c
            break
    if store_col is None:
        store_col = df.columns[0]
    if store_col != 'Store Full Name':
        df = df.rename(columns={store_col: 'Store Full Name'})
    df = df.dropna(subset=['Store Full Name'])
    # Also drop rows where store name doesn't look like a store
    df = df[df['Store Full Name'].astype(str).str.match(r'^\d')]

    for _, row in df.iterrows():
        store = str(row['Store Full Name']).strip()
        store_num = re.match(r'(\d+)', store)
        store_num = store_num.group(1).lstrip('0') if store_num else ''
        # Extract short name: "1252-FL-Fort Lauderdale-W. Broward Blvd." -> "Fort Lauderdale-W. Broward Blvd."
        parts = store.split('-', 2)
        short = parts[2].strip()[:30] if len(parts) >= 3 else store[:30]

        sos = parse_time(row.get('SOS'))
        pre_bump = parse_pct(row.get('Pre-Bump Rate'))
        adoption = parse_pct(row.get('Bone-in Cook Adoption'))
        make_ahead = parse_pct(row.get('Make Ahead Rate(Bone-in)'))
        waste = parse_pct(row.get('Bone-in Waste'))

        # Adherence checks (pass/fail for each metric)
        checks = {}
        if sos is not None:
            checks['SOS < 10 min'] = sos < 10
        if adoption is not None:
            checks['Adoption >= 85%'] = adoption >= 85
        if make_ahead is not None:
            checks['Make Ahead <= 10%'] = make_ahead <= 10
        if waste is not None:
            checks['Waste <= 5%'] = waste <= 5
        if pre_bump is not None:
            checks['Pre-Bump <= 1.5%'] = pre_bump <= 1.5

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        adherence = (passed / total * 100) if total > 0 else None

        all_rows.append({
            'Period': period,
            'Store No': store_num,
            'Store Name': short,
            'Store Full': store,
            'SOS': sos,
            'Pre-Bump %': pre_bump,
            'Adoption %': adoption,
            'Make Ahead %': make_ahead,
            'Waste %': waste,
            'Checks Passed': passed,
            'Checks Total': total,
            'Adherence %': adherence,
            'SOS Pass': checks.get('SOS < 10 min'),
            'Adoption Pass': checks.get('Adoption >= 85%'),
            'Make Ahead Pass': checks.get('Make Ahead <= 10%'),
            'Waste Pass': checks.get('Waste <= 5%'),
            'Pre-Bump Pass': checks.get('Pre-Bump <= 1.5%'),
        })

result = pd.DataFrame(all_rows)
# Sort periods chronologically
result['_sort'] = result['Period'].apply(lambda x: (int(x[1]), int(x[3])))
result = result.sort_values(['_sort', 'Store No']).drop('_sort', axis=1)

print(f'Total rows: {len(result)}')
print(f'Periods: {sorted(result["Period"].unique(), key=lambda x: (int(x[1]), int(x[3])))}')
print(f'Stores per period:')
print(result.groupby('Period')['Store No'].count().sort_index())
print(f'\nAdherence stats:')
print(f'  Mean: {result["Adherence %"].mean():.1f}%')
print(f'  Min:  {result["Adherence %"].min():.1f}%')
print(f'  Max:  {result["Adherence %"].max():.1f}%')
print(f'\nBottom 10 stores (avg adherence):')
avg = result.groupby(['Store No', 'Store Name'])['Adherence %'].mean().sort_values()
print(avg.head(10).to_string())

out = Path(r'C:\Users\sorja\Downloads\Wingstop Data\data\kds_dinner.csv')
result.to_csv(out, index=False)
print(f'\nSaved to {out}')
