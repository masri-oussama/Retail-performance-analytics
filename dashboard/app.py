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

st.caption(
    "Explore revenue, orders, customers, products, countries, "
    "and cancellation behavior from online retail transactions."
)
st.info(
    "The dataset covers transactions from December 2010 to December 2011. "
    "December 2011 is incomplete because records end on December 9."
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
st.sidebar.header("Filters")

minimum_date = df["invoice_date"].min().date()
maximum_date = df["invoice_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

country_options = sorted(df["country"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=country_options,
    default=country_options,
)
filtered_df = df.copy()

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["invoice_date"].dt.date.between(
            start_date,
            end_date,
        )
    ]

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["country"].isin(selected_countries)
    ]


sales_df = filtered_df[
    (filtered_df["quantity"] > 0)
    & (~filtered_df["is_cancellation"])
    & (filtered_df["unit_price"] > 0)
].copy()

if filtered_df.empty:
    st.warning(
        "No records match the selected filters. "
        "Please choose another date range or country."
    )
    st.stop()

if sales_df.empty:
    st.warning(
        "No successful sales match the selected filters."
    )
    st.stop()

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

total_invoice_count = filtered_df["invoice_no"].nunique()

cancelled_invoice_count = (
    filtered_df.loc[
        filtered_df["is_cancellation"],
        "invoice_no",
    ]
    .nunique()
)

cancellation_rate = (
    cancelled_invoice_count / total_invoice_count * 100
    if total_invoice_count > 0
    else 0
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
if (
    not sales_df.empty
    and sales_df["invoice_date"].max().year == 2011
    and sales_df["invoice_date"].max().month == 12
    and sales_df["invoice_date"].max().day < 31
):
    st.caption(
        "Note: December 2011 is incomplete because "
        "the dataset ends on December 9, 2011."
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

st.subheader("Country Performance")

country_revenue_df = (
    sales_df
    .groupby("country", as_index=False)
    .agg(
        total_revenue=("revenue", "sum"),
        number_of_orders=("invoice_no", "nunique"),
        identified_customers=("customer_id", "nunique"),
    )
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

country_chart = px.bar(
    country_revenue_df.sort_values("total_revenue"),
    x="total_revenue",
    y="country",
    orientation="h",
    hover_data=[
        "number_of_orders",
        "identified_customers",
    ],
    labels={
        "total_revenue": "Revenue",
        "country": "Country",
        "number_of_orders": "Orders",
        "identified_customers": "Customers",
    },
)

country_chart.update_layout(
    yaxis_title=None,
    xaxis_title="Revenue (£)",
    height=500,
)

st.plotly_chart(
    country_chart,
    use_container_width=True,
)

st.divider()

st.caption(
    "Built with Python, Pandas, Plotly, and Streamlit. "
    "Created as part of a Data Science and AI portfolio project."
)