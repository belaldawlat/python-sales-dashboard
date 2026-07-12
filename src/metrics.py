from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd


def calculate_kpi_metrics(df: pd.DataFrame) -> Dict[str, float | int | str]:
    """Compute the headline KPI values for the filtered dataset."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "units_sold": 0,
            "number_of_products": 0,
            "average_sale": 0.0,
            "best_selling_product": "N/A",
            "best_performing_category": "N/A",
        }

    total_revenue = float(df["Revenue"].sum())
    units_sold = int(df["Quantity"].sum())
    number_of_products = int(df["Product"].nunique())
    average_sale = float(df["Revenue"].mean()) if not df.empty else 0.0

    product_units = df.groupby("Product")["Quantity"].sum().sort_values(ascending=False)
    best_selling_product = product_units.index[0] if not product_units.empty else "N/A"

    category_revenue = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    best_performing_category = category_revenue.index[0] if not category_revenue.empty else "N/A"

    return {
        "total_revenue": total_revenue,
        "units_sold": units_sold,
        "number_of_products": number_of_products,
        "average_sale": average_sale,
        "best_selling_product": best_selling_product,
        "best_performing_category": best_performing_category,
    }


def build_summary_report(df: pd.DataFrame) -> pd.DataFrame:
    """Create a simple summary CSV dataset for export."""
    metrics = calculate_kpi_metrics(df)
    records = [
        {"Metric": "Total Revenue", "Value": metrics["total_revenue"]},
        {"Metric": "Units Sold", "Value": metrics["units_sold"]},
        {"Metric": "Number of Products", "Value": metrics["number_of_products"]},
        {"Metric": "Average Sale", "Value": metrics["average_sale"]},
        {"Metric": "Best Selling Product", "Value": metrics["best_selling_product"]},
        {"Metric": "Best Performing Category", "Value": metrics["best_performing_category"]},
    ]
    return pd.DataFrame(records)


def build_top_bottom_products(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return ranked product summaries for the top and bottom five products."""
    product_summary = (
        df.groupby("Product", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Units_Sold=("Quantity", "sum"))
        .sort_values(["Revenue", "Units_Sold"], ascending=False)
        .reset_index(drop=True)
    )

    top_df = product_summary.head(5).copy()
    bottom_df = product_summary.sort_values(["Revenue", "Units_Sold"], ascending=True).head(5).copy()

    return top_df, bottom_df
