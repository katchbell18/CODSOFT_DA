from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.runtime import CLEAN_DATA_DIR, OUTPUTS_DIR, RAW_DATA_DIR, ensure_dir

import numpy as np
import pandas as pd

RAW_FILE = RAW_DATA_DIR / "retail_customer_orders_raw.csv"
CLEAN_FILE = CLEAN_DATA_DIR / "retail_customer_orders_cleaned.csv"
OUTPUT_DIR = ensure_dir(OUTPUTS_DIR / "task_1_data_cleaning")

CITY_FIXES = {
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "mumbai": "Mumbai",
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "jaipur": "Jaipur",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "chennai": "Chennai",
    "lucknow": "Lucknow",
    "ahmedabad": "Ahmedabad",
}

STATE_BY_CITY = {
    "Delhi": "Delhi",
    "Mumbai": "Maharashtra",
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Pune": "Maharashtra",
    "Jaipur": "Rajasthan",
    "Kolkata": "West Bengal",
    "Chennai": "Tamil Nadu",
    "Lucknow": "Uttar Pradesh",
    "Ahmedabad": "Gujarat",
}

STATE_FIXES = {
    "delhi": "Delhi",
    "maharashtra": "Maharashtra",
    "maharastra": "Maharashtra",
    "karnataka": "Karnataka",
    "telangana": "Telangana",
    "rajasthan": "Rajasthan",
    "west bengal": "West Bengal",
    "tamil nadu": "Tamil Nadu",
    "uttar pradesh": "Uttar Pradesh",
    "gujarat": "Gujarat",
}

CATEGORY_FIXES = {
    "electronics": "Electronics",
    "fashion": "Fashion",
    "home & kitchen": "Home & Kitchen",
    "beauty": "Beauty",
    "grocery": "Grocery",
}

PAYMENT_FIXES = {
    "upi": "UPI",
    "credit card": "Credit Card",
    "debit card": "Debit Card",
    "wallet": "Wallet",
    "cash on delivery": "Cash on Delivery",
    "cod": "Cash on Delivery",
}

CHANNEL_FIXES = {"app": "App", "website": "Website", "store": "Store"}
TIER_FIXES = {"silver": "Silver", "gold": "Gold", "platinum": "Platinum"}
GENDER_FIXES = {"m": "Male", "male": "Male", "f": "Female", "female": "Female"}
RETURN_FIXES = {
    "yes": 1,
    "y": 1,
    "returned": 1,
    "1": 1,
    "true": 1,
    "no": 0,
    "n": 0,
    "kept": 0,
    "0": 0,
    "false": 0,
}


def normalize_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    return " ".join(str(value).strip().split())


