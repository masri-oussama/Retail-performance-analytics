from pathlib import Path
import plotly.express as px
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
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(
        path,
        parse_dates=["invoice_date"],
    )


try:
    df = load_data(DATA_PATH)

except FileNotFoundError:
    st.error(
        "The dashboard dataset could not be found."
    )
    st.stop()


sales_df = df[
    (df["quantity"] > 0)
    & (~df["is_cancellation"])
    & (df["unit_price"] > 0)
].copy()


# KPI calculations

total_revenue = sales_df["revenue"].sum()

total_orders = sales_df["invoice_no"].nunique()

total_customers = (
    sales_df["customer_id"]
    .dropna()
    .nunique()
)

order_revenue_df = (
    sales_df
    .groupby("invoice_no", as_index=False)["revenue"]
    .sum()
)

average_order_value = order_revenue_df["revenue"].mean()

total_invoice_count = df["invoice_no"].nunique()

cancelled_invoice_count = (
    df.loc[df["is_cancellation"], "invoice_no"]
    .nunique()
)

cancellation_rate = (
    cancelled_invoice_count
    / total_invoice_count
    * 100
)


# KPI display

st.subheader("Business Overview")

kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = st.columns(5)

with kpi_1:
    st.metric(
        label="Total Revenue",
        value=f"£{total_revenue:,.0f}",
    )

with kpi_2:
    st.metric(
        label="Orders",
        value=f"{total_orders:,}",
    )

with kpi_3:
    st.metric(
        label="Identified Customers",
        value=f"{total_customers:,}",
    )

with kpi_4:
    st.metric(
        label="Average Order Value",
        value=f"£{average_order_value:,.2f}",
    )

with kpi_5:
    st.metric(
        label="Cancellation Rate",
        value=f"{cancellation_rate:.2f}%",
    )
st.subheader("Monthly Revenue Trend")

monthly_revenue_df = (
    sales_df
    .groupby("year_month", as_index=False)["revenue"]
    .sum()
    .rename(columns={"revenue": "monthly_revenue"})
    .sort_values("year_month")
)

st.line_chart(
    monthly_revenue_df,
    x="year_month",
    y="monthly_revenue",
)
st.caption(
    "Note: December 2011 is incomplete because the dataset ends on December 9, 2011."
)

st.subheader("Top 10 Products by Revenue")

operational_entries = [
    "DOTCOM POSTAGE",
    "POSTAGE",
    "AMAZON FEE",
    "Adjust bad debt",
]

product_sales_df = sales_df[
    ~sales_df["description"].isin(operational_entries)
].copy()

top_products_df = (
    product_sales_df
    .groupby("description", as_index=False)["revenue"]
    .sum()
    .rename(columns={"revenue": "product_revenue"})
    .sort_values("product_revenue", ascending=False)
    .head(10)
    .sort_values("product_revenue", ascending=True)
)

product_chart = px.bar(
    top_products_df,
    x="product_revenue",
    y="description",
    orientation="h",
    labels={
        "product_revenue": "Revenue",
        "description": "Product",
    },
)

product_chart.update_layout(
    yaxis_title=None,
    xaxis_title="Revenue (£)",
    height=500,
)

st.plotly_chart(
    product_chart,
    use_container_width=True,
)
st.subheader("Customer Behavior")

customer_orders_df = (
    sales_df
    .dropna(subset=["customer_id"])
    .groupby("customer_id", as_index=False)["invoice_no"]
    .nunique()
    .rename(columns={"invoice_no": "number_of_orders"})
)

one_time_customers = (
    customer_orders_df["number_of_orders"] == 1
).sum()

repeat_customers = (
    customer_orders_df["number_of_orders"] > 1
).sum()

repeat_customer_rate = (
    repeat_customers
    / len(customer_orders_df)
    * 100
)

customer_type_df = pd.DataFrame({
    "customer_type": [
        "One-time customers",
        "Repeat customers",
    ],
    "number_of_customers": [
        one_time_customers,
        repeat_customers,
    ],
})

customer_chart = px.bar(
    customer_type_df,
    x="customer_type",
    y="number_of_customers",
    labels={
        "customer_type": "Customer Type",
        "number_of_customers": "Number of Customers",
    },
)

customer_chart.update_layout(
    xaxis_title=None,
    yaxis_title="Customers",
    height=400,
)

customer_col_1, customer_col_2 = st.columns([1, 2])

with customer_col_1:
    st.metric(
        label="Repeat Customer Rate",
        value=f"{repeat_customer_rate:.2f}%",
    )

    st.write(f"One-time customers: **{one_time_customers:,}**")
    st.write(f"Repeat customers: **{repeat_customers:,}**")

with customer_col_2:
    st.plotly_chart(
        customer_chart,
        use_container_width=True,
    )