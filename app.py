"""Streamlit UI for the Marketing Text-to-SQL Agent with RBAC Simulation.

Run with:  streamlit run app.py
"""

import logging

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from agent.executor import init_database
from agent.graph import create_agent, get_last_results, set_current_role
from config.roles import ROLES, ROLE_PERMISSIONS, SUGGESTED_PROMPTS

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(name)s]  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Text2SQL Assistant",
    page_icon="\U0001f4ca",
    layout="wide",
)

# ── Session state init ───────────────────────────────────────────────────
if "role" not in st.session_state:
    st.session_state.role = "Marketing Analyst"
if "db_ready" not in st.session_state:
    init_database()
    st.session_state.db_ready = True
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Header with role selector (top-right) ────────────────────────────────
top_left, top_right = st.columns([3, 1])

with top_left:
    st.title("\U0001f4ca Text2SQL Assistant")

with top_right:
    selected_role = st.selectbox(
        "\U0001f3ad Simulate User Role",
        ROLES,
        index=ROLES.index(st.session_state.role),
        key="role_selector",
    )

# Handle role change — clear chat and rebuild agent
if selected_role != st.session_state.role:
    st.session_state.role = selected_role
    st.session_state.messages = []
    st.session_state.chat_history = []
    if "agent" in st.session_state:
        del st.session_state["agent"]
    st.rerun()

# Keep the module-level role in sync with session state
set_current_role(st.session_state.role)

# Build agent on first run (or after a role switch)
if "agent" not in st.session_state:
    st.session_state.agent = create_agent(st.session_state.role)

# ── Role info banner ─────────────────────────────────────────────────────
role = st.session_state.role
role_cfg = ROLE_PERMISSIONS[role]

_ROLE_COLORS = {
    "Marketing Analyst": ("#4C9AFF", "\U0001f4c8"),
    "Marketing Manager": ("#36B37E", "\U0001f4ca"),
    "Finance Viewer":    ("#FF8B00", "\U0001f4b0"),
    "Executive":         ("#FF5630", "\U0001f451"),
    "Admin":             ("#6554C0", "\U0001f6e1\ufe0f"),
}
accent, icon = _ROLE_COLORS.get(role, ("#888", "\U0001f464"))

st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 12px 20px; border-radius: 10px; margin-bottom: 12px;
        border-left: 4px solid {accent};
    ">
        <span style="color: white; font-weight: 600;">
            {icon} Active Role: {role}
        </span><br>
        <span style="color: #ccc; font-size: 0.85em;">
            {role_cfg['description']}
        </span>
        {"<br><span style='color: #FF8B00; font-size: 0.85em;'>"
         "&#9888;&#65039; Aggregation-only mode</span>"
         if role_cfg['aggregation_only'] else ""}
    </div>
    """,
    unsafe_allow_html=True,
)

# Allowed-columns expander
with st.expander("\U0001f511 Access scope for this role"):
    st.markdown(
        "**Allowed:** "
        + " \u00b7 ".join(f"`{c}`" for c in role_cfg["allowed_columns"])
    )
    if role_cfg["restricted_columns"]:
        st.markdown(
            "**Restricted:** "
            + " \u00b7 ".join(f"`{c}`" for c in role_cfg["restricted_columns"])
        )
    if role_cfg["aggregation_only"]:
        st.info("This role can only view **aggregated summaries** (no row-level detail).")
    st.caption("Results are filtered based on your role permissions.")

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("\U0001f4a1 Suggested Queries")
    st.caption(f"for **{role}**")
    for q in SUGGESTED_PROMPTS.get(role, []):
        st.markdown(f"- *{q}*")

    st.divider()

    st.header("\U0001f4ca Dataset Info")
    st.markdown(
        """
**Table:** `marketing_campaign_performance`

**Channels:** Google Ads, Facebook, LinkedIn, Email, Display

**Metrics:** impressions, clicks, conversions, spend, revenue

**Records:** ~1 000 rows \u00b7 12 campaigns \u00b7 Jan 2024 \u2013 Jun 2025
        """
    )

    st.divider()
    st.markdown(
        "Built with **LangChain**, **Claude**, and **Streamlit**. "
        "All queries are **read-only** \U0001f512"
    )

# ── Render previous messages ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("dataframe") is not None:
            st.dataframe(msg["dataframe"], use_container_width=True)
        if msg.get("chart") is not None:
            st.image(msg["chart"])

# ── Chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about marketing campaigns\u2026"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Analysing with RBAC checks\u2026 \U0001f50d"):
            try:
                messages = list(st.session_state.chat_history) + [
                    HumanMessage(content=prompt),
                ]
                response = st.session_state.agent.invoke({"messages": messages})
                output = response["messages"][-1].content
                st.markdown(output)

                # Attach data artefacts
                results = get_last_results()
                assistant_msg: dict = {"role": "assistant", "content": output}

                if results.get("df") is not None and not results["df"].empty:
                    st.dataframe(results["df"], use_container_width=True)
                    assistant_msg["dataframe"] = results["df"]

                if results.get("chart") is not None:
                    st.image(results["chart"])
                    assistant_msg["chart"] = results["chart"]
                    results["chart"] = None  # consume once

                st.session_state.messages.append(assistant_msg)

                # Maintain LangChain conversation memory
                st.session_state.chat_history.extend(
                    [
                        HumanMessage(content=prompt),
                        AIMessage(content=output),
                    ]
                )

            except Exception:
                logger.exception("Agent error")
                err = (
                    "Something went wrong. "
                    "Check the logs or try rephrasing your question."
                )
                st.error(err)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err}
                )
