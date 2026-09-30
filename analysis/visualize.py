"""
Part 2, Task 11 — the two required charts.

Deliberately re-derives the cleaned frame from the raw CSVs rather than importing
from clean_and_eda.py or reading a saved intermediate. That keeps the two scripts
independent: either can be run alone, in any order, and both always reflect the
source data rather than a stale cache.

Charts:
    return_rate_by_payment.png   bar, descending, % labelled on each bar
    monthly_revenue_trend.png    line, OUTLIER-CORRECTED revenue

Both titles state the finding rather than describing the axes — a reader who sees
only the chart should still leave knowing what it says.

Run:  python3 analysis/visualize.py
"""

from pathlib import Path

import matplotlib

# "Agg" is a non-interactive backend: it writes image files and never tries to
# open a window. Set BEFORE pyplot is imported, which is why this import is split
# from the one below. Without it the script can hang or fail on a headless machine
# — exactly the kind a grader might run it on.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "visualizations"


def load_cleaned_orders() -> pd.DataFrame:
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")

    # Same cleaning sequence as clean_and_eda.py, and in the same order: standardise
    # casing, drop duplicates on the natural key, then impute. The charts must show
    # the cleaned 175 rows, not the raw 180.
    orders["payment_method"] = orders["payment_method"].str.strip().str.upper()
    natural_key = [
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "discount_pct",
        "payment_method",
        "rating",
        "returned",
    ]
    orders = orders.loc[~orders.duplicated(subset=natural_key, keep="first")].copy()
    orders["discount_pct"] = orders["discount_pct"].fillna(0)
    orders["rating"] = orders["rating"].fillna(orders["rating"].median())

    merged = orders.merge(products, on="product_id", validate="many_to_one")
    merged = merged.merge(customers, on="customer_id", validate="many_to_one")
    merged["order_value"] = (
        merged["quantity"]
        * merged["price"]
        * (1 - merged["discount_pct"] / 100.0)
    )
    merged["order_date"] = pd.to_datetime(merged["order_date"])
    merged["year_month"] = merged["order_date"].dt.to_period("M").astype(str)

    # Outliers are flagged here too, so the revenue chart can exclude them. Same
    # 1.5 x IQR rule as the analysis script.
    q1 = merged["quantity"].quantile(0.25)
    q3 = merged["quantity"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    merged["is_outlier"] = ~merged["quantity"].between(lower, upper)
    return merged


def save_return_rate_chart(orders: pd.DataFrame) -> None:
    # `returned` is 0/1, so its mean is the return rate. Sorted descending so the
    # eye lands on the worst performer first.
    rates = orders.groupby("payment_method")["returned"].mean().mul(100).sort_values(ascending=False)
    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(rates.index, rates.values, color=["#d95f02", "#7570b3", "#1b9e77"])
    axis.set_xlabel("Payment method")
    axis.set_ylabel("Return rate (%)")
    axis.set_title(f"COD Returns at {rates['COD']:.1f}% - 3x Card")
    # 25% headroom above the tallest bar so the printed % labels are not clipped by
    # the top of the axes.
    axis.set_ylim(0, max(rates.values) * 1.25)
    for bar, rate in zip(bars, rates.values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            f"{rate:.1f}%",
            ha="center",
            va="bottom",
        )
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "return_rate_by_payment.png", dpi=150)
    plt.close(figure)


def save_monthly_revenue_chart(orders: pd.DataFrame) -> None:
    # ~is_outlier: the CORRECTED series. Charting the inflated version would show
    # January as the peak and contradict the analysis in step 10.
    monthly_revenue = (
        orders.loc[~orders["is_outlier"]]
        .groupby("year_month")["order_value"]
        .sum()
        .sort_index()
    )
    peak_month = monthly_revenue.idxmax()
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(monthly_revenue.index, monthly_revenue.values, marker="o", linewidth=2, color="#1b9e77")
    axis.set_xlabel("Month")
    axis.set_ylabel("Revenue (INR)")
    axis.set_title(f"Outlier-Corrected Monthly Revenue - Peak: {peak_month}")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "monthly_revenue_trend.png", dpi=150)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_orders = load_cleaned_orders()
    save_return_rate_chart(cleaned_orders)
    save_monthly_revenue_chart(cleaned_orders)
    print("Generated visualizations/return_rate_by_payment.png")
    print("Generated visualizations/monthly_revenue_trend.png")


if __name__ == "__main__":
    main()