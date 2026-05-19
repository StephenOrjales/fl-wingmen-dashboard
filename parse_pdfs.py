import sys
import io
import re
import csv
import pdfplumber
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── Parse Smart Kitchen Performance ──
print("Parsing Smart Kitchen Performance...")
pdf_sk = pdfplumber.open(r"C:\Users\sorja\Downloads\Smart Kitchen Performance.pdf")

# Page 3 has all stores with Brand Partner Name
text_p3 = pdf_sk.pages[2].extract_text()
lines = text_p3.split('\n')

sk_rows = []
for line in lines:
    # Match store lines: number-state-name  BrandPartner  #weeks  SOS  AQT  %7-10  BoneInAcc  BoneInAdopt  MakeAhead  Waste%  Orders  PreBump
    # Simpler approach: find lines with time patterns like HH:MM
    parts = line.strip()
    if not parts or not parts[0].isdigit():
        continue
    # Skip header-like lines
    if 'Store' in parts and 'Brand' in parts:
        continue
    # Try to extract numeric fields from the end
    tokens = parts.split()
    # Find time pattern (MM:SS) - indicates SOS column
    time_indices = [i for i, t in enumerate(tokens) if re.match(r'^\d{2}:\d{2}$', t)]
    if len(time_indices) >= 2:
        sos_idx = time_indices[0]
        aqt_idx = time_indices[1]
        store_name = ' '.join(tokens[:sos_idx - 2])  # Before brand partner and weeks
        # Find brand partner (usually "Sergio Balsinde" = 2 tokens before weeks)
        brand_partner = tokens[sos_idx - 2] + ' ' + tokens[sos_idx - 1] if sos_idx >= 2 else ''
        # Actually the pattern is: store_name  Sergio Balsinde  ##  HH:MM  HH:MM  ...
        # Let's find "Sergio" or the weeks number
        sergio_idx = None
        for i, t in enumerate(tokens):
            if t == 'Sergio':
                sergio_idx = i
                break
        if sergio_idx is not None:
            store_name = ' '.join(tokens[:sergio_idx])
            weeks = tokens[sergio_idx + 2] if sergio_idx + 2 < len(tokens) else ''
            remaining = tokens[sergio_idx + 3:]  # After weeks
        else:
            store_name = ' '.join(tokens[:sos_idx - 1])
            weeks = tokens[sos_idx - 1]
            remaining = tokens[sos_idx:]
            brand_partner = ''

        if len(remaining) >= 8:
            row = {
                'store': store_name,
                'brand_partner': brand_partner if sergio_idx else '',
                'weeks': weeks,
                'sos': remaining[0] if len(remaining) > 0 else '',
                'aqt': remaining[1] if len(remaining) > 1 else '',
                'pct_orders_7_10': remaining[2] if len(remaining) > 2 else '',
                'bone_in_accuracy': remaining[3] if len(remaining) > 3 else '',
                'bone_in_adoption': remaining[4] if len(remaining) > 4 else '',
                'make_ahead_unit': remaining[5] if len(remaining) > 5 else '',
                'waste_pct': remaining[6] if len(remaining) > 6 else '',
                'orders': remaining[7] if len(remaining) > 7 else '',
                'pre_bump_rate': remaining[8] if len(remaining) > 8 else '',
            }
            sk_rows.append(row)

print(f"  Found {len(sk_rows)} store rows")
for r in sk_rows[:3]:
    print(f"    {r['store']}: SOS={r['sos']}, Orders={r['orders']}")

# ── Parse Brand Partner Performance ──
print("\nParsing Brand Partner Performance...")
pdf_bp = pdfplumber.open(r"C:\Users\sorja\Downloads\Brand Partner Performance - BP View.pdf")

# Page 2 has store-level: Store, FBC, DMA, Avg Wk Sales, Avg Wk TXN, Avg Ticket, COGS, Digital, Delivery, Boneless, Sandwich, Tenders, Net Sales
text_p2 = pdf_bp.pages[1].extract_text()
lines_p2 = text_p2.split('\n')

