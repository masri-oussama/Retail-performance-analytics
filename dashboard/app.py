from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/dashboard_transactions.csv.gz")


st.set_page_config(
    page_title="Retail Performance Analytics",
    page_icon="📊",
    layout="wide",
)


st.title("Retail Performance Analytics")

st.write(
    "Interactive dashboard for analyzing sales, customers, products, "
    "countries, and cancellations."
)


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Load the compressed dashboard dataset."""

    if not path.exists():
        raise FileNotFoundError(
            f"Dashboard dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["invoice_date"],
    )


try:
    df = load_data(DATA_PATH)

except FileNotFoundError:
    st.error(
        "The dashboard dataset could not be found. "
        "Make sure `data/dashboard_transactions.csv.gz` "
        "is included in the GitHub repository."
    )
    st.stop()

except Exception as error:
    st.error(f"An error occurred while loading the data: {error}")
    st.stop()


sales_df = df[
    (df["quantity"] > 0)
    & (~df["is_cancellation"])
    & (df["unit_price"] > 0)
].copy()


st.subheader("Data validation")

column_1, column_2 = st.columns(2)

with column_1:
    st.metric(
        label="All cleaned rows",
        value=f"{len(df):,}",
    )

with column_2:
    st.metric(
        label="Successful sales rows",
        value=f"{len(sales_df):,}",
    )


st.subheader("Sample data")

st.dataframe(
    sales_df.head(10),
    use_container_width=True,
)