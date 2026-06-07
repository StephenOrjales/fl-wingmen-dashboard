import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

pdf_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\sorja\Downloads\1.03 - Sales Journal.pdf'

pdf = pdfplumber.open(pdf_path)
print(f'Pages: {len(pdf.pages)}')

all_rows = []

for i in range(0, len(pdf.pages), 2):
    page1 = pdf.pages[i].extract_text() or ''
    page2 = pdf.pages[i + 1].extract_text() if i + 1 < len(pdf.pages) else ''

    # Extract store number from header like "0079 - FL - Plantation - W"
    store_match = re.match(r'(\d+)\s*-\s*[Ff][Ll]\s*-\s*', page1)
    if not store_match:
        print(f'  Skipping page {i+1}: no store match')
        continue
    store_no = str(int(store_match.group(1)))

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

    # Page 1 metrics
    net_sales = parse_dollar(page1, r'= Net Sales\s+\$?([\d,]+\.?\d*)')
    gross_sales = parse_dollar(page1, r'= Gross Sales\s+\$?([\d,]+\.?\d*)')
    food_sales = parse_dollar(page1, r'Food Sales\s+\$?([\d,]+\.?\d*)')
    bev_sales = parse_dollar(page1, r'Beverage Sales\s+\$?([\d,]+\.?\d*)')
    sales_tax = parse_dollar(page1, r'\+ Sales Tax\s+\$?([\d,]+\.?\d*)')
    void_count = parse_int(page1, r'Void Count\s+(\d+)')
    void_sales = parse_dollar(page1, r'Void Sales\s+\$?([\d,]+\.?\d*)')
    refund = parse_dollar(page1, r'Refund \$\s+\-?\$?([\d,]+\.?\d*)')
    # Check for negative refund
    refund_match = re.search(r'Refund \$\s+(-?\$?[\d,]+\.?\d*)', page1)
    if refund_match:
        val = refund_match.group(1).replace(',', '').replace('$', '')
        try:
            refund = float(val)
        except ValueError:
            refund = None

    cash_over_short_match = re.search(r'Cash Over/Short\s+\(?\$?([\d,]+\.?\d*)\)?', page1)
    cash_over_short = None
    if cash_over_short_match:
        val = cash_over_short_match.group(1).replace(',', '')
        try:
            cash_over_short = float(val)
        except ValueError:
            pass
        # Check if negative (in parens)
        full = re.search(r'Cash Over/Short\s+(\(?\$?[\d,]+\.?\d*\)?)', page1)
        if full and '(' in full.group(1):
            cash_over_short = -cash_over_short

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

df = pd.DataFrame(all_rows)
df = df.sort_values('Store No', key=lambda x: x.astype(int))
print(f'\nTotal stores: {len(df)}')
print(f'Period: {df["Period"].iloc[0] if len(df) > 0 else "?"}')
print(f'\nNet Sales stats:')
print(f'  Total: ${df["Net Sales"].sum():,.2f}')
print(f'  Avg:   ${df["Net Sales"].mean():,.2f}')
print(f'  Min:   ${df["Net Sales"].min():,.2f}')
print(f'  Max:   ${df["Net Sales"].max():,.2f}')
print(f'\nVoid Count total: {df["Void Count"].sum()}')
print(f'Void Sales total: ${df["Void Sales"].sum():,.2f}')
print(f'Cash Over/Short total: ${df["Cash Over/Short"].sum():,.2f}')
print(f'\nDaypart sales totals:')
for dp in ['Lunch', 'Snack', 'Dinner', 'Late']:
    print(f'  {dp}: ${df[f"{dp} Sales"].sum():,.2f}')

out = Path(r'C:\Users\sorja\Downloads\Wingstop Data\data\sales_journal.csv')
df.to_csv(out, index=False)
print(f'\nSaved to {out}')
