"""
Task definitions for the FP&A Variance Analysis Crew.

Sequential: validate -> analyze -> write, each stage's output passed
as context into the next.
"""

from crewai import Task
from agents import data_validator, variance_analyst, report_writer

validate_task = Task(
    description=(
        "Run a full data quality check on the FP&A budget-vs-actual "
        "dataset. Confirm the row/column counts, department list, date "
        "range, and that the Variance column is calculated correctly. "
        "State clearly whether the dataset is safe to proceed with "
        "analysis."
    ),
    expected_output=(
        "A short data quality report (4-6 lines) covering row/column "
        "counts, departments, date range, and a clear go/no-go "
        "statement."
    ),
    agent=data_validator,
)

analyze_task = Task(
    description=(
        "Using the validated dataset, identify: (1) the 3 departments "
        "with the largest full-year unfavorable (over-budget) variance, "
        "(2) the 3 departments with the largest full-year favorable "
        "(under-budget) variance, and (3) the single biggest one-time "
        "overspend and underspend events during the year. For each, "
        "state the dollar amount and percentage. Use your tools for "
        "every figure — do not estimate."
    ),
    expected_output=(
        "A structured summary covering the 3 most unfavorable "
        "departments, 3 most favorable departments, and the biggest "
        "single-month outlier events, each with specific dollar and "
        "percentage figures."
    ),
    agent=variance_analyst,
    context=[validate_task],
)

report_task = Task(
    description=(
        "Write a short FP&A variance commentary based on the analyst's "
        "findings — the kind that would go into a monthly finance "
        "review deck. Structure it with a one-paragraph headline "
        "summary, a section on departments needing attention (largest "
        "unfavorable variances), a section on departments performing "
        "well (largest favorable variances), and a short note on any "
        "one-time outlier events worth flagging separately from the "
        "full-year trend. Keep it direct and numbers-first. Format in "
        "clean markdown."
    ),
    expected_output=(
        "A complete markdown report, 350-500 words, with a headline "
        "summary and clearly headed sections, written in direct "
        "finance-review style."
    ),
    agent=report_writer,
    context=[analyze_task],
    output_file="output/report.md",
)
