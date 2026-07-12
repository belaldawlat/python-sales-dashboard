from __future__ import annotations

import streamlit as st

from src.charts import (
    create_revenue_by_category_chart,
    create_revenue_by_product_chart,
    create_revenue_over_time_chart,
    create_units_by_product_chart,
    render_kpi_cards,
    render_sales_table,
)
from src.data_loader import load_sales_data
from src.filters import apply_filters, render_sidebar_filters
from src.metrics import build_summary_report, build_top_bottom_products, calculate_kpi_metrics
from src.utils import get_download_button_csv

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(
    page_title="Belal Sales Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #020617 0%, #111827 100%);
        color: #e5e7eb;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.5rem 0;
    }
    .metric-card {
        background: linear-gradient(160deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.45);
    }
    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #93c5fd;
        margin-bottom: 0.7rem;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.45rem;
    }
    .metric-subtitle {
        font-size: 0.82rem;
        color: #94a3b8;
    }
    .section-label {
        font-size: 0.9rem;
        color: #7dd3fc;
        font-weight: 700;
        margin-bottom: 0.55rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Header
# -----------------------
st.title("📈 Belal Sales Intelligence Dashboard")
st.caption("Portfolio-grade sales analytics with clean filters, premium visuals, and export-ready reporting.")

# -----------------------
# Data source selection
# -----------------------
st.sidebar.markdown("### Data source")
source_option = st.sidebar.radio(
    "Choose dataset",
    options=["Default sales data", "Upload CSV file"],
    horizontal=True,
)

uploaded_file = None
if source_option == "Upload CSV file":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a sales CSV file",
        type=["csv"],
        help="Required columns: Date, Product, Category, Quantity, Price",
    )
    if uploaded_file is None:
        st.info("Choose a CSV file to use the upload mode, or switch back to the default sales dataset.")
        st.stop()

# -----------------------
# Load data with safe validation
# -----------------------
try:
    df = load_sales_data(uploaded_file)
except Exception as exc:
    st.error(f"Unable to load the sales data: {exc}")
    st.info("Please upload a CSV file that contains Date, Product, Category, Quantity, and Price columns.")
    st.stop()

# -----------------------
# Sidebar filters
# -----------------------
filters = render_sidebar_filters(df)
filtered_df = apply_filters(df, filters)

if filtered_df.empty:
    st.warning("No sales records match the current filters. Try widening the date range or clearing the product/category selection.")
    st.stop()

# -----------------------
# KPI metrics
# -----------------------
metrics = calculate_kpi_metrics(filtered_df)
render_kpi_cards(metrics)

st.subheader("Analysis")

# -----------------------
# Trend selector and charts grid
# -----------------------
trend_selection = st.radio(
    "Revenue trend view",
    options=["Daily", "Weekly", "Monthly"],
    horizontal=True,
    key="trend_selector",
)

chart_col_1, chart_col_2 = st.columns(2)
with chart_col_1:
    st.plotly_chart(create_revenue_by_product_chart(filtered_df), width="stretch")
with chart_col_2:
    st.plotly_chart(create_revenue_by_category_chart(filtered_df), width="stretch")

chart_col_3, chart_col_4 = st.columns(2)
with chart_col_3:
    st.plotly_chart(create_units_by_product_chart(filtered_df), width="stretch")
with chart_col_4:
    st.plotly_chart(create_revenue_over_time_chart(filtered_df, trend_selection), width="stretch")

# -----------------------
# Product ranking tables
# -----------------------
ranking_col_1, ranking_col_2 = st.columns(2)
top_products_df, bottom_products_df = build_top_bottom_products(filtered_df)

with ranking_col_1:
    st.subheader("Top 5 products")
    st.dataframe(top_products_df, width="stretch", hide_index=True)
with ranking_col_2:
    st.subheader("Bottom 5 products")
    st.dataframe(bottom_products_df, width="stretch", hide_index=True)

# -----------------------
# Detailed sales data
# -----------------------
st.subheader("Detailed filtered sales table")
render_sales_table(filtered_df)

# -----------------------
# Exports section
# -----------------------
st.subheader("Exports")
export_col_1, export_col_2 = st.columns(2)
with export_col_1:
    get_download_button_csv(
        filtered_df,
        label="Download filtered CSV",
        file_name="filtered_sales_export.csv",
    )
with export_col_2:
    summary_report_df = build_summary_report(filtered_df)
    get_download_button_csv(
        summary_report_df,
        label="Download summary report CSV",
        file_name="sales_summary_report.csv",
    )