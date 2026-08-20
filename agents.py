"""
Agent definitions for the FP&A Variance Analysis Crew.

Same 3-agent pattern as the AI Job Market Crew: Validator -> Analyst ->
Report Writer. Uses Groq (free tier) by default via CrewAI's native LLM
class.
"""

import os
from crewai import Agent, LLM
from tools.data_tools import (
    check_data_quality,
    get_department_summary,
    get_biggest_monthly_variances,
)

llm = LLM(
    model="groq/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    parallel_tool_calls=False,
)

data_validator = Agent(
    role="Data Quality Validator",
    goal=(
        "Confirm the FP&A budget-vs-actual dataset is clean and safe to "
        "analyze, and verify the Variance column is calculated correctly "
        "before analysis begins."
    ),
    backstory=(
        "You are a meticulous financial data controller. You never let "
        "a variance report go out the door until you've personally "
        "verified the underlying numbers add up."
    ),
    tools=[check_data_quality],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

variance_analyst = Agent(
    role="FP&A Variance Analyst",
    goal=(
        "Identify which departments are most over or under budget for "
        "the full year, and flag the single biggest one-time overspend "
        "and underspend events — using only real computed figures from "
        "your tools, never estimates."
    ),
    backstory=(
        "You are an FP&A analyst who has sat through enough budget "
        "review meetings to know that leadership wants two things: "
        "which departments need a conversation, and whether a bad month "
        "was a trend or a one-off. You always state whether a variance "
        "is favorable or unfavorable, using standard cost-center "
        "convention (overspend = unfavorable)."
    ),
    tools=[get_department_summary, get_biggest_monthly_variances],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

report_writer = Agent(
    role="Finance Report Writer",
    goal=(
        "Turn the analyst's findings into a short, CFO-ready variance "
        "commentary — the kind of write-up that goes directly into a "
        "monthly finance review deck."
    ),
    backstory=(
        "You write the way finance leaders actually want to read: "
        "direct, numbers-first, no padding. You flag what needs "
        "attention and don't bury it in caveats."
    ),
    tools=[],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)
