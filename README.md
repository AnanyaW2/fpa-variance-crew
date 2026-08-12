# FP&A Variance Analysis Crew

A 3-agent system (built with [CrewAI](https://www.crewai.com/)) that automates the first pass of a monthly budget-vs-actual variance review — the kind of recurring FP&A task that's mechanical but time-consuming.

**Part of a small suite of business-function agent crews** — see also: [AI Job Market Analysis Crew](../ai-job-market-crew).

---

## What it does

Given a year of budget-vs-actual data across 8 departments, the crew:
1. Validates the data is clean and the variance math is correct
2. Identifies which departments are most over/under budget for the year, and the single biggest one-time overspend/underspend events
3. Writes a short, direct variance commentary — the kind that goes into a monthly finance review deck

## Architecture

```
Data Validator  →  Variance Analyst  →  Report Writer
```

Same pattern as the AI Job Market Crew: each agent has one job, and every number comes from a real pandas tool call, not the LLM's own reasoning. See that project's README for the full rationale on why grounded tools matter.

## FP&A convention used

`Variance = Actual - Budget`
- **Negative variance = "favorable"** (spent less than planned)
- **Positive variance = "unfavorable"** (spent more than planned)

This is standard cost-center convention. All departments in this dataset are treated as expense budgets.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# add your free Groq API key (console.groq.com -> API Keys)
```

Place the dataset at `data/fpa_variance.csv` — [source on Kaggle](https://www.kaggle.com/datasets/ameernassar/fp-and-a-variance-analysis).

Run:
```bash
python3 main.py
```

Report saved to `output/report.md`.

## Tools

Python · CrewAI · pandas · Groq (Llama 3.3 70B)
