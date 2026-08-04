from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.runtime import CLEAN_DATA_DIR, OUTPUTS_DIR, ensure_dir

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

CLEAN_FILE = CLEAN_DATA_DIR / "retail_customer_orders_cleaned.csv"
OUTPUT_DIR = ensure_dir(OUTPUTS_DIR / "task_3_visualization_dashboard")


def save_matplotlib_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()


def main() -> None:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Clean dataset not found: {CLEAN_FILE}. Run task_1_data_cleaning/clean_data.py first.")

    df = pd.read_csv(CLEAN_FILE, parse_dates=["signup_date", "order_date"])
    sns.set_theme(style="whitegrid", palette="deep")

    category_revenue = df.groupby("product_category")["net_amount"].sum().sort_values(ascending=False)
    monthly_revenue = df.groupby("order_month")["net_amount"].sum().sort_index()
    payment_counts = df["payment_method"].value_counts()

    plt.figure(figsize=(9, 5))
    sns.barplot(x=category_revenue.index, y=category_revenue.values, hue=category_revenue.index, legend=False)
    plt.title("Revenue by Product Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    save_matplotlib_figure(OUTPUT_DIR / "revenue_by_category.png")

    plt.figure(figsize=(10, 5))
    sns.lineplot(x=monthly_revenue.index, y=monthly_revenue.values, marker="o", linewidth=2.5)
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    save_matplotlib_figure(OUTPUT_DIR / "monthly_sales_trend.png")

    plt.figure(figsize=(7, 7))
    plt.pie(payment_counts.values, labels=payment_counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Payment Method Share")
    save_matplotlib_figure(OUTPUT_DIR / "payment_method_share.png")

    plt.figure(figsize=(9, 5))
    sns.histplot(df["net_amount"], bins=25, kde=True, color="#2a9d8f")
    plt.title("Order Value Distribution")
    plt.xlabel("Net Order Amount")
    plt.ylabel("Frequency")
    save_matplotlib_figure(OUTPUT_DIR / "order_value_distribution.png")

    plt.figure(figsize=(9, 5))
    sampled = df.sample(n=min(350, len(df)), random_state=42)
    sns.scatterplot(
        data=sampled,
        x="age",
        y="net_amount",
        hue="customer_tier",
        alpha=0.75,
        s=70,
    )
    plt.title("Age vs Order Value by Customer Tier")
    plt.xlabel("Age")
    plt.ylabel("Net Order Amount")
    save_matplotlib_figure(OUTPUT_DIR / "age_vs_order_value.png")

    dashboard = make_subplots(
        rows=3,
        cols=2,
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "domain"}, {"type": "histogram"}],
            [{"type": "scatter", "colspan": 2}, None],
        ],
        subplot_titles=[
            "Revenue by Category",
            "Monthly Sales Trend",
            "Payment Share",
            "Order Value Distribution",
            "Age vs Order Value",
        ],
    )

    dashboard.add_trace(
        go.Bar(x=category_revenue.index, y=category_revenue.values, marker_color="#457b9d"),
        row=1,
        col=1,
    )
    dashboard.add_trace(
        go.Scatter(
            x=monthly_revenue.index,
            y=monthly_revenue.values,
            mode="lines+markers",
            line=dict(color="#e76f51", width=3),
        ),
        row=1,
        col=2,
    )
    dashboard.add_trace(
        go.Pie(labels=payment_counts.index, values=payment_counts.values, hole=0.35),
        row=2,
        col=1,
    )
    dashboard.add_trace(
        go.Histogram(x=df["net_amount"], nbinsx=25, marker_color="#2a9d8f"),
        row=2,
        col=2,
    )
    dashboard.add_trace(
        go.Scatter(
            x=sampled["age"],
            y=sampled["net_amount"],
            mode="markers",
            marker=dict(size=9, opacity=0.75, color=sampled["discount_pct"], colorscale="Viridis", showscale=True),
            text=sampled["customer_tier"],
        ),
        row=3,
        col=1,
    )
    dashboard.update_layout(
        height=1200,
        width=1400,
        title_text="Retail Analytics Dashboard",
        template="plotly_white",
        showlegend=False,
    )
    dashboard.update_xaxes(title_text="Category", row=1, col=1)
    dashboard.update_yaxes(title_text="Revenue", row=1, col=1)
    dashboard.update_xaxes(title_text="Month", row=1, col=2)
    dashboard.update_yaxes(title_text="Revenue", row=1, col=2)
    dashboard.update_xaxes(title_text="Net Order Amount", row=2, col=2)
    dashboard.update_yaxes(title_text="Frequency", row=2, col=2)
    dashboard.update_xaxes(title_text="Age", row=3, col=1)
    dashboard.update_yaxes(title_text="Net Order Amount", row=3, col=1)
    dashboard.write_html(OUTPUT_DIR / "interactive_dashboard.html", include_plotlyjs=True)

    notes = """# Task 3 Visualization Notes

- The bar chart highlights the categories that contribute the most revenue.
- The line chart shows seasonality across months.
- The pie chart captures how customers prefer to pay.
- The histogram explains order value spread and outlier concentration.
- The scatter plot compares age and spend while using discount percentage as a color cue.
"""
    (OUTPUT_DIR / "visualization_notes.md").write_text(notes, encoding="utf-8")
    print(f"Visualization outputs saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

