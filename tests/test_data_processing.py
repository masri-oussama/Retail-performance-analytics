import pandas as pd

from src.data_processing import (
    add_business_features,
    standardize_column_names,
)


def test_standardize_column_names():
    df = pd.DataFrame(
        columns=["InvoiceNo", "UnitPrice", "CustomerID"]
    )

    result = standardize_column_names(df)

    assert "invoice_no" in result.columns
    assert "unit_price" in result.columns
    assert "customer_id" in result.columns


def test_revenue_calculation():
    df = pd.DataFrame({
        "invoice_no": ["123"],
        "quantity": [4],
        "unit_price": [2.5],
        "invoice_date": pd.to_datetime(
            ["2026-01-01 10:00:00"]
        ),
        "customer_id": [1],
    })

    result = add_business_features(df)

    assert result.loc[0, "revenue"] == 10.0


def test_cancellation_detection():
    df = pd.DataFrame({
        "invoice_no": ["C123", "124"],
        "quantity": [-1, 2],
        "unit_price": [10.0, 5.0],
        "invoice_date": pd.to_datetime(
            ["2026-01-01", "2026-01-02"]
        ),
        "customer_id": [1, 2],
    })

    result = add_business_features(df)

    assert bool(result.loc[0, "is_cancellation"]) is True
    assert bool(result.loc[1, "is_cancellation"]) is False