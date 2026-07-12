from __future__ import annotations

import pandas as pd

from src.data_loader import normalize_sales_dataframe


def test_normalize_sales_dataframe_rejects_negative_values() -> None:
    invalid_df = pd.DataFrame(
        {
            "Date": ["2026-07-01"],
            "Product": ["Laptop"],
            "Category": ["Electronics"],
            "Quantity": [-1],
            "Price": [1500],
        }
    )

    try:
        normalize_sales_dataframe(invalid_df)
    except ValueError as exc:
        assert "Negative Quantity or Price" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative numeric values.")
