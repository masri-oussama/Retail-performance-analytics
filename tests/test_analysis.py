import pandas as pd

from src.analysis import (
    calculate_kpis,
    get_customer_behavior,
    get_monthly_revenue,
    get_top_products,
)


def test_calculate_kpis():
    df = pd.DataFrame({
        "invoice_no": ["1", "1", "2", "C3"],
        "customer_id": [101, 101, 102, 103],
        "revenue": [10.0, 20.0, 30.0, -15.0],
        "is_cancellation": [False, False, False, True],
    })

    sales_df = df[
        ~df["is_cancellation"]
    ].copy()

    result = calculate_kpis(
        df,
        sales_df,
    )

    assert result["total_revenue"] == 60.0
    assert result["total_orders"] == 2
    assert result["total_customers"] == 2
    assert result["average_order_value"] == 30.0


def test_cancellation_rate():
    df = pd.DataFrame({
        "invoice_no": ["1", "2", "C3", "C4"],
        "customer_id": [101, 102, 103, 104],
        "revenue": [10.0, 20.0, -10.0, -20.0],
        "is_cancellation": [
            False,
            False,
            True,
            True,
        ],
    })

    sales_df = df[
        ~df["is_cancellation"]
    ].copy()

    result = calculate_kpis(
        df,
        sales_df,
    )

    assert result["cancellation_rate"] == 50.0


def test_monthly_revenue():
    sales_df = pd.DataFrame({
        "year_month": [
            "2026-01",
            "2026-01",
            "2026-02",
        ],
        "revenue": [
            10.0,
            20.0,
            40.0,
        ],
    })

    result = get_monthly_revenue(
        sales_df
    )

    assert len(result) == 2

    january_revenue = result.loc[
        result["year_month"] == "2026-01",
        "monthly_revenue",
    ].iloc[0]

    february_revenue = result.loc[
        result["year_month"] == "2026-02",
        "monthly_revenue",
    ].iloc[0]

    assert january_revenue == 30.0
    assert february_revenue == 40.0


def test_top_products_excludes_operational_entries():
    sales_df = pd.DataFrame({
        "description": [
            "Normal Product",
            "Normal Product",
            "POSTAGE",
            "AMAZON FEE",
        ],
        "revenue": [
            100.0,
            50.0,
            500.0,
            1000.0,
        ],
    })

    result = get_top_products(
        sales_df,
        top_n=10,
    )

    assert "POSTAGE" not in result["description"].values
    assert "AMAZON FEE" not in result["description"].values
    assert "Normal Product" in result["description"].values


def test_customer_behavior():
    sales_df = pd.DataFrame({
        "customer_id": [
            101,
            101,
            102,
            103,
            103,
        ],
        "invoice_no": [
            "1",
            "2",
            "3",
            "4",
            "4",
        ],
    })

    result = get_customer_behavior(
        sales_df
    )

    assert result["one_time_customers"] == 2
    assert result["repeat_customers"] == 1

    assert round(
        result["repeat_customer_rate"],
        2,
    ) == 33.33