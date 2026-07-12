import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Belal's Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Belal's Sales Dashboard")
st.caption("Interactive Sales Performance Dashboard")

# -----------------------
# Load Data
# -----------------------
df = pd.read_csv("data/sales.csv")

df["Date"] = pd.to_datetime(df["Date"])
df["Revenue"] = df["Quantity"] * df["Price"]

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("Filters")

selected_categories = st.sidebar.multiselect(
    "Choose Categories",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique()),
)

selected_products = st.sidebar.multiselect(
    "Choose Products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique()),
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Date"].min().date(),
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Date"].max().date(),
)

if start_date > end_date:
    st.error("Start date cannot be after end date.")
    st.stop()

# -----------------------
# Apply Filters
# -----------------------
filtered_df = df[
    df["Category"].isin(selected_categories)
    & df["Product"].isin(selected_products)
    & (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No data available.")
    st.stop()

# -----------------------
# KPIs
# -----------------------
total_revenue = filtered_df["Revenue"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_products = filtered_df["Product"].nunique()
average_sale = filtered_df["Revenue"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"${total_revenue:,.0f}")
col2.metric("🛒 Units Sold", f"{total_quantity:,}")
col3.metric("📦 Products", total_products)
col4.metric("📊 Average Sale", f"${average_sale:,.0f}")

st.divider()

# -----------------------
# Sales Table
# -----------------------
st.subheader("Sales Data")

display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%d %b %Y")
display_df["Price"] = display_df["Price"].map("${:,.2f}".format)
display_df["Revenue"] = display_df["Revenue"].map("${:,.2f}".format)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------
# Revenue by Product
# -----------------------
st.subheader("Revenue by Product")

revenue_by_product = (
    filtered_df.groupby("Product", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)

fig1 = px.bar(
    revenue_by_product,
    x="Product",
    y="Revenue",
    text_auto=True,
)

fig1.update_layout(
    height=450,
    xaxis_title="Product",
    yaxis_title="Revenue ($)",
)

fig1.update_xaxes(tickangle=-30)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# -----------------------
# Sales by Category
# -----------------------
st.subheader("Sales by Category")

category_sales = (
    filtered_df.groupby("Category", as_index=False)["Revenue"]
    .sum()
)

fig2 = px.pie(
    category_sales,
    values="Revenue",
    names="Category",
    hole=0.5,
)

fig2.update_layout(height=450)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -----------------------
# Revenue Over Time
# -----------------------
st.subheader("Revenue Over Time")

revenue_over_time = (
    filtered_df.groupby("Date", as_index=False)["Revenue"]
    .sum()
    .sort_values("Date")
)

fig3 = px.line(
    revenue_over_time,
    x="Date",
    y="Revenue",
    markers=True,
)

fig3.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="Revenue ($)",
)

fig3.update_xaxes(
    tickformat="%d %b",
    nticks=7,
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------
# Top Selling Products
# -----------------------
st.subheader("🏆 Top Selling Products")

top_products = (
    filtered_df.groupby("Product")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.dataframe(
    top_products,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------
# Download Report
# -----------------------
st.subheader("📥 Download Report")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Sales CSV",
    data=csv,
    file_name="filtered_sales_report.csv",
    mime="text/csv",
)