def normalize_key(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    return " ".join(str(value).strip().split()).lower()


def extract_number(value: object) -> float:
    if pd.isna(value):
        return np.nan
    cleaned = str(value).replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else np.nan


def mode_or_na(series: pd.Series) -> object:
    non_null = series.dropna()
    if non_null.empty:
        return pd.NA
    mode = non_null.mode()
    return mode.iat[0] if not mode.empty else non_null.iloc[0]


def fill_group_mode(frame: pd.DataFrame, group_col: str, target_col: str) -> pd.Series:
    group_modes = frame.groupby(group_col)[target_col].transform(mode_or_na)
    return frame[target_col].fillna(group_modes)


def fill_group_median(frame: pd.DataFrame, group_col: str, target_col: str) -> pd.Series:
    group_medians = frame.groupby(group_col)[target_col].transform("median")
    return frame[target_col].fillna(group_medians)


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_FILE}. Run scripts/generate_raw_dataset.py first.")

    ensure_dir(CLEAN_DATA_DIR)
    df = pd.read_csv(RAW_FILE)
    rows_before = len(df)
    missing_before = df.isna().sum()

    full_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    duplicate_order_ids = int(df.duplicated(subset=["order_id"]).sum())
    df = df.drop_duplicates(subset=["order_id"]).copy()

    df["customer_name"] = df["customer_name"].map(normalize_text)
    df["product_name"] = df["product_name"].map(normalize_text)

    df["gender"] = df["gender"].map(normalize_key).map(GENDER_FIXES)
    df["city"] = df["city"].map(normalize_key).map(CITY_FIXES)
    df["state"] = df["state"].map(normalize_key).map(STATE_FIXES)
    df["product_category"] = df["product_category"].map(normalize_key).map(CATEGORY_FIXES)
    df["payment_method"] = df["payment_method"].map(normalize_key).map(PAYMENT_FIXES)
    df["channel"] = df["channel"].map(normalize_key).map(CHANNEL_FIXES)
    df["customer_tier"] = df["customer_tier"].map(normalize_key).map(TIER_FIXES)
    df["returned"] = df["returned"].map(normalize_key).map(RETURN_FIXES)

    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce", dayfirst=True, format="mixed")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=True, format="mixed")

    numeric_columns = ["age", "quantity", "unit_price", "discount_pct", "rating"]
    for column in numeric_columns:
        df[column] = df[column].map(extract_number)

    df["returned"] = pd.to_numeric(df["returned"], errors="coerce")

    df.loc[~df["age"].between(18, 70), "age"] = np.nan
    df.loc[~df["quantity"].between(1, 10), "quantity"] = np.nan
    df.loc[~df["unit_price"].between(100, 15000), "unit_price"] = np.nan
    df.loc[~df["discount_pct"].between(0, 40), "discount_pct"] = np.nan
    df.loc[~df["rating"].between(1, 5), "rating"] = np.nan

    df["state"] = df["state"].fillna(df["city"].map(STATE_BY_CITY))

    for column in ["customer_name", "gender", "city", "state", "customer_tier"]:
        df[column] = fill_group_mode(df, "customer_id", column)

    df["state"] = df["state"].fillna(df["city"].map(STATE_BY_CITY))
    df["city"] = fill_group_mode(df, "state", "city")

    df["payment_method"] = fill_group_mode(df, "customer_id", "payment_method")
    df["channel"] = fill_group_mode(df, "customer_id", "channel")
    df["product_category"] = fill_group_mode(df, "product_name", "product_category")
    df["returned"] = fill_group_mode(df, "customer_id", "returned")

    df["age"] = fill_group_median(df, "customer_id", "age")
    df["quantity"] = fill_group_median(df, "product_category", "quantity")
    df["unit_price"] = fill_group_median(df, "product_name", "unit_price")
    df["discount_pct"] = fill_group_median(df, "channel", "discount_pct")
    df["rating"] = fill_group_median(df, "product_category", "rating")

    df["city"] = df["city"].fillna(mode_or_na(df["city"]))
    df["state"] = df["state"].fillna(df["city"].map(STATE_BY_CITY))
    df["payment_method"] = df["payment_method"].fillna(mode_or_na(df["payment_method"]))
    df["channel"] = df["channel"].fillna(mode_or_na(df["channel"]))
    df["customer_tier"] = df["customer_tier"].fillna(mode_or_na(df["customer_tier"]))
    df["gender"] = df["gender"].fillna(mode_or_na(df["gender"]))
    df["age"] = df["age"].fillna(df["age"].median())
    df["quantity"] = df["quantity"].fillna(df["quantity"].median())
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median())
    df["discount_pct"] = df["discount_pct"].fillna(df["discount_pct"].median())
    df["rating"] = df["rating"].fillna(df["rating"].median())
    df["returned"] = df["returned"].fillna(0)

    df = df.dropna(subset=["order_id", "customer_id", "order_date", "signup_date"]).copy()

    df["age"] = df["age"].round().astype(int)
    df["quantity"] = df["quantity"].round().astype(int)
    df["unit_price"] = df["unit_price"].round(2)
    df["discount_pct"] = df["discount_pct"].round(2)
    df["rating"] = df["rating"].round(1)
    df["returned"] = df["returned"].astype(int)

    df["gross_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df["discount_amount"] = (df["gross_amount"] * df["discount_pct"] / 100).round(2)
    df["net_amount"] = (df["gross_amount"] - df["discount_amount"]).round(2)
    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 25, 35, 45, 55, 71],
        labels=["18-24", "25-34", "35-44", "45-54", "55-70"],
        right=False,
    )
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

    df = df.sort_values(["order_date", "order_id"]).reset_index(drop=True)
    df.to_csv(CLEAN_FILE, index=False)

    missing_after = df.isna().sum()
    quality_summary = pd.DataFrame({"missing_before": missing_before, "missing_after": missing_after})
    quality_summary.to_csv(OUTPUT_DIR / "data_quality_summary.csv")

    report = f"""# Task 1 Cleaning Report

## Dataset Summary

- Raw rows: {rows_before}
- Clean rows: {len(df)}
- Full duplicate rows removed: {full_duplicates}
- Duplicate order IDs removed: {duplicate_order_ids}
- Remaining missing values: {int(missing_after.sum())}

## Cleaning Steps

- Standardized inconsistent city, state, category, gender, payment, channel, and tier values.
- Parsed mixed date formats for `signup_date` and `order_date`.
- Converted messy numeric fields like `quantity`, `unit_price`, `discount_pct`, and `rating`.
- Imputed missing values using customer-level modes and category-level medians.
- Created analysis-ready columns: `gross_amount`, `discount_amount`, `net_amount`, `age_group`, and `order_month`.

## Final Dataset Snapshot

- Unique customers: {df["customer_id"].nunique()}
- Date range: {df["order_date"].min().date()} to {df["order_date"].max().date()}
- Total revenue-ready rows: {len(df)}
"""
    (OUTPUT_DIR / "cleaning_report.md").write_text(report, encoding="utf-8")
    print(f"Cleaned dataset saved to {CLEAN_FILE}")


if __name__ == "__main__":
    main()

