"""LangGraph ReAct agent — RBAC-aware tools and dynamic system prompt.

NOTE: ``_current_role`` and ``_last_results`` are module-level globals.
This is intentional for a single-user Streamlit POC.  A production app
would use request-scoped context or dependency injection instead.
"""

import logging

from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from config.roles import ROLE_PERMISSIONS
from config.schema import ANTHROPIC_MODEL, SCHEMA_DESCRIPTION, TABLE_NAME
from agent.executor import execute_query
from agent.rbac import RBACError
from agent.validator import GuardrailError, validate_query
from visualization import create_chart

logger = logging.getLogger(__name__)

# ── Module-level state (single-user POC only) ───────────────────────────
_last_results: dict = {"df": None, "sql": None, "chart": None}
_current_role: str = "Marketing Analyst"


def set_current_role(role: str) -> None:
    global _current_role
    _current_role = role


def get_current_role() -> str:
    return _current_role


def get_last_results() -> dict:
    """Return the latest query DataFrame, SQL, and chart buffer."""
    return _last_results


# ── Tools ────────────────────────────────────────────────────────────────


@tool
def run_sql_query(sql: str) -> str:
    """Execute a SQL SELECT query on the marketing database.

    Only SELECT statements are allowed.  The single available table is
    **marketing_campaign_performance** with columns: campaign_id,
    campaign_name, channel, impressions, clicks, conversions, spend,
    revenue, date.  The query is validated against the active RBAC role.
    """
    try:
        validated = validate_query(sql, _current_role)
        df = execute_query(validated)

        _last_results["df"] = df
        _last_results["sql"] = validated
        _last_results["chart"] = None  # reset previous chart

        if df.empty:
            return "Query executed successfully but returned no rows."
        return f"Results ({len(df)} rows):\n{df.to_string(index=False)}"

    except (GuardrailError, RBACError) as exc:
        # Surface the friendly RBAC / guardrail message to the LLM
        return str(exc)
    except Exception as exc:
        logger.exception("Query execution failed")
        return f"❌ Query failed: {exc}"


@tool
def generate_chart(chart_type: str, title: str, x_column: str, y_column: str) -> str:
    """Generate a chart from the most recent SQL query results.

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


# ── Dynamic system prompt (rebuilt per role) ─────────────────────────────


def _build_system_prompt(role: str) -> str:
    """Create an RBAC-aware system prompt for *role*."""
    config = ROLE_PERMISSIONS[role]
    allowed = ", ".join(config["allowed_columns"])
    restricted = ", ".join(config["restricted_columns"]) or "none"

    agg_warning = ""
    if config["aggregation_only"]:
        agg_warning = (
            "\n⚠️  AGGREGATION-ONLY ROLE — you MUST use GROUP BY with "
            "aggregate functions (SUM, COUNT, AVG …). "
            "NEVER return raw row-level data for this role.\n"
        )

    return f"""\
You are a marketing analytics assistant.  You convert natural-language
questions into SQL, execute them, explain the results, and optionally
create visualisations.

ACTIVE ROLE : {role}
ALLOWED COLS: {allowed}
RESTRICTED  : {restricted}
{agg_warning}
DATABASE SCHEMA
───────────────
{SCHEMA_DESCRIPTION}

RULES
─────
1. Convert the user's question into a valid **SQLite SELECT** query.
2. ONLY use columns from the ALLOWED list above.
3. ONLY reference the **{TABLE_NAME}** table.
4. NEVER generate INSERT, UPDATE, DELETE, CREATE, DROP, or ALTER.
5. Call `run_sql_query` to execute your SQL.
6. After receiving results, provide a concise natural-language explanation.
7. When a visualisation would help, call `generate_chart`:
   • Trends over time → line
   • Category comparisons → bar
   • Distributions → histogram
   • Proportional breakdowns → pie
8. If the question is unrelated to marketing data, politely decline.
9. Always show the SQL you generated so the user can learn.
10. If a query is blocked by RBAC, relay the access-denied message to the
    user clearly and suggest switching roles.
"""


# ── Agent factory ────────────────────────────────────────────────────────


def create_agent(role: str = "Marketing Analyst"):
    """Build and return a LangGraph ReAct agent tuned for *role*."""
    set_current_role(role)
    llm = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)
    return create_react_agent(
        model=llm,
        tools=[run_sql_query, generate_chart],
        prompt=_build_system_prompt(role),
    )
