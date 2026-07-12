from __future__ import annotations

from src.data_loader import load_sales_data
from src.filters import apply_filters


def test_apply_filters_returns_expected_subset() -> None:
    df = load_sales_data()

    filters = {
        "categories": ["Electronics"],
        "products": ["Laptop"],
        "date_range": (df["Date"].min().date(), df["Date"].max().date()),
        "search_term": "",
    }

    filtered_df = apply_filters(df, filters)

    assert filtered_df["Category"].eq("Electronics").all()
    assert filtered_df["Product"].eq("Laptop").all()


def test_apply_filters_search_returns_empty_for_unknown_term() -> None:
    df = load_sales_data()

    filters = {
        "categories": [],
        "products": [],
        "date_range": (df["Date"].min().date(), df["Date"].max().date()),
        "search_term": "definitely-not-a-real-product",
    }

    filtered_df = apply_filters(df, filters)

    assert filtered_df.empty
