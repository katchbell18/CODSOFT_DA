from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.runtime import CLEAN_DATA_DIR, OUTPUTS_DIR, ensure_dir

import pandas as pd

CLEAN_FILE = CLEAN_DATA_DIR / "retail_customer_orders_cleaned.csv"
OUTPUT_DIR = ensure_dir(OUTPUTS_DIR / "task_2_eda")


def to_serializable_table(series: pd.Series, top_n: int = 5) -> dict[str, float]:
    return {str(key): round(float(value), 2) for key, value in series.head(top_n).items()}


def main() -> None:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Clean dataset not found: {CLEAN_FILE}. Run task_1_data_cleaning/clean_data.py first.")

    df = pd.read_csv(CLEAN_FILE, parse_dates=["signup_date", "order_date"])

    numeric_columns = [
        "age",
        "quantity",
        "unit_price",
        "discount_pct",
        "rating",
        "gross_amount",
        "discount_amount",
        "net_amount",
    ]

    numeric_summary = df[numeric_columns].describe().round(2)
    numeric_summary.to_csv(OUTPUT_DIR / "numeric_summary.csv")

    correlation_matrix = df[numeric_columns].corr().round(2)
    correlation_matrix.to_csv(OUTPUT_DIR / "correlation_matrix.csv")

    q1 = df["net_amount"].quantile(0.25)
    q3 = df["net_amount"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    outliers = df[df["net_amount"] > upper_bound].sort_values("net_amount", ascending=False)
    outliers.to_csv(OUTPUT_DIR / "order_value_outliers.csv", index=False)

    monthly_revenue = df.groupby("order_month")["net_amount"].sum().sort_index()
    category_revenue = df.groupby("product_category")["net_amount"].sum().sort_values(ascending=False)
    city_revenue = df.groupby("city")["net_amount"].sum().sort_values(ascending=False)
    payment_mix = df["payment_method"].value_counts(normalize=True).mul(100).round(2)
    channel_return_rate = df.groupby("channel")["returned"].mean().mul(100).round(2).sort_values(ascending=False)
    tier_aov = df.groupby("customer_tier")["net_amount"].mean().round(2).sort_values(ascending=False)
    category_rating = df.groupby("product_category")["rating"].mean().round(2).sort_values(ascending=False)

    monthly_revenue.round(2).to_csv(OUTPUT_DIR / "monthly_revenue.csv")
    category_revenue.round(2).to_csv(OUTPUT_DIR / "category_revenue.csv")
    city_revenue.round(2).to_csv(OUTPUT_DIR / "city_revenue.csv")
    payment_mix.to_csv(OUTPUT_DIR / "payment_mix.csv")

    top_category = category_revenue.idxmax()
    top_city = city_revenue.idxmax()
    favorite_payment = payment_mix.idxmax()
    best_month = monthly_revenue.idxmax()
    highest_aov_tier = tier_aov.idxmax()
    highest_rating_category = category_rating.idxmax()
    riskiest_channel = channel_return_rate.idxmax()
    discount_revenue_corr = round(float(df["discount_pct"].corr(df["net_amount"])), 2)

    summary_payload = {
        "row_count": int(len(df)),
        "customer_count": int(df["customer_id"].nunique()),
        "total_revenue": round(float(df["net_amount"].sum()), 2),
        "average_order_value": round(float(df["net_amount"].mean()), 2),
        "median_order_value": round(float(df["net_amount"].median()), 2),
        "top_category_by_revenue": top_category,
        "top_city_by_revenue": top_city,
        "most_used_payment_method": favorite_payment,
        "best_sales_month": best_month,
        "highest_average_order_value_tier": highest_aov_tier,
        "highest_rated_category": highest_rating_category,
        "highest_return_rate_channel": riskiest_channel,
        "discount_to_revenue_correlation": discount_revenue_corr,
        "outlier_orders": int(len(outliers)),
        "top_categories": to_serializable_table(category_revenue),
        "top_cities": to_serializable_table(city_revenue),
    }

    with (OUTPUT_DIR / "eda_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary_payload, file, indent=2)

    report = f"""# Task 2 EDA Report

## Executive Summary

- Total analyzed orders: {len(df)}
- Unique customers: {df["customer_id"].nunique()}
- Total revenue: {df["net_amount"].sum():,.2f}
- Average order value: {df["net_amount"].mean():,.2f}
- Median order value: {df["net_amount"].median():,.2f}

## Key Business Findings

- The highest revenue product category is **{top_category}**.
- The strongest city by revenue is **{top_city}**.
- The most used payment method is **{favorite_payment}**.
- **{highest_aov_tier}** customers generate the highest average order value.
- **{riskiest_channel}** has the highest return rate, which deserves operational review.
- The highest rated category is **{highest_rating_category}**.
- The strongest month for sales was **{best_month}**.
- The correlation between discount percentage and net order value is **{discount_revenue_corr}**, which suggests only a mild linear relationship.

## Outlier Review

- Orders above the IQR upper bound: {len(outliers)}
- Share of outlier orders: {(len(outliers) / len(df)) * 100:.2f}%
- The outlier file can be used to review premium or bulk purchases separately.
"""
    (OUTPUT_DIR / "eda_report.md").write_text(report, encoding="utf-8")
    print(f"EDA outputs saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