bp_rows = []
for line in lines_p2:
    parts = line.strip()
    if not parts or not parts[0].isdigit():
        continue
    if 'Store' in parts and 'FBC' in parts:
        continue
    # Pattern: store_name  FBC_name  DMA  $sales  txn  $ticket  cogs%  digital%  delivery%  boneless%  sandwich%  tenders%  $net_sales
    # Find dollar amounts
    dollars = re.findall(r'\$[\d,.]+', parts)
    percents = re.findall(r'[\d.]+%', parts)
    numbers = re.findall(r'(?<!\$)(?<!\d)\b(\d{1,5})\b(?!%)', parts)

    # Use the text extraction from pdfplumber tables instead
    pass

# Better approach: use pdfplumber table extraction on page 2
tables_p2 = pdf_bp.pages[1].extract_tables()
print(f"  Page 2 tables: {len(tables_p2)}")
for t_idx, table in enumerate(tables_p2):
    print(f"    Table {t_idx}: {len(table)} rows x {len(table[0]) if table else 0} cols")

# Page 3 - COGS Analysis
text_p3_bp = pdf_bp.pages[2].extract_text()
lines_p3_bp = text_p3_bp.split('\n')

cogs_rows = []
for line in lines_p3_bp:
    parts = line.strip()
    if not parts or not parts[0].isdigit():
        continue
    if 'Store' in parts and 'COGS' in parts:
        continue
    if 'Total' in parts:
        continue
    # Pattern: store  COGS%  CY_COGS_PY  Var  Theoretical  Var  BonelessMix  BonelessMixPY  Var  BoneInCount  BoneInWeekly  Void  LandedCost  ChickenVar  PotatoVar
    tokens = parts.split()
    # Find store name - ends before first percentage
    pct_idx = None
    for i, t in enumerate(tokens):
        if '%' in t or t.startswith('$') or (re.match(r'^-?\d+\.\d+%?$', t) and i > 3):
            pct_idx = i
            break
    if pct_idx and pct_idx > 2:
        store = ' '.join(tokens[:pct_idx])
        metrics = tokens[pct_idx:]
        if len(metrics) >= 10:
            cogs_rows.append({
                'store': store,
                'cogs_pct': metrics[0],
                'cogs_py_var': metrics[1],
                'theoretical_var': metrics[2],
                'boneless_mix': metrics[3],
                'boneless_mix_py_var': metrics[4],
                'bone_in_count': metrics[5] if not metrics[5].endswith('%') else '',
                'bone_in_weekly_pct': metrics[6] if '%' in metrics[6] else metrics[5],
                'void_pct': metrics[-4] if len(metrics) > 10 else '',
                'landed_cost': [m for m in metrics if m.startswith('$')][0] if any(m.startswith('$') for m in metrics) else '',
            })

print(f"  Found {len(cogs_rows)} COGS rows")
for r in cogs_rows[:3]:
    print(f"    {r['store']}: COGS={r['cogs_pct']}")

# Page 4 - Labor Analysis
text_p4_bp = pdf_bp.pages[3].extract_text()
lines_p4_bp = text_p4_bp.split('\n')

labor_rows = []
for line in lines_p4_bp:
    parts = line.strip()
    if not parts or not parts[0].isdigit():
        continue
    if 'Restaurant' in parts or 'Total' in parts:
        continue
    tokens = parts.split()
    pct_idx = None
    for i, t in enumerate(tokens):
        if '%' in t and i > 3:
            pct_idx = i
            break
    if pct_idx and pct_idx > 2:
        store = ' '.join(tokens[:pct_idx])
        metrics = tokens[pct_idx:]
        labor_rows.append({
            'store': store,
            'labor_pct': metrics[0] if len(metrics) > 0 else '',
            'labor_var_py': metrics[1] if len(metrics) > 1 else '',
            'splh': metrics[2] if len(metrics) > 2 else '',
            'tplh': metrics[3] if len(metrics) > 3 else '',
        })

print(f"  Found {len(labor_rows)} Labor rows")

