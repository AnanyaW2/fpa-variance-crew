"""
Custom tools for the FP&A Variance Analysis Crew.

Same principle as the AI Job Market Crew: every number that ends up in
the final report is computed here in real pandas code, not guessed by
the LLM. The agent's job is to interpret and communicate, never to do
arithmetic from memory.

FP&A convention used throughout:
  Variance = Actual - Budget
  Negative variance = "favorable" (spent less than planned)
  Positive variance = "unfavorable" (spent more than planned)
This is standard for cost-center/expense budgets, which is what all
departments in this dataset represent.
"""

import pandas as pd
from crewai.tools import tool

DATA_PATH = "data/fpa_variance.csv"


@tool("Dataset Quality Check")
def check_data_quality(note: str = "") -> str:
    """
    Loads the FP&A dataset and returns a data quality report: row/column
    counts, missing values, department list, and date range. Use this
    before any analysis to confirm the dataset is safe to use.
    """
    df = pd.read_csv(DATA_PATH)

    report = []
    report.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    report.append(f"Departments ({df['Department'].nunique()}): {', '.join(sorted(df['Department'].unique()))}")
    report.append(f"Date range: {df['Month'].min()} to {df['Month'].max()}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    report.append("Missing values: none" if missing.empty else f"Missing values: {missing.to_dict()}")

    # Sanity check: does Variance = Actual - Budget?
    check = (df["Actual"] - df["Budget"] - df["Variance"]).abs().sum()
    report.append(
        "Variance column verified as Actual - Budget: consistent"
        if check == 0
        else f"WARNING: Variance column does not match Actual - Budget in all rows (total diff: {check})"
    )

    return "\n".join(report)


@tool("Full-Year Department Variance Summary")
def get_department_summary(note: str = "") -> str:
    """
    Returns full-year budget, actual, and variance totals for each
    department, sorted by the size of the variance (largest overspend
    or underspend first), with a favorable/unfavorable label for each.
    """
    df = pd.read_csv(DATA_PATH)

    summary = (
        df.groupby("Department")
        .agg(total_budget=("Budget", "sum"), total_actual=("Actual", "sum"), total_variance=("Variance", "sum"))
        .reset_index()
    )
    summary["variance_pct"] = (summary["total_variance"] / summary["total_budget"] * 100).round(1)
    summary["label"] = summary["total_variance"].apply(lambda v: "UNFAVORABLE (over budget)" if v > 0 else "FAVORABLE (under budget)")
    summary = summary.reindex(summary["total_variance"].abs().sort_values(ascending=False).index)

    lines = ["FULL-YEAR VARIANCE BY DEPARTMENT (sorted by size of variance):"]
    for _, row in summary.iterrows():
        lines.append(
            f"  {row['Department']}: Budget ${row['total_budget']:,.0f}, Actual ${row['total_actual']:,.0f}, "
            f"Variance ${row['total_variance']:,.0f} ({row['variance_pct']:+.1f}%) — {row['label']}"
        )

    return "\n".join(lines)


@tool("Biggest Monthly Variance Events")
def get_biggest_monthly_variances(note: str = "") -> str:
    """
    Returns the 5 single biggest unfavorable (over-budget) and 5 biggest
    favorable (under-budget) department-month events across the year,
    for spotting one-time outliers rather than year-long trends.
    """
    df = pd.read_csv(DATA_PATH)

    worst = df.sort_values("Variance", ascending=False).head(5)
    best = df.sort_values("Variance", ascending=True).head(5)

    lines = ["TOP 5 SINGLE-MONTH OVERSPENDS (unfavorable):"]
    for _, row in worst.iterrows():
        lines.append(f"  {row['Department']} ({row['Month'][:7]}): ${row['Variance']:,.0f} over budget ({row['Variance_pct']:+.1f}%)")

    lines.append("\nTOP 5 SINGLE-MONTH UNDERSPENDS (favorable):")
    for _, row in best.iterrows():
        lines.append(f"  {row['Department']} ({row['Month'][:7]}): ${row['Variance']:,.0f} under budget ({row['Variance_pct']:+.1f}%)")

    return "\n".join(lines)
