from pathlib import Path

import pandas as pd
import streamlit as st

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Belal's Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# Load Sales Data
# -------------------------------------------------
@st.cache_data
def load_data():
    file_path = Path("data/sales.csv")
    return pd.read_csv(file_path)

df = load_data()

# -------------------------------------------------
# Calculate KPIs
# -------------------------------------------------
df["Revenue"] = df["Quantity"] * df["Price"]

total_revenue = df["Revenue"].sum()
total_units = df["Quantity"].sum()
total_products = df["Product"].nunique()
average_sale = df["Revenue"].mean()

# -------------------------------------------------
# Dashboard Title
# -------------------------------------------------
st.title("📊 Belal's Sales Dashboard")

st.success("Sales data loaded successfully!")

# -------------------------------------------------
# KPI Cards
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
col2.metric("📦 Units Sold", total_units)
col3.metric("📱 Products", total_products)
col4.metric("📈 Average Sale", f"${average_sale:,.0f}")

st.divider()

# -------------------------------------------------
# Sales Data Table
# -------------------------------------------------
st.subheader("📋 Sales Data")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)