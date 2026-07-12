from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_loader import load_sales_data, normalize_sales_dataframe


def test_load_default_sales_dataset_returns_expected_schema() -> None:
    df = load_sales_data()

    assert not df.empty
    assert list(df.columns) == [
        "Date",
        "Product",
        "Category",
        "Quantity",
        "Price",
        "Revenue",
    ]
    assert "Revenue" in df.columns
    assert (df["Revenue"] >= 0).all()


def test_normalize_sales_dataframe_rejects_missing_required_columns() -> None:
    invalid_df = pd.DataFrame({"Date": ["2026-07-01"], "Product": ["Laptop"]})

    try:
        normalize_sales_dataframe(invalid_df)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid CSV schema.")


def test_load_sales_data_supports_uploaded_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "uploaded_sales.csv"
    csv_path.write_text(
        "Date,Product,Category,Quantity,Price\n"
        "2026-07-01,Laptop,Electronics,2,1500\n"
        "2026-07-02,Phone,Electronics,1,900\n",
        encoding="utf-8",
    )

    df = load_sales_data(csv_path)

    assert len(df) == 2
    assert df["Revenue"].sum() == 3900
