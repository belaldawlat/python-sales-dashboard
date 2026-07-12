from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """Render the dashboard sidebar filters and return the chosen values."""
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    categories = sorted(df["Category"].dropna().astype(str).unique())
    products = sorted(df["Product"].dropna().astype(str).unique())

    st.sidebar.markdown("### Filters")
    selected_categories = st.sidebar.multiselect(
        "Category",
        options=categories,
        default=categories,
        key="dashboard_category_filter",
    )
    selected_products = st.sidebar.multiselect(
        "Product",
        options=products,
        default=products,
        key="dashboard_product_filter",
    )
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="dashboard_date_range",
    )
    search_term = st.sidebar.text_input(
        "Search",
        placeholder="Search product or category",
        key="dashboard_search_term",
    )

    reset_button = st.sidebar.button("Reset filters", width="stretch")
    if reset_button:
        st.session_state["dashboard_category_filter"] = categories
        st.session_state["dashboard_product_filter"] = products
        st.session_state["dashboard_search_term"] = ""
        st.session_state["dashboard_date_range"] = (min_date, max_date)
        st.rerun()

    return {
        "categories": selected_categories,
        "products": selected_products,
        "date_range": date_range,
        "search_term": search_term,
    }


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply sidebar selections to the base dataframe."""
    filtered_df = df.copy()

    selected_categories = filters.get("categories", [])
    selected_products = filters.get("products", [])
    start_date, end_date = filters.get("date_range", (df["Date"].min().date(), df["Date"].max().date()))
    search_term = str(filters.get("search_term", "")).strip().lower()

    if selected_categories:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
    if selected_products:
        filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date)
            & (filtered_df["Date"].dt.date <= end_date)
        ]
    if search_term:
        filtered_df = filtered_df[
            filtered_df["Product"].astype(str).str.lower().str.contains(search_term)
            | filtered_df["Category"].astype(str).str.lower().str.contains(search_term)
        ]

    return filtered_df.reset_index(drop=True)
