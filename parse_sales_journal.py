import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

pdf_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\sorja\Downloads\1.03 - Sales Journal.pdf'

pdf = pdfplumber.open(pdf_path)
print(f'Pages: {len(pdf.pages)}')


def parse_dollar(text, pattern):
    m = re.search(pattern, text)
    if m:
        val = m.group(1).replace(',', '').replace('$', '').replace('(', '-').replace(')', '')
        try:
            return float(val)
        except ValueError:
            return None
    return None


def parse_int(text, pattern):
    m = re.search(pattern, text)
    if m:
        val = m.group(1).replace(',', '')
        try:
            return int(val)
        except ValueError:
            return None
    return None


def parse_pct(text, pattern):
    m = re.search(pattern, text)
    if m:
        val = m.group(1).replace('%', '')
        try:
            return float(val)
        except ValueError:
            return None
    return None


# Group pages by store — each store has a main page and a daypart page
# Some stores may have extra pages, so detect by content rather than assuming pairs
stores_pages = []  # list of {'main': text, 'daypart': text}
current = None

for i in range(len(pdf.pages)):
    text = pdf.pages[i].extract_text() or ''
    has_daypart = 'Day Part Sales' in text
    store_match = re.match(r'(\d+)\s*-\s*[Ff][Ll]\s*-', text)

    if has_daypart:
        # This is a daypart page — attach to current store
        if current:
            current['daypart'] = text
            stores_pages.append(current)
            current = None
    elif store_match:
        # This is a main page for a (possibly new) store
        store_no = str(int(store_match.group(1)))
        if current and current.get('store_no') == store_no:
            # Extra main page for same store — merge text
            current['main'] += '\n' + text
        else:
            # New store — save previous if it exists without daypart
            if current:
                stores_pages.append(current)
            current = {'store_no': store_no, 'main': text, 'daypart': ''}
    else:
        print(f'  Skipping page {i+1}: no store match')

# Don't forget the last store if it had no daypart page
if current:
    stores_pages.append(current)

print(f'Stores found: {len(stores_pages)}')

