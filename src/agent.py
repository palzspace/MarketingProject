"""LangChain agent wiring — Claude + SQL tool + chart tool."""

import logging

import pandas as pd
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config import ANTHROPIC_MODEL, SCHEMA_DESCRIPTION
from src.database import execute_query
from src.guardrails import GuardrailError, validate_query
from src.visualization import create_chart

logger = logging.getLogger(__name__)

# Module-level store for the most recent query results.
# Fine for a single-session Streamlit POC; not for production.
_last_results: dict = {"df": None, "sql": None, "chart": None}


# ── Tools ────────────────────────────────────────────────────────────────

@tool
def run_sql_query(sql: str) -> str:
    """Execute a SQL SELECT query on the marketing database.

    Only SELECT statements are allowed. The single available table
    is **campaigns** with columns: campaign_id, campaign_name,
    channel, impressions, clicks, conversions, spend, revenue, date.
    """
    try:
        validated = validate_query(sql)
        df = execute_query(validated)
        _last_results["df"] = df
        _last_results["sql"] = validated
        _last_results["chart"] = None  # reset previous chart

        if df.empty:
            return "Query executed successfully but returned no rows."
        return f"Results ({len(df)} rows):\n{df.to_string(index=False)}"

    except GuardrailError as exc:
        return str(exc)
    except Exception as exc:
        logger.exception("Query execution failed")
        return f"❌ Query failed: {exc}"


@tool
def generate_chart(chart_type: str, title: str, x_column: str, y_column: str) -> str:
    """Generate a chart from the last SQL query results.

    Args:
        chart_type: bar | line | histogram | pie
        title: A descriptive chart title.
        x_column: Column for the x-axis / labels.
        y_column: Column for the y-axis / values.
    """
    df = _last_results.get("df")
    if df is None or df.empty:
        return "No data available — please run a SQL query first."

    try:
        buf = create_chart(df, chart_type, title, x_column, y_column)
        _last_results["chart"] = buf
        return f"✅ {chart_type.capitalize()} chart created: '{title}'"
    except Exception as exc:
        logger.exception("Chart generation failed")
        return f"❌ Chart generation failed: {exc}"


# ── System prompt ────────────────────────────────────────────────────────

_SYSTEM_PROMPT = f"""\
You are a marketing analytics assistant. You help users explore campaign
performance data by converting natural-language questions into SQL,
executing them, explaining the results, and optionally visualising them.

DATABASE SCHEMA
───────────────
{SCHEMA_DESCRIPTION}

RULES
─────
1. Convert the user's question into a valid **SQLite SELECT** query.
2. NEVER generate INSERT, UPDATE, DELETE, CREATE, DROP, or ALTER.
3. Only reference the **campaigns** table and its columns listed above.
4. Call `run_sql_query` to execute the SQL.
5. After receiving results, provide a concise natural-language explanation.
6. When a visualisation would add clarity, call `generate_chart`:
   • Trends over time → line
   • Comparisons across categories → bar
   • Distributions of a metric → histogram
   • Proportional breakdowns → pie
7. If the question is unrelated to marketing campaign data, politely decline.
8. Always show the SQL you generated so the user can learn from it.
"""

# ── Agent factory ────────────────────────────────────────────────────────

def create_agent() -> AgentExecutor:
    """Build and return a ready-to-invoke LangChain agent."""
    llm = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)
    tools = [run_sql_query, generate_chart]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=6,
        handle_parsing_errors=True,
    )


def get_last_results() -> dict:
    """Return the latest query DataFrame and chart buffer (if any)."""
    return _last_results
