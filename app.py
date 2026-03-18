"""Streamlit chat UI for the Marketing Text-to-SQL Agent.

Run with:  streamlit run app.py
"""

import logging

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from src.agent import create_agent, get_last_results
from src.database import init_database

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(name)s]  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Marketing SQL Agent", page_icon="📊", layout="wide")
st.title("📊 Marketing Text-to-SQL Agent")
st.caption("Ask questions about marketing campaigns in plain English!")


# ── Sidebar with sample questions ────────────────────────────────────────
with st.sidebar:
    st.header("💡 Try asking…")
    sample_questions = [
        "What is the total revenue by channel?",
        "Which campaign had the highest ROI?",
        "Show me monthly spend trends",
        "Compare conversions across all campaigns",
        "What's the average click-through rate by channel?",
        "Top 5 campaigns by revenue",
    ]
    for q in sample_questions:
        st.markdown(f"- *{q}*")

    st.divider()
    st.markdown(
        "Built with **LangChain**, **Claude**, and **Streamlit**. "
        "All queries are **read-only** — your data is safe! 🔒"
    )


# ── Session state init ───────────────────────────────────────────────────
if "db_ready" not in st.session_state:
    init_database()
    st.session_state.db_ready = True

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── Render previous messages ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("dataframe") is not None:
            st.dataframe(msg["dataframe"], use_container_width=True)
        if msg.get("chart") is not None:
            st.image(msg["chart"])


# ── Chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about marketing campaigns…"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Crunching the numbers… 🔍"):
            try:
                messages = list(st.session_state.chat_history) + [
                    HumanMessage(content=prompt),
                ]
                response = st.session_state.agent.invoke(
                    {"messages": messages}
                )
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
                    results["chart"] = None  # consume so it isn't shown twice

                st.session_state.messages.append(assistant_msg)

                # Maintain LangChain memory
                st.session_state.chat_history.extend(
                    [
                        HumanMessage(content=prompt),
                        AIMessage(content=output),
                    ]
                )

            except Exception:
                logger.exception("Agent error")
                error_text = "❌ Something went wrong. Check the logs or try rephrasing your question."
                st.error(error_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text}
                )
