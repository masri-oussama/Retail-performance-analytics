from pathlib import Path
import sqlite3
import pandas as pd


PROCESSED_DATA_PATH = Path("data/processed/transactions_clean.csv")
DATABASE_PATH = Path("data/processed/retail.db")


def load_processed_data(path: Path) -> pd.DataFrame:
    """Load the cleaned retail dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Processed data not found: {path}")

    return pd.read_csv(path)


def create_database(df: pd.DataFrame, database_path: Path) -> None:
    """Create a SQLite database and load the transaction table."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        df.to_sql(
            "transactions",
            connection,
            if_exists="replace",
            index=False,
        )


def main() -> None:
    df = load_processed_data(PROCESSED_DATA_PATH)
    create_database(df, DATABASE_PATH)

    print(f"Database created at: {DATABASE_PATH}")
    print(f"Rows loaded: {len(df):,}")


if __name__ == "__main__":
    main()