# ── Parse Executive Flash ──
print("\nParsing Executive Flash...")
pdf_ef = pdfplumber.open(r"C:\Users\sorja\Downloads\Brand Partner Performance - BP View Executive Flash.pdf")

# Page 5 has DMA-level and store-level sales data
text_p5 = pdf_ef.pages[4].extract_text()
lines_p5 = text_p5.split('\n')

flash_rows = []
for line in lines_p5:
    parts = line.strip()
    if not parts or not parts[0].isdigit():
        continue
    if 'Total' in parts:
        continue
    tokens = parts.split()
    # Store lines have store name then dollar values
    dollar_idx = None
    for i, t in enumerate(tokens):
        if t.startswith('$') or (re.match(r'^\d+K$', t)):
            dollar_idx = i
            break
    if dollar_idx and dollar_idx > 2:
        store = ' '.join(tokens[:dollar_idx])
        metrics = tokens[dollar_idx:]
        flash_rows.append({
            'store': store,
            'metrics': ' '.join(metrics),
        })

print(f"  Found {len(flash_rows)} Flash rows")

# ── Now build combined data using text-based parsing ──
# The most reliable data is from the raw text of each PDF page
# Let me re-parse more carefully using the full text

print("\n\n=== BUILDING COMBINED STORE DATA ===")

# Re-parse Smart Kitchen page 1 text more carefully
all_sk_text = ''
for page in pdf_sk.pages:
    all_sk_text += page.extract_text() + '\n'

# Find all unique store entries
store_pattern = re.compile(
    r'(\d{2,4}-FL-[A-Za-z\s.\'-]+?)(?:\s+(?:Sergio Balsinde|MIAMI|WEST PALM))'
)
all_stores = set()
for m in store_pattern.finditer(all_sk_text):
    all_stores.add(m.group(1).strip())

print(f"Found {len(all_stores)} unique stores across Smart Kitchen PDF")
for s in sorted(all_stores)[:5]:
    print(f"  {s}")

# Parse page 3 line by line more carefully
print("\n--- Re-parsing page 3 ---")
text = pdf_sk.pages[2].extract_text()
store_metrics = []
current_section = ''

for line in text.split('\n'):
    line = line.strip()
    if 'Top Stores' in line or 'Bottom Stores' in line:
        current_section = line
        continue
    if not line or not line[0].isdigit():
        continue

    # Try to split: everything before "Sergio Balsinde" is store name
    if 'Sergio Balsinde' in line:
        idx = line.index('Sergio Balsinde')
        store_name = line[:idx].strip()
        rest = line[idx + len('Sergio Balsinde'):].strip()
        tokens = rest.split()
        if len(tokens) >= 9:
            store_metrics.append({
                'store': store_name,
                'weeks': tokens[0],
                'sos': tokens[1],
                'aqt': tokens[2],
                'pct_orders_7_10': tokens[3],
                'bone_in_accuracy': tokens[4],
                'bone_in_adoption': tokens[5],
                'make_ahead_unit': tokens[6],
                'waste_pct': tokens[7],
                'orders': tokens[8],
                'pre_bump_rate': tokens[9] if len(tokens) > 9 else '',
            })

print(f"Parsed {len(store_metrics)} stores from SK page 3")

# Parse BP page 2 - store sales data
text_bp2 = pdf_bp.pages[1].extract_text()
sales_metrics = []
for line in text_bp2.split('\n'):
    line = line.strip()
    if not line or not line[0].isdigit():
        continue
    # Lines have: store  FBC_name  DMA  $amount  number  $amount  percent...
    # Find the FBC name (Jackson Mueller or similar)
    for fbc in ['Jackson Mueller', 'Sergio Balsinde']:
        if fbc in line:
            idx = line.index(fbc)
            store_name = line[:idx].strip()
            rest = line[idx + len(fbc):].strip()
            # Remove DMA prefix
            rest = re.sub(r'^MIAMI-FT\. LAUDE[A-Z]*\.?\s*', '', rest)
            rest = re.sub(r'^WEST PALM BEACH[A-Z\s.-]*\s*', '', rest)
            tokens = rest.split()
            # Expected: $sales  txn  $ticket  cogs%  digital%  delivery%  boneless%  sandwich%  tenders%  $net_sales
            dollars = [t for t in tokens if t.startswith('$')]
            percents = [t for t in tokens if '%' in t]
            nums = [t for t in tokens if re.match(r'^\d{1,5}$', t)]

            if dollars and len(tokens) >= 5:
                sales_metrics.append({
                    'store': store_name,
                    'avg_wk_sales': dollars[0] if len(dollars) > 0 else '',
                    'avg_wk_txn': nums[0] if nums else '',
                    'avg_ticket': dollars[1] if len(dollars) > 1 else '',
                    'net_sales': dollars[-1] if len(dollars) > 2 else '',
                })
            break

