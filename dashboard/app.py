from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import (
    calculate_kpis,
    get_country_performance,
    get_customer_behavior,
    get_monthly_revenue,
    get_top_products,
)


DATA_PATH = Path(
    "data/dashboard_transactions.csv.gz"
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Retail Performance Analytics",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("Retail Performance Analytics")

st.caption(
    "Explore revenue, orders, customers, products, countries, "
    "and cancellation behavior from online retail transactions."
)

st.info(
    "The dataset covers transactions from December 2010 "
    "to December 2011. December 2011 is incomplete because "
    "records end on December 9."
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

@st.cache_data
def load_data(
    path: Path,
) -> pd.DataFrame:
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
        "exists in the repository."
    )
    st.stop()

except Exception as error:
    st.error(
        f"An error occurred while loading the data: {error}"
    )
    st.stop()


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Filters")

minimum_date = (
    df["invoice_date"]
    .min()
    .date()
)

maximum_date = (
    df["invoice_date"]
    .max()
    .date()
)

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(
        minimum_date,
        maximum_date,
    ),
    min_value=minimum_date,
    max_value=maximum_date,
)

country_options = sorted(
    df["country"]
    .dropna()
    .unique()
)

selected_countries = (
    st.sidebar.multiselect(
        "Select countries",
        options=country_options,
        default=country_options,
    )
)


# --------------------------------------------------
# Apply filters
# --------------------------------------------------

filtered_df = df.copy()

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df[
            "invoice_date"
        ]
        .dt.date
        .between(
            start_date,
            end_date,
        )
    ]

if selected_countries:
    filtered_df = filtered_df[
        filtered_df[
            "country"
        ].isin(
            selected_countries
        )
    ]


# --------------------------------------------------
# Empty result safeguard
# --------------------------------------------------

if filtered_df.empty:
    st.warning(
        "No records match the selected filters. "
        "Please choose another date range or country."
    )
    st.stop()


# --------------------------------------------------
# Successful sales
# --------------------------------------------------

sales_df = filtered_df[
    (filtered_df["quantity"] > 0)
    & (~filtered_df["is_cancellation"])
    & (filtered_df["unit_price"] > 0)
].copy()


if sales_df.empty:
    st.warning(
        "No successful sales match the selected filters."
    )
    st.stop()


# --------------------------------------------------
# Business overview
# --------------------------------------------------

kpis = calculate_kpis(
    filtered_df,
    sales_df,
)

st.subheader("Business Overview")

kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = (
    st.columns(5)
)

with kpi_1:
    st.metric(
        label="Total Revenue",
        value=(
            f"£{kpis['total_revenue']:,.0f}"
        ),
    )

with kpi_2:
    st.metric(
        label="Orders",
        value=(
            f"{kpis['total_orders']:,}"
        ),
    )

with kpi_3:
    st.metric(
        label="Identified Customers",
        value=(
            f"{kpis['total_customers']:,}"
        ),
    )

with kpi_4:
    st.metric(
        label="Average Order Value",
        value=(
            f"£{kpis['average_order_value']:,.2f}"
        ),
    )

with kpi_5:
    st.metric(
        label="Cancellation Rate",
        value=(
            f"{kpis['cancellation_rate']:.2f}%"
        ),
    )


# --------------------------------------------------
# Monthly revenue
# --------------------------------------------------

st.subheader(
    "Monthly Revenue Trend"
)

monthly_revenue_df = (
    get_monthly_revenue(
        sales_df
    )
)

monthly_chart = px.line(
    monthly_revenue_df,
    x="year_month",
    y="monthly_revenue",
    markers=True,
    labels={
        "year_month": "Month",
        "monthly_revenue": "Revenue",
    },
)

monthly_chart.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (£)",
    height=450,
)

st.plotly_chart(
    monthly_chart,
    use_container_width=True,
)


maximum_selected_date = (
    sales_df[
        "invoice_date"
    ].max()
)

if (
    maximum_selected_date.year == 2011
    and maximum_selected_date.month == 12
    and maximum_selected_date.day < 31
):
    st.caption(
        "Note: December 2011 is incomplete because "
        "the dataset ends on December 9, 2011."
    )


# --------------------------------------------------
# Top products
# --------------------------------------------------

st.subheader(
    "Top 10 Products by Revenue"
)

top_products_df = get_top_products(
    sales_df,
    top_n=10,
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


# --------------------------------------------------
# Customer behavior
# --------------------------------------------------

st.subheader(
    "Customer Behavior"
)

customer_behavior = (
    get_customer_behavior(
        sales_df
    )
)

customer_type_df = (
    customer_behavior[
        "customer_type_df"
    ]
)

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

customer_col_1, customer_col_2 = (
    st.columns(
        [1, 2]
    )
)

with customer_col_1:
    st.metric(
        label="Repeat Customer Rate",
        value=(
            f"{customer_behavior['repeat_customer_rate']:.2f}%"
        ),
    )

    st.write(
        "One-time customers: "
        f"**{customer_behavior['one_time_customers']:,}**"
    )

    st.write(
        "Repeat customers: "
        f"**{customer_behavior['repeat_customers']:,}**"
    )

with customer_col_2:
    st.plotly_chart(
        customer_chart,
        use_container_width=True,
    )


# --------------------------------------------------
# Country performance
# --------------------------------------------------

st.subheader(
    "Country Performance"
)

country_performance_df = (
    get_country_performance(
        sales_df,
        top_n=10,
    )
)

country_chart = px.bar(
    country_performance_df.sort_values(
        "total_revenue"
    ),
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


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Built with Python, Pandas, Plotly, and Streamlit. "
    "Created as part of a Data Science and AI portfolio project."
)