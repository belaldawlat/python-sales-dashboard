from __future__ import annotations

import pandas as pd

from src.metrics import calculate_kpi_metrics


def test_calculate_kpi_metrics_returns_expected_values() -> None:
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-03"]),
            "Product": ["Laptop", "Laptop", "Phone"],
            "Category": ["Electronics", "Electronics", "Electronics"],
            "Quantity": [2, 1, 3],
            "Price": [1500, 1500, 900],
            "Revenue": [3000, 1500, 2700],
        }
    )

    metrics = calculate_kpi_metrics(df)

    assert metrics["total_revenue"] == 7200.0
    assert metrics["units_sold"] == 6
    assert metrics["number_of_products"] == 2
    assert metrics["average_sale"] == 2400.0
    assert metrics["best_selling_product"] == "Laptop"
    assert metrics["best_performing_category"] == "Electronics"
