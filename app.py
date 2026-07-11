import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Belal's Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Belal's Sales Dashboard")

# Load data
df = pd.read_csv("data/sales.csv")

# Prepare data
df["Date"] = pd.to_datetime(df["Date"])
df["Revenue"] = df["Quantity"] * df["Price"]

# Sidebar filters
st.sidebar.header("Filters")

selected_categories = st.sidebar.multiselect(
    "Choose categories",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique()),
)

selected_products = st.sidebar.multiselect(
    "Choose products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique()),
)

start_date = st.sidebar.date_input(
    "Start date",
    value=df["Date"].min().date(),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
)

end_date = st.sidebar.date_input(
    "End date",
    value=df["Date"].max().date(),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
)

# Validate date range
if start_date > end_date:
    st.error("Start date cannot be after the end date.")
    st.stop()

# Apply filters
filtered_df = df[
    df["Category"].isin(selected_categories)
    & df["Product"].isin(selected_products)
    & (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

# KPI calculations
total_revenue = filtered_df["Revenue"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_products = filtered_df["Product"].nunique()
average_sale = filtered_df["Revenue"].mean() if not filtered_df.empty else 0

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"${total_revenue:,.0f}")
col2.metric("🛒 Units Sold", f"{total_quantity:,}")
col3.metric("📦 Products", total_products)
col4.metric("📊 Average Sale", f"${average_sale:,.0f}")

st.divider()

# Empty-result message
if filtered_df.empty:
    st.warning("No sales data matches the selected filters.")
    st.stop()

# Clean date display
display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

# Sales table
st.subheader("Sales Data")

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)

st.divider()

# Revenue by product
st.subheader("Revenue by Product")

revenue_by_product = (
    filtered_df.groupby("Product", as_index=False)["Revenue"]
    .sum()
    .set_index("Product")
)

st.bar_chart(revenue_by_product)

st.divider()

# Revenue over time
st.subheader("Revenue Over Time")

revenue_over_time = (
    filtered_df.groupby("Date", as_index=False)["Revenue"]
    .sum()
    .set_index("Date")
)

st.line_chart(revenue_over_time)