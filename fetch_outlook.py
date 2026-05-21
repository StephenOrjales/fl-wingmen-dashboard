import win32com.client
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SUBJECT = "Subscription for Smart Kitchen Daily"
DAILY_FILE = DATA_DIR / "smart_kitchen_daily.xlsx"
HISTORY_FILE = DATA_DIR / "kds_history.csv"


def fetch_latest_report():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Outlook...")
    try:
        outlook = win32com.client.GetActiveObject("Outlook.Application")
    except Exception:
        outlook = win32com.client.Dispatch("Outlook.Application")
    mapi = outlook.GetNamespace("MAPI")
    inbox = mapi.GetDefaultFolder(6)

    cutoff = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y")
    restriction = f"[ReceivedTime] >= '{cutoff}'"
    messages = inbox.Items.Restrict(restriction)
    messages.Sort("[ReceivedTime]", True)

    print(f"  Looking for: '{SUBJECT}'")
    print(f"  Emails since {cutoff}: {messages.Count}")

    candidates = []
    for msg in messages:
        try:
            subj = msg.Subject or ""
            if SUBJECT.lower() in subj.lower():
                print(f"  Match: '{subj}' at {msg.ReceivedTime}")
                candidates.append(msg)
        except Exception:
            continue

    found = None
    if candidates:
        found = max(candidates, key=lambda m: m.ReceivedTime)
        print(f"  Using newest: {found.ReceivedTime}")

    if not found:
        print("  No matching email found.")
        return False

    attachments = found.Attachments
    if attachments.Count == 0:
        print("  Email found but no attachments.")
        return False

    saved = False
    for i in range(1, attachments.Count + 1):
        att = attachments.Item(i)
        if att.FileName.endswith((".xlsx", ".xls")):
            att.SaveAsFile(str(DAILY_FILE.resolve()))
            print(f"  Saved: {att.FileName} -> {DAILY_FILE}")
            saved = True
            break

    if not saved:
        print("  No Excel attachment found.")
        return False

    append_to_history()
    return True


def append_to_history():
    print("\n  Updating history...")
    df = pd.read_excel(DAILY_FILE, sheet_name="Smart Kitchen Daily", header=None, skiprows=10)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    df = df.loc[:, df.columns.notna()]
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["STORE FULL NAME"])

    n_stores = df["STORE FULL NAME"].nunique()
    n_days = len(df) // n_stores if n_stores > 0 else 0
    file_mod = datetime.fromtimestamp(DAILY_FILE.stat().st_mtime)

    if HISTORY_FILE.exists():
        history = pd.read_csv(HISTORY_FILE)
        history = history.loc[:, ~history.columns.str.startswith("Unnamed")]
        history.columns = [str(c).strip() for c in history.columns]
        existing_dates = set(history["data_date"].unique())

        data_cols = [c for c in df.columns if c != "data_date"]
        history_data_cols = [c for c in data_cols if c in history.columns]

        new_day = file_mod - timedelta(days=1)
        new_date = new_day.strftime("%Y-%m-%d")

        if new_date in existing_dates:
            print(f"  History already has {new_date}. No update needed.")
            return

        prev_count = len(history[history["data_date"] == max(existing_dates)])
        curr_total = len(df)
        new_rows_count = curr_total - (curr_total - n_stores)

        merged = df.merge(
            history[history_data_cols].drop_duplicates(),
            how="left", indicator=True, on=history_data_cols,
        )
        new_rows = merged[merged["_merge"] == "left_only"].drop("_merge", axis=1).copy()

        if len(new_rows) == 0:
            print(f"  No new rows found for {new_date}.")
            return

        new_rows = new_rows.drop_duplicates(subset=["STORE FULL NAME"], keep="first")
        new_rows["data_date"] = new_date
        print(f"  Found {len(new_rows)} new rows for {new_date}")

        shared_cols = list(dict.fromkeys(c for c in new_rows.columns if c in history.columns))
        new_rows = new_rows[shared_cols]
        history = history[shared_cols]
        history = pd.concat([history, new_rows], ignore_index=True)
        history = history.drop_duplicates(subset=["STORE FULL NAME", "data_date"], keep="last")
    else:
        recent_date = (file_mod - timedelta(days=1)).strftime("%Y-%m-%d")
        prior_date = (file_mod - timedelta(days=2)).strftime("%Y-%m-%d")
        df["_rank"] = df.groupby("STORE FULL NAME").cumcount()
        day1 = df[df["_rank"] == 0].drop("_rank", axis=1).copy()
        day2 = df[df["_rank"] == 1].drop("_rank", axis=1).copy()
        day1["data_date"] = recent_date
        day2["data_date"] = prior_date
        history = pd.concat([day1, day2], ignore_index=True)
        history = history.drop_duplicates(subset=["STORE FULL NAME", "data_date"], keep="last")

    history = history.sort_values(["data_date", "STORE FULL NAME"], ascending=[False, True])
    history.to_csv(HISTORY_FILE, index=False)
    dates_in_history = sorted(history["data_date"].unique(), reverse=True)
    print(f"  History updated: {len(history)} rows, {len(dates_in_history)} dates")
    print(f"  Dates: {', '.join(dates_in_history[:5])}{'...' if len(dates_in_history) > 5 else ''}")


if __name__ == "__main__":
    import sys
    success = fetch_latest_report()
    if success:
        print("\nDone! Dashboard data updated.")
    else:
        print("\nNo update available.")
        sys.exit(1)