all_rows = []
for sp in stores_pages:
    page1 = sp['main']
    page2 = sp['daypart']
    store_no = sp['store_no']

    # Extract period/week
    period_match = re.search(r'Period:\s*(\d+)\s+Week:\s*(\d+)', page1)
    if period_match:
        period = f'P{period_match.group(1)}W{period_match.group(2)}'
    else:
        period = ''

    # Extract date range
    date_match = re.search(r'(\d+/\d+/\d+)\s*-\s*(\d+/\d+/\d+)', page1)
    start_date = date_match.group(1) if date_match else ''
    end_date = date_match.group(2) if date_match else ''

    # Page 1 metrics
    net_sales = parse_dollar(page1, r'= Net Sales\s+\$?([\d,]+\.?\d*)')
    gross_sales = parse_dollar(page1, r'= Gross Sales\s+\$?([\d,]+\.?\d*)')
    food_sales = parse_dollar(page1, r'Food Sales\s+\$?([\d,]+\.?\d*)')
    bev_sales = parse_dollar(page1, r'Beverage Sales\s+\$?([\d,]+\.?\d*)')
    sales_tax = parse_dollar(page1, r'\+ Sales Tax\s+\$?([\d,]+\.?\d*)')
    void_count = parse_int(page1, r'Void Count\s+(\d+)')
    void_sales = parse_dollar(page1, r'Void Sales\s+\$?([\d,]+\.?\d*)')

    # Refund (may be negative)
    refund = None
    refund_match = re.search(r'Refund \$\s+(-?\$?[\d,]+\.?\d*)', page1)
    if refund_match:
        val = refund_match.group(1).replace(',', '').replace('$', '')
        try:
            refund = float(val)
        except ValueError:
            pass

    # Cash Over/Short (negative if in parens)
    cash_over_short = None
    cos_match = re.search(r'Cash Over/Short\s+(\(?\$?[\d,]+\.?\d*\)?)', page1)
    if cos_match:
        raw = cos_match.group(1)
        is_neg = '(' in raw
        val = raw.replace('(', '').replace(')', '').replace('$', '').replace(',', '')
        try:
            cash_over_short = -float(val) if is_neg else float(val)
        except ValueError:
            pass

    checks_total = parse_int(page1, r'Checks - TOTAL\s+([\d,]+)')
    check_avg = parse_dollar(page1, r'Check Average\s+\$?([\d,]+\.?\d*)')

    # Labor
    labor_pct = parse_pct(page1, r'Labor Percent\s+([\d.]+)%')
    labor_dollars = parse_dollar(page1, r'Labor Dollars\s+\$?([\d,]+\.?\d*)')
    labor_reg_hours = parse_dollar(page1, r'Labor REG Hours\s+([\d,]+\.?\d*)')
    labor_spmh = parse_dollar(page1, r'Labor SPMH\s+\$?([\d,]+\.?\d*)')

    # Page 2 - Daypart sales
    dayparts = {}
    for dp_name in ['Lunch', 'Snack', 'Dinner', 'Late']:
        dp_match = re.search(
            rf'{dp_name}\s+[\d:]+\s+[AP]M\s+\$?([\d,]+\.?\d*)\s+([\d,]+)\s+\$?([\d,]+\.?\d*)\s+([\d.]+)%',
            page2
        )
        if dp_match:
            dayparts[dp_name] = {
                'sales': float(dp_match.group(1).replace(',', '')),
                'tickets': int(dp_match.group(2).replace(',', '')),
                'avg': float(dp_match.group(3).replace(',', '')),
                'pct': float(dp_match.group(4)),
            }

    # Total online
    online_sales = parse_dollar(page2, r'Total Online\s+\$?([\d,]+\.?\d*)')

    # Discounts
    total_comps = parse_dollar(page2, r'TOTAL COMPS\s+\$?([\d,]+\.?\d*)')
    total_promos = parse_dollar(page2, r'TOTAL PROMOS\s+\$?([\d,]+\.?\d*)')
    total_discount = parse_dollar(page2, r'TOTAL DISCOUNT\s+\$?([\d,]+\.?\d*)')
    discount_pct = parse_pct(page2, r'TOTAL DISCOUNT\s+\$?[\d,]+\.?\d*\s+([\d.]+)%')

    row = {
        'Period': period,
        'Start Date': start_date,
        'End Date': end_date,
        'Store No': store_no,
        'Net Sales': net_sales,
        'Gross Sales': gross_sales,
        'Food Sales': food_sales,
        'Beverage Sales': bev_sales,
        'Sales Tax': sales_tax,
        'Void Count': void_count,
        'Void Sales': void_sales,
        'Refund': refund,
        'Cash Over/Short': cash_over_short,
        'Checks Total': checks_total,
        'Check Avg': check_avg,
        'Labor %': labor_pct,
        'Labor $': labor_dollars,
        'Labor REG Hours': labor_reg_hours,
        'Labor SPMH': labor_spmh,
        'Online Sales': online_sales,
        'Total Comps': total_comps,
        'Total Promos': total_promos,
        'Total Discount': total_discount,
        'Discount %': discount_pct,
    }

    # Daypart columns
    for dp_name in ['Lunch', 'Snack', 'Dinner', 'Late']:
        dp = dayparts.get(dp_name, {})
        row[f'{dp_name} Sales'] = dp.get('sales')
        row[f'{dp_name} Tickets'] = dp.get('tickets')
        row[f'{dp_name} Avg'] = dp.get('avg')
        row[f'{dp_name} %'] = dp.get('pct')

    all_rows.append(row)

new_df = pd.DataFrame(all_rows)
# Drop incomplete store records (e.g., a partial/placeholder page with no Net Sales).
_before = len(new_df)
new_df = new_df[new_df["Net Sales"].notna()].reset_index(drop=True)
if len(new_df) < _before:
    dropped = _before - len(new_df)
    print(f'Dropped {dropped} incomplete store row(s) (no Net Sales)')
new_period = new_df["Period"].iloc[0] if len(new_df) > 0 else "?"
print(f'\nParsed {len(new_df)} stores for {new_period}')

out = Path(r'C:\Users\sorja\Downloads\Wingstop Data\data\sales_journal.csv')

# Merge with existing data (append new period, replace if period already exists)
if out.exists():
    existing = pd.read_csv(out)
    existing = existing[existing["Period"] != new_period]  # remove old data for this period
    combined = pd.concat([existing, new_df], ignore_index=True)
else:
    combined = new_df

combined = combined.sort_values(['Period', 'Store No'])
combined.to_csv(out, index=False)

print(f'Total rows: {len(combined)}')
print(f'Periods: {sorted(combined["Period"].unique())}')
print(f'\n{new_period} stats:')
print(f'  Net Sales Total: ${new_df["Net Sales"].sum():,.2f}')
print(f'  Stores: {len(new_df)}')
print(f'  Void Count: {new_df["Void Count"].sum()}')
print(f'  Cash Over/Short: ${new_df["Cash Over/Short"].sum():,.2f}')
print(f'\nSaved to {out}')
