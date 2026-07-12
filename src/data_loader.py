from __future__ import annotations

from pathlib import Path
from typing import IO, Any, Optional, Union

import pandas as pd

REQUIRED_COLUMNS = ["Date", "Product", "Category", "Quantity", "Price"]
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sales.csv"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_ROWS = 100_000


def get_default_data_path() -> Path:
    """Return the default dataset location used by the dashboard."""
    return DEFAULT_DATA_PATH


def _ensure_safe_upload_size(data_source: Optional[Union[str, Path, IO[Any]]]) -> None:
    """Reject overly large uploads before the dashboard reads them."""
    if data_source is None:
        return

    if isinstance(data_source, (str, Path)):
        source_path = Path(data_source)
        if source_path.exists() and source_path.stat().st_size > MAX_UPLOAD_BYTES:
            raise ValueError(
                f"The uploaded CSV is too large. Please keep uploads below {MAX_UPLOAD_BYTES / (1024 * 1024):.0f} MB."
            )
        return

    if hasattr(data_source, "size") and isinstance(data_source.size, int):
        if data_source.size > MAX_UPLOAD_BYTES:
            raise ValueError(
                f"The uploaded CSV is too large. Please keep uploads below {MAX_UPLOAD_BYTES / (1024 * 1024):.0f} MB."
            )


def load_sales_data(data_source: Optional[Union[str, Path, IO[Any]]] = None) -> pd.DataFrame:
    """Load the default dataset or a user-uploaded CSV file.

    The function validates the schema, converts date and numeric columns safely,
    and computes a Revenue column automatically.
    """
    _ensure_safe_upload_size(data_source)

    try:
        if data_source is None:
            source_path = get_default_data_path()
            raw_df = pd.read_csv(source_path)
        elif isinstance(data_source, (str, Path)):
            source_path = Path(data_source)
            if not source_path.exists():
                raise FileNotFoundError(f"The CSV file does not exist: {source_path}")
            raw_df = pd.read_csv(source_path)
        else:
            if hasattr(data_source, "seek"):
                data_source.seek(0)
            raw_df = pd.read_csv(data_source)
    except FileNotFoundError as exc:
        raise FileNotFoundError(str(exc)) from exc
    except Exception as exc:
        raise ValueError(
            "Unable to read the CSV file. Please upload a valid comma-separated value file."
        ) from exc

    if raw_df.shape[0] > MAX_ROWS:
        raise ValueError(
            f"The uploaded CSV contains too many rows. Please keep uploads below {MAX_ROWS:,} records."
        )

    return normalize_sales_dataframe(raw_df)


def normalize_sales_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a sales dataframe with safety checks and derived metrics."""
    if raw_df is None or raw_df.empty:
        raise ValueError("The provided CSV file is empty.")

    df = raw_df.copy()
    df.columns = [str(column).strip() for column in df.columns]

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Product"] = df["Product"].fillna("Unknown").astype(str).str.strip()
    df["Category"] = df["Category"].fillna("Unknown").astype(str).str.strip()

    numeric_quantity = pd.to_numeric(df["Quantity"], errors="coerce")
    numeric_price = pd.to_numeric(df["Price"], errors="coerce")
    df["Quantity"] = numeric_quantity.fillna(0)
    df["Price"] = numeric_price.fillna(0)

    if df["Product"].eq("").sum() or df["Category"].eq("").sum():
        df["Product"] = df["Product"].replace("", "Unknown")
        df["Category"] = df["Category"].replace("", "Unknown")

    df["Revenue"] = (df["Quantity"] * df["Price"]).fillna(0)
    df = df.dropna(subset=["Date"]).copy()

    if df["Quantity"].lt(0).any() or df["Price"].lt(0).any():
        raise ValueError("Negative Quantity or Price values are not allowed in the sales dataset.")

    if df.empty:
        raise ValueError("The CSV file does not contain any valid dated sales records.")

    df = df.sort_values("Date").reset_index(drop=True)
    return df
