from __future__ import annotations

import io
from typing import Any

import pandas as pd
import streamlit as st


def format_currency(value: Any) -> str:
    """Return a user-friendly currency string."""
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "$0"


def format_number(value: Any) -> str:
    """Return a user-friendly integer string."""
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return "0"


def get_download_button_csv(df: pd.DataFrame, label: str, file_name: str):
    """Create a download button with a reliable CSV payload."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return st.download_button(
        label=label,
        data=csv_buffer.getvalue(),
        file_name=file_name,
        mime="text/csv",
        width="stretch",
    )
