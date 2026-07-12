from __future__ import annotations

from html import escape
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils import format_currency, format_number


def render_kpi_cards(metrics: Dict[str, float | int | str]) -> None:
    """Render a premium metric-card grid for the main KPIs.

    The UI values are escaped before insertion into HTML so user-supplied
    product or category data cannot be interpreted as markup later.
    """
    cards = [
        ("Total Revenue", format_currency(metrics["total_revenue"]), "Overall revenue in the current view."),
        ("Units Sold", format_number(metrics["units_sold"]), "All units sold across filtered rows."),
        ("Number of Products", format_number(metrics["number_of_products"]), "Distinct products in the filtered data."),
        ("Average Sale", format_currency(metrics["average_sale"]), "Average revenue per transaction."),
        ("Best-Selling Product", str(metrics["best_selling_product"]), "Largest quantity sold by product."),
        ("Best-Performing Category", str(metrics["best_performing_category"]), "Highest revenue category."),
    ]

    card_html = ""
    for label, value, subtitle in cards:
        safe_label = escape(str(label))
        safe_value = escape(str(value))
        safe_subtitle = escape(str(subtitle))
        card_html += (
            f'<div class="metric-card">'
            f'<div class="metric-label">{safe_label}</div>'
            f'<div class="metric-value">{safe_value}</div>'
            f'<div class="metric-subtitle">{safe_subtitle}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="metric-grid">{card_html}</div>', unsafe_allow_html=True)


def create_revenue_by_product_chart(df: pd.DataFrame):
    """Return a horizontal product revenue chart."""
    chart_df = (
        df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    fig = px.bar(
        chart_df,
        x="Revenue",
        y="Product",
        color="Revenue",
        text="Revenue",
        orientation="h",
        template="plotly_dark",
        color_continuous_scale="Viridis",
        title="Revenue by Product",
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", cliponaxis=False)
    fig.update_layout(
        height=460,
        margin=dict(l=15, r=15, t=55, b=15),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        xaxis_title="Revenue ($)",
        yaxis_title="Product",
        showlegend=False,
    )
    return fig


def create_revenue_by_category_chart(df: pd.DataFrame):
    """Return a donut chart of category revenue distribution."""
    chart_df = df.groupby("Category", as_index=False)["Revenue"].sum()
    fig = px.pie(
        chart_df,
        values="Revenue",
        names="Category",
        hole=0.55,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Revenue by Category",
    )
    fig.update_traces(textinfo="percent+label", hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<extra></extra>")
    fig.update_layout(
        height=460,
        margin=dict(l=15, r=15, t=55, b=15),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
    )
    return fig


def create_revenue_over_time_chart(df: pd.DataFrame, trend: str = "Daily"):
    """Return a line chart that can be aggregated daily, weekly, or monthly."""
    chart_df = df.copy()
    chart_df["Date"] = pd.to_datetime(chart_df["Date"])

    if trend == "Weekly":
        chart_df["Date"] = chart_df["Date"].dt.to_period("W-MON").dt.to_timestamp()
    elif trend == "Monthly":
        chart_df["Date"] = chart_df["Date"].dt.to_period("M").dt.to_timestamp()

    chart_df = chart_df.groupby("Date", as_index=False)["Revenue"].sum().sort_values("Date")
    fig = px.line(
        chart_df,
        x="Date",
        y="Revenue",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=["#60a5fa"],
        title=f"Revenue Over Time ({trend})",
    )
    fig.update_layout(
        height=450,
        margin=dict(l=15, r=15, t=55, b=20),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
    )
    return fig


def create_units_by_product_chart(df: pd.DataFrame):
    """Return a units-sold chart for each product."""
    chart_df = (
        df.groupby("Product", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
    )
    fig = px.bar(
        chart_df,
        x="Product",
        y="Quantity",
        color="Quantity",
        text="Quantity",
        template="plotly_dark",
        color_continuous_scale="Cividis",
        title="Units Sold by Product",
    )
    fig.update_traces(texttemplate="%{text:,}", cliponaxis=False)
    fig.update_layout(
        height=460,
        margin=dict(l=15, r=15, t=55, b=15),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        xaxis_title="Product",
        yaxis_title="Units Sold",
        showlegend=False,
    )
    return fig


def render_sales_table(df: pd.DataFrame) -> None:
    """Render a filtered sales table with clean presentation."""
    display_df = df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    display_df["Price"] = display_df["Price"].map(lambda value: f"${value:,.2f}")
    display_df["Revenue"] = display_df["Revenue"].map(lambda value: f"${value:,.2f}")
    st.dataframe(display_df, width="stretch", hide_index=True)
