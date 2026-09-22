"""
Exploratory Data Analysis Module
----------------------------------
Generates comprehensive EDA visualizations and prints analytical
summaries. All figures are saved to outputs/figures/.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import FIGURES_DIR, TARGET_COL
from src.data_preprocessing import get_preprocessed_data


def section_header(title):
    print(f"\n{'-'*70}")
    print(f"  {title}")
    print(f"{'-'*70}")


def run_eda():
    """Run the complete EDA pipeline."""
    print("=" * 70)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 70)

    # Load preprocessed data
    train, _ = get_preprocessed_data()

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams.update({"font.size": 11, "figure.dpi": 120})

    # ----------------------------------------------------------------------
    # Section 1: Dataset Overview
    # ----------------------------------------------------------------------
    section_header("1. DATASET OVERVIEW")
    print(f"  Total records: {len(train):,}")
    print(f"  Columns: {list(train.columns)}")
    print(f"  Date range: {train['Date'].min().date()} to {train['Date'].max().date()}")
    print(f"  Unique Stores: {train['Store'].nunique()}")
    print(f"  Unique Departments: {train['Dept'].nunique()}")
    print(f"  Memory usage: {train.memory_usage(deep=True).sum() / 1e6:.1f} MB")

    # ----------------------------------------------------------------------
    # Section 2: Data Quality
    # ----------------------------------------------------------------------
    section_header("2. DATA QUALITY")
    print(f"  Missing values per column:")
    missing = train.isnull().sum()
    for col in missing[missing > 0].index:
        print(f"    {col}: {missing[col]:,} ({missing[col]/len(train)*100:.2f}%)")
    if missing.sum() == 0:
        print(f"    None — all values present.")
    print(f"  Duplicate rows: {train.duplicated().sum()}")
    print(f"  Negative Weekly_Sales: {(train[TARGET_COL] < 0).sum():,}")
    print(f"  Zero Weekly_Sales: {(train[TARGET_COL] == 0).sum():,}")

    # ----------------------------------------------------------------------
    # Section 3: Sales Distribution
    # ----------------------------------------------------------------------
    section_header("3. SALES DISTRIBUTION")
    sales = train[TARGET_COL]
    print(f"  Total Sales:   ${sales.sum():,.2f}")
    print(f"  Average Sales: ${sales.mean():,.2f}")
    print(f"  Median Sales:  ${sales.median():,.2f}")
    print(f"  Std Dev:       ${sales.std():,.2f}")
    print(f"  Min Sales:     ${sales.min():,.2f}")
    print(f"  Max Sales:     ${sales.max():,.2f}")
    print(f"  Skewness:      {sales.skew():.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram (cap at 99th percentile for readability)
    cap = sales.quantile(0.99)
    axes[0].hist(sales[sales <= cap], bins=60, color="#2196F3",
                 edgecolor="white", alpha=0.85)
    axes[0].set_xlabel("Weekly Sales ($)")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("Distribution of Weekly Sales (capped at 99th percentile)")
    axes[0].axvline(sales.mean(), color="red", linestyle="--", label=f"Mean: ${sales.mean():,.0f}")
    axes[0].axvline(sales.median(), color="green", linestyle="--", label=f"Median: ${sales.median():,.0f}")
    axes[0].legend()

    # Box plot
    axes[1].boxplot(sales, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#4CAF50", alpha=0.7))
    axes[1].set_ylabel("Weekly Sales ($)")
    axes[1].set_title("Box Plot of Weekly Sales")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "sales_distribution.png"), bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------------------
    # Section 4: Time-Series Analysis
    # ----------------------------------------------------------------------
    section_header("4. TIME-SERIES ANALYSIS")

    weekly_sales = train.groupby("Date")[TARGET_COL].sum().sort_index()
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(weekly_sales.index, weekly_sales.values, color="#1565C0", linewidth=1.2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Weekly Sales ($)")
    ax.set_title("Total Weekly Sales Over Time")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "weekly_sales_trend.png"), bbox_inches="tight")
    plt.close()

    # Monthly sales
    train_copy = train.copy()
    train_copy["YearMonth"] = train_copy["Date"].dt.to_period("M")
    monthly = train_copy.groupby("YearMonth")[TARGET_COL].sum()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(len(monthly)), monthly.values, color="#FF9800", edgecolor="white")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales ($)")
    ax.set_title("Monthly Total Sales")
    # Show every 3rd label for readability
    tick_positions = range(0, len(monthly), 3)
    ax.set_xticks(list(tick_positions))
    ax.set_xticklabels([str(monthly.index[i]) for i in tick_positions], rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "monthly_sales.png"), bbox_inches="tight")
    plt.close()

    # Week-of-year pattern
    woy_sales = train.groupby("WeekOfYear" if "WeekOfYear" in train.columns
                              else train["Date"].dt.isocalendar().week)[TARGET_COL].mean()
    if "WeekOfYear" not in train.columns:
        train_copy["WeekOfYear"] = train_copy["Date"].dt.isocalendar().week.astype(int)
        woy_sales = train_copy.groupby("WeekOfYear")[TARGET_COL].mean().sort_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(woy_sales.index, woy_sales.values, color="#9C27B0", linewidth=1.5, marker="o", markersize=3)
    ax.set_xlabel("Week of Year")
    ax.set_ylabel("Average Weekly Sales ($)")
    ax.set_title("Average Sales by Week of Year (Seasonal Pattern)")
    ax.set_xticks(range(1, 53, 4))
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "seasonal_pattern.png"), bbox_inches="tight")
    plt.close()

    print("  Time-series charts saved.")

    # ----------------------------------------------------------------------
    # Section 5: Store Analysis
    # ----------------------------------------------------------------------
    section_header("5. STORE ANALYSIS")

    store_sales = train.groupby("Store")[TARGET_COL].agg(["sum", "mean"]).sort_values("sum", ascending=False)
    print(f"  Top 5 stores by total sales:")
    for i, (store, row) in enumerate(store_sales.head().iterrows()):
        print(f"    {i+1}. Store {store}: ${row['sum']:,.0f} (avg ${row['mean']:,.0f})")
    print(f"  Bottom 5 stores by total sales:")
    for i, (store, row) in enumerate(store_sales.tail().iterrows()):
        print(f"    {i+1}. Store {store}: ${row['sum']:,.0f} (avg ${row['mean']:,.0f})")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Top 10 stores
    top10 = store_sales.head(10)
    axes[0].barh(range(10), top10["sum"].values, color="#4CAF50")
    axes[0].set_yticks(range(10))
    axes[0].set_yticklabels([f"Store {s}" for s in top10.index])
    axes[0].set_xlabel("Total Sales ($)")
    axes[0].set_title("Top 10 Stores by Total Sales")
    axes[0].invert_yaxis()

    # Sales by store type
    if "Type_encoded" in train.columns:
        type_map = {2: "A", 1: "B", 0: "C"}
        type_sales = train.copy()
        type_sales["StoreType"] = type_sales["Type_encoded"].map(type_map)
        type_avg = type_sales.groupby("StoreType")[TARGET_COL].mean().sort_values(ascending=False)

        axes[1].bar(type_avg.index, type_avg.values,
                    color=["#2196F3", "#FF9800", "#F44336"])
        axes[1].set_xlabel("Store Type")
        axes[1].set_ylabel("Average Weekly Sales ($)")
        axes[1].set_title("Average Sales by Store Type")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "store_analysis.png"), bbox_inches="tight")
    plt.close()

    # Store size vs sales
    if "Size" in train.columns:
        store_info = train.groupby("Store").agg({
            TARGET_COL: "mean", "Size": "first"
        }).reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(store_info["Size"], store_info[TARGET_COL],
                   c="#1565C0", s=60, alpha=0.7, edgecolors="white")
        ax.set_xlabel("Store Size (sq ft)")
        ax.set_ylabel("Average Weekly Sales ($)")
        ax.set_title("Store Size vs Average Weekly Sales")
        # Add trend line
        z = np.polyfit(store_info["Size"], store_info[TARGET_COL], 1)
        p = np.poly1d(z)
        x_line = np.linspace(store_info["Size"].min(), store_info["Size"].max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.7, label="Trend line")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "store_size_vs_sales.png"), bbox_inches="tight")
        plt.close()

    print("  Store analysis charts saved.")

    # ----------------------------------------------------------------------
    # Section 6: Department Analysis
    # ----------------------------------------------------------------------
    section_header("6. DEPARTMENT ANALYSIS")

    dept_sales = train.groupby("Dept")[TARGET_COL].agg(["sum", "mean"]).sort_values("sum", ascending=False)
    print(f"  Top 5 departments by total sales:")
    for i, (dept, row) in enumerate(dept_sales.head().iterrows()):
        print(f"    {i+1}. Dept {dept}: ${row['sum']:,.0f} (avg ${row['mean']:,.0f})")

    fig, ax = plt.subplots(figsize=(12, 6))
    top15_dept = dept_sales.head(15)
    ax.bar(range(15), top15_dept["sum"].values,
           color=plt.cm.viridis(np.linspace(0.2, 0.9, 15)))
    ax.set_xticks(range(15))
    ax.set_xticklabels([f"Dept {d}" for d in top15_dept.index], rotation=45, ha="right")
    ax.set_xlabel("Department")
    ax.set_ylabel("Total Sales ($)")
    ax.set_title("Top 15 Departments by Total Sales")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "department_analysis.png"), bbox_inches="tight")
    plt.close()
    print("  Department analysis chart saved.")

    # ----------------------------------------------------------------------
    # Section 7: Holiday Analysis
    # ----------------------------------------------------------------------
    section_header("7. HOLIDAY ANALYSIS")

    holiday_avg = train.groupby("IsHoliday")[TARGET_COL].mean()
    non_hol = holiday_avg.get(0, holiday_avg.get(False, 0))
    hol = holiday_avg.get(1, holiday_avg.get(True, 0))
    pct_diff = ((hol - non_hol) / non_hol) * 100

    print(f"  Average sales — Holiday:     ${hol:,.2f}")
    print(f"  Average sales — Non-holiday: ${non_hol:,.2f}")
    print(f"  Holiday premium: {pct_diff:+.1f}%")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(["Non-Holiday", "Holiday"], [non_hol, hol],
                color=["#2196F3", "#F44336"])
    axes[0].set_ylabel("Average Weekly Sales ($)")
    axes[0].set_title("Holiday vs Non-Holiday Average Sales")

    # Sales distribution comparison
    holiday_sales = train[train["IsHoliday"] == 1][TARGET_COL]
    non_holiday_sales = train[train["IsHoliday"] == 0][TARGET_COL]
    cap_val = train[TARGET_COL].quantile(0.95)

    axes[1].hist(non_holiday_sales[non_holiday_sales <= cap_val], bins=50,
                 alpha=0.6, label="Non-Holiday", color="#2196F3")
    axes[1].hist(holiday_sales[holiday_sales <= cap_val], bins=50,
                 alpha=0.6, label="Holiday", color="#F44336")
    axes[1].set_xlabel("Weekly Sales ($)")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title("Sales Distribution: Holiday vs Non-Holiday")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "holiday_analysis.png"), bbox_inches="tight")
    plt.close()
    print("  Holiday analysis charts saved.")

    # ----------------------------------------------------------------------
    # Section 8: External Factors
    # ----------------------------------------------------------------------
    section_header("8. EXTERNAL FACTORS ANALYSIS")

    ext_cols = ["Temperature", "Fuel_Price", "CPI", "Unemployment"]
    available_ext = [c for c in ext_cols if c in train.columns]

    if available_ext:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.ravel()

        for i, col in enumerate(available_ext):
            # Use store-level weekly averages for clearer patterns
            agg = train.groupby("Date").agg({
                TARGET_COL: "mean", col: "first"
            }).reset_index()

            axes[i].scatter(agg[col], agg[TARGET_COL], alpha=0.4, s=15, color="#1565C0")
            axes[i].set_xlabel(col)
            axes[i].set_ylabel("Avg Weekly Sales ($)")
            corr = agg[col].corr(agg[TARGET_COL])
            axes[i].set_title(f"{col} vs Sales (corr: {corr:.3f})")

        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "external_factors.png"), bbox_inches="tight")
        plt.close()

        for col in available_ext:
            corr = train[col].corr(train[TARGET_COL])
            print(f"  {col} correlation with Sales: {corr:.4f}")

    print("  External factors chart saved.")

    # ----------------------------------------------------------------------
    # Section 9: Correlation Heatmap
    # ----------------------------------------------------------------------
    section_header("9. CORRELATION ANALYSIS")

    numeric_cols = train.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude Store and Dept IDs from correlation (they're identifiers)
    corr_cols = [c for c in numeric_cols if c not in ["Store", "Dept"]]
    corr_matrix = train[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(12, 9))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0, square=True,
                linewidths=0.5, ax=ax, vmin=-1, vmax=1)
    ax.set_title("Correlation Heatmap (Numerical Features)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_heatmap.png"), bbox_inches="tight")
    plt.close()

    # Print top correlations with target
    target_corr = corr_matrix[TARGET_COL].drop(TARGET_COL).abs().sort_values(ascending=False)
    print(f"  Top correlations with {TARGET_COL}:")
    for feat, corr_val in target_corr.head(10).items():
        sign = "+" if corr_matrix.loc[feat, TARGET_COL] > 0 else "-"
        print(f"    {feat}: {sign}{corr_val:.4f}")

    print("  Correlation heatmap saved.")

    # ----------------------------------------------------------------------
    # Section 10: Markdown Analysis
    # ----------------------------------------------------------------------
    section_header("10. MARKDOWN ANALYSIS")

    md_cols = [c for c in ["MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5"]
               if c in train.columns]
    if md_cols:
        has_md = train[md_cols].sum(axis=1) > 0
        md_sales = train[has_md][TARGET_COL].mean()
        no_md_sales = train[~has_md][TARGET_COL].mean()
        print(f"  With markdowns: ${md_sales:,.2f} avg (n={has_md.sum():,})")
        n_no_md = (~has_md).sum()
        print(f"  Without markdowns: ${no_md_sales:,.2f} avg (n={n_no_md:,})")
        print(f"  Markdown effect: {((md_sales - no_md_sales)/no_md_sales)*100:+.1f}%")

    # ----------------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------------
    section_header("EDA COMPLETE")
    print(f"  All visualizations saved to: {FIGURES_DIR}")
    print(f"  Figures generated:")
    for f in sorted(os.listdir(FIGURES_DIR)):
        if f.endswith(".png"):
            print(f"    - {f}")


if __name__ == "__main__":
    run_eda()