print(f"Parsed {len(sales_metrics)} stores from BP page 2")

# Parse BP page 3 - COGS
text_bp3 = pdf_bp.pages[2].extract_text()
cogs_data = []
for line in text_bp3.split('\n'):
    line = line.strip()
    if not line or not line[0].isdigit():
        continue
    if 'Total' in line:
        continue
    # Store name ends before first percentage
    tokens = line.split()
    first_pct = None
    for i, t in enumerate(tokens):
        if re.match(r'^-?\d+\.?\d*%$', t) and i > 3:
            first_pct = i
            break
    if first_pct:
        store = ' '.join(tokens[:first_pct])
        metrics = tokens[first_pct:]
        if len(metrics) >= 6:
            cogs_data.append({
                'store': store,
                'cogs_pct': metrics[0],
                'cogs_var_py': metrics[1],
                'theoretical_var': metrics[2],
                'boneless_mix': metrics[3],
                'boneless_mix_var': metrics[4],
            })

print(f"Parsed {len(cogs_data)} stores from BP page 3 (COGS)")

# Parse BP page 4 - Labor
text_bp4 = pdf_bp.pages[3].extract_text()
labor_data = []
for line in text_bp4.split('\n'):
    line = line.strip()
    if not line or not line[0].isdigit():
        continue
    if 'Total' in line or 'Restaurant' in line:
        continue
    tokens = line.split()
    first_pct = None
    for i, t in enumerate(tokens):
        if re.match(r'^-?\d+\.?\d*%$', t) and i > 3:
            first_pct = i
            break
    if first_pct:
        store = ' '.join(tokens[:first_pct])
        metrics = tokens[first_pct:]
        if len(metrics) >= 3:
            labor_data.append({
                'store': store,
                'labor_pct': metrics[0],
                'labor_var_py': metrics[1] if len(metrics) > 1 else '',
                'splh': metrics[2] if len(metrics) > 2 else '',
                'tplh': metrics[3] if len(metrics) > 3 else '',
            })

print(f"Parsed {len(labor_data)} stores from BP page 4 (Labor)")

# ── Write combined CSV ──
print("\n=== Writing CSV files ===")

# Smart Kitchen data
if store_metrics:
    with open(DATA_DIR / 'smart_kitchen.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=store_metrics[0].keys())
        writer.writeheader()
        writer.writerows(store_metrics)
    print(f"  Wrote smart_kitchen.csv ({len(store_metrics)} rows)")

# Sales data
if sales_metrics:
    with open(DATA_DIR / 'store_sales.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sales_metrics[0].keys())
        writer.writeheader()
        writer.writerows(sales_metrics)
    print(f"  Wrote store_sales.csv ({len(sales_metrics)} rows)")

# COGS data
if cogs_data:
    with open(DATA_DIR / 'store_cogs.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cogs_data[0].keys())
        writer.writeheader()
        writer.writerows(cogs_data)
    print(f"  Wrote store_cogs.csv ({len(cogs_data)} rows)")

# Labor data
if labor_data:
    with open(DATA_DIR / 'store_labor.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=labor_data[0].keys())
        writer.writeheader()
        writer.writerows(labor_data)
    print(f"  Wrote store_labor.csv ({len(labor_data)} rows)")

print("\nDone!")
