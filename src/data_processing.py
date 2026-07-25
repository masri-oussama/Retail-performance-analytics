from pathlib import Path
import pandas as pd

# Using relative paths makes your project portable!
RAW_DATA_PATH = Path("data/raw/Online Retail.xlsx")
PROCESSED_DATA_PATH = Path("data/processed/transactions_clean.csv")

def load_data(path: Path) -> pd.DataFrame:
    """Load the raw retail dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    return pd.read_excel(path)

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to lowercase snake_case."""
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    rename_mapping = {
        "invoiceno": "invoice_no",
        "stockcode": "stock_code",
        "invoicedate": "invoice_date",
        "unitprice": "unit_price",
        "customerid": "customer_id",
    }

    # Apply the mapping, print to verify, then return
    df = df.rename(columns=rename_mapping)
    print("New columns:", df.columns.tolist())
    
    return df
def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns into appropriate data types."""
    df = df.copy()

    df["invoice_no"] = df["invoice_no"].astype(str)
    df["stock_code"] = df["stock_code"].astype(str)
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"],
        errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    return df

def add_business_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create useful columns for business analysis."""
    df = df.copy()

    df["is_cancellation"] = (
        df["invoice_no"]
        .str.startswith("C")
    )

    df["revenue"] = (
        df["quantity"]
        * df["unit_price"]
    )

    df["year"] = df["invoice_date"].dt.year
    df["month"] = df["invoice_date"].dt.month
    df["year_month"] = (
        df["invoice_date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["day_of_week"] = (
        df["invoice_date"]
        .dt.day_name()
    )

    df["hour"] = df["invoice_date"].dt.hour

    df["has_customer_id"] = (
        df["customer_id"].notna()
    )

    return df

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clean the retail dataset.

    Returns:
        cleaned_df: Valid rows for future analysis.
        rejected_df: Invalid rows removed during cleaning.
    """
    df = df.copy()

    df = standardize_column_names(df)
    df = convert_data_types(df)

    df = df.drop_duplicates()

    df["description"] = (
        df["description"]
        .fillna("Unknown product")
        .str.strip()
    )

    invalid_rows = (
        df["invoice_date"].isna()
        | df["quantity"].isna()
        | df["unit_price"].isna()
        | (df["unit_price"] <= 0)
    )

    rejected_df = df.loc[invalid_rows].copy()
    cleaned_df = df.loc[~invalid_rows].copy()

    cleaned_df = add_business_features(cleaned_df)

    return cleaned_df, rejected_df

def save_data(
    cleaned_df: pd.DataFrame,
    rejected_df: pd.DataFrame
) -> None:
    """Save cleaned and rejected datasets."""
    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned_df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    rejected_df.to_csv(
        "data/processed/rejected_rows.csv",
        index=False
    )

def main() -> None:
    raw_df = load_data(RAW_DATA_PATH)

    cleaned_df, rejected_df = clean_data(raw_df)

    save_data(cleaned_df, rejected_df)

    print(f"Raw rows: {len(raw_df):,}")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Rejected rows: {len(rejected_df):,}")


if __name__ == "__main__":
    main()