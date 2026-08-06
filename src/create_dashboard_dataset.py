from pathlib import Path

import pandas as pd


SOURCE_PATH = Path("data/processed/transactions_clean.csv")
OUTPUT_PATH = Path("data/dashboard_transactions.csv.gz")

df = pd.read_csv(
    SOURCE_PATH,
    parse_dates=["invoice_date"],
)

df.to_csv(
    OUTPUT_PATH,
    index=False,
    compression="gzip",
)

print(f"Dashboard dataset created at: {OUTPUT_PATH}")
print(f"Rows: {len(df):,}")