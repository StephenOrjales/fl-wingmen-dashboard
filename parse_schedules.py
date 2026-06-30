import pdfplumber, pandas as pd, re

_sched_dir = r'C:\Users\sorja\flwingmen.com\Daymara Vidaurre - Quality Control and Evaluations\RSM Reporting\Schedule Guide\2026'
files = {
    'P5W2': r'C:\Users\sorja\Downloads\P5W2_2026.pdf',
    'P5W3': r'C:\Users\sorja\Downloads\P5W3_2026.pdf',
    'P5W4': r'C:\Users\sorja\Downloads\P5W4_2026.pdf',
    'P6W1': _sched_dir + r'\P6W1_2026.pdf',
    'P6W2': r'C:\Users\sorja\Downloads\P6W2_2026.pdf',
    'P6W4': _sched_dir + r'\P6W4_2026.pdf',
    'P6W5': _sched_dir + r'\P6W5_2026.pdf',
    'P7W1': _sched_dir + r'\P7W1_2026.pdf',
    'P7W2': _sched_dir + r'\P7W2_2026.pdf',
}

all_rows = []
for period, f in files.items():
    with pdfplumber.open(f) as pdf:
        text = pdf.pages[0].extract_text()
    lines = text.split('\n')
    start_date = end_date = ''
    current_district = ''
    for line in lines:
        if line.startswith('Start Date'):
            start_date = line.split()[-1]
        elif line.startswith('End Date'):
            end_date = line.split()[-1]
        elif line.startswith('District') and 'SubTotal' not in line and 'Store' not in line:
            current_district = line.strip()
        elif line.startswith('Store #') or line.startswith('TOTAL') or line.startswith('*'):
            continue
        elif 'SubTotal' in line:
            continue
        else:
            # store line: 346 Miami Old Cutler Road $27,886) (370)
            m = re.match(r'^(\d+)\s+(.+?)\s+\$([0-9,]+)\)\s+\(?([0-9,]+)\)?', line)
            if m:
                store_no = m.group(1)
                name = m.group(2).strip()
                sales = m.group(3).replace(',', '')
                hours = m.group(4).replace(',', '')
                all_rows.append({
                    'Period': period,
                    'Start Date': start_date,
                    'End Date': end_date,
                    'District': current_district,
                    'Store No': int(store_no),
                    'Store Name': name,
                    'Sales Forecast': int(sales),
                    'Hours Guide': int(hours),
                })

df = pd.DataFrame(all_rows)
print(f'Total rows: {len(df)}')
print(f'Periods: {df["Period"].unique().tolist()}')
print(f'Districts: {df["District"].unique().tolist()}')
print(f'Stores per period:')
print(df.groupby('Period')['Store No'].count())
print('\nSample:')
print(df.head(10).to_string(index=False))
df.to_csv(r'C:\Users\sorja\Downloads\Wingstop Data\data\schedule_guide.csv', index=False)
print('\nSaved to data/schedule_guide.csv')
