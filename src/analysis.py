import pandas as pd


OPERATIONAL_ENTRIES = [
    "DOTCOM POSTAGE",
    "POSTAGE",
    "AMAZON FEE",
    "Adjust bad debt",
]


def calculate_kpis(
    df: pd.DataFrame,
    sales_df: pd.DataFrame,
) -> dict:
    """Calculate headline business KPIs."""

    total_revenue = sales_df["revenue"].sum()

    total_orders = sales_df["invoice_no"].nunique()

    total_customers = (
        sales_df["customer_id"]
        .dropna()
        .nunique()
    )

    order_revenue = (
        sales_df
        .groupby("invoice_no")["revenue"]
        .sum()
    )

    average_order_value = (
        order_revenue.mean()
        if not order_revenue.empty
        else 0
    )

    total_invoices = df["invoice_no"].nunique()

    cancelled_invoices = (
        df.loc[
            df["is_cancellation"],
            "invoice_no",
        ]
        .nunique()
    )

    cancellation_rate = (
        cancelled_invoices
        / total_invoices
        * 100
        if total_invoices > 0
        else 0
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_order_value": average_order_value,
        "cancellation_rate": cancellation_rate,
    }


def get_monthly_revenue(
    sales_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly revenue from successful sales."""

    return (
        sales_df
        .groupby(
            "year_month",
            as_index=False,
        )["revenue"]
        .sum()
        .rename(
            columns={
                "revenue": "monthly_revenue"
            }
        )
        .sort_values("year_month")
    )


def get_top_products(
    sales_df: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Return the top products by revenue.

    Operational entries such as postage and fees
    are excluded from product analysis.
    """

    product_sales_df = sales_df[
        ~sales_df["description"].isin(
            OPERATIONAL_ENTRIES
        )
    ].copy()

    return (
        product_sales_df
        .groupby(
            "description",
            as_index=False,
        )["revenue"]
        .sum()
        .rename(
            columns={
                "revenue": "product_revenue"
            }
        )
        .sort_values(
            "product_revenue",
            ascending=False,
        )
        .head(top_n)
        .sort_values(
            "product_revenue",
            ascending=True,
        )
    )


def get_customer_behavior(
    sales_df: pd.DataFrame,
) -> dict:
    """
    Calculate one-time and repeat-customer statistics.
    """

    customer_orders_df = (
        sales_df
        .dropna(
            subset=["customer_id"]
        )
        .groupby(
            "customer_id",
            as_index=False,
        )["invoice_no"]
        .nunique()
        .rename(
            columns={
                "invoice_no": "number_of_orders"
            }
        )
    )

    one_time_customers = (
        customer_orders_df[
            "number_of_orders"
        ] == 1
    ).sum()

    repeat_customers = (
        customer_orders_df[
            "number_of_orders"
        ] > 1
    ).sum()

    total_customers = len(
        customer_orders_df
    )

    repeat_customer_rate = (
        repeat_customers
        / total_customers
        * 100
        if total_customers > 0
        else 0
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

    return {
        "one_time_customers": one_time_customers,
        "repeat_customers": repeat_customers,
        "repeat_customer_rate": repeat_customer_rate,
        "customer_type_df": customer_type_df,
    }


def get_country_performance(
    sales_df: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """Calculate revenue, orders, and customers by country."""

    return (
        sales_df
        .groupby(
            "country",
            as_index=False,
        )
        .agg(
            total_revenue=(
                "revenue",
                "sum",
            ),
            number_of_orders=(
                "invoice_no",
                "nunique",
            ),
            identified_customers=(
                "customer_id",
                "nunique",
            ),
        )
        .sort_values(
            "total_revenue",
            ascending=False,
        )
        .head(top_n)
    )