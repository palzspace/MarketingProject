# 📊 Marketing Text-to-SQL Agent (POC)

A conversational AI agent that converts natural-language questions into SQL,
executes them against a marketing campaign database, and returns **tabular
results**, **natural-language explanations**, and **auto-generated charts**.

## ✨ Features

| Feature                  | Details                                              |
| ------------------------ | ---------------------------------------------------- |
| **Chat Interface**       | Streamlit web UI with conversation history            |
| **Text → SQL**           | Claude converts plain English to SQLite-compatible SQL |
| **Visualisation**        | Auto-selects bar / line / histogram / pie charts      |
| **Guardrails**           | Read-only enforcement, schema validation, keyword blocking |
| **Orchestration**        | LangChain agent with tool-calling                     |
| **Session Memory**       | Multi-turn conversations with context                 |

## 🏗️ Architecture

```
User Question
     │
     ▼
┌──────────┐     ┌──────────┐     ┌───────────┐
│ Streamlit │────▶│ LangChain│────▶│   Claude   │
│    UI     │◀────│  Agent   │◀────│  (Sonnet)  │
└──────────┘     └────┬─────┘     └───────────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
        ┌──────────┐   ┌──────────────┐
        │ SQLite   │   │ Matplotlib   │
        │ (read-   │   │ Charts       │
        │  only)   │   └──────────────┘
        └──────────┘
```

## 🚀 Quick Start

### 1. Clone & install

```bash
cd MarketingProject
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Set your API key

```bash
copy .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Run the app

```bash
streamlit run app.py
```

The browser will open at **http://localhost:8501** — start asking questions!

## 💬 Example Questions

- *What is the total revenue by channel?*
- *Which campaign had the highest ROI?*
- *Show me monthly spend trends*
- *Compare conversions across all campaigns*
- *Top 5 campaigns by revenue*

## 🗂️ Project Structure

```
MarketingProject/
├── app.py                  # Streamlit entry point
├── data/
│   └── marketing_data.csv  # Sample 60-row marketing dataset
├── src/
│   ├── __init__.py
│   ├── config.py           # Paths, schema, constants
│   ├── database.py         # CSV → SQLite loader & query runner
│   ├── guardrails.py       # SQL validation & safety checks
│   ├── visualization.py    # Chart generation (Matplotlib)
│   └── agent.py            # LangChain agent + Claude tools
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔒 Safety & Guardrails

- **Read-only SQLite connection** (`?mode=ro`) — writes are blocked at the engine level.
- **Keyword blocking** — `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER`, etc.
- **Table/column validation** — queries referencing unknown tables are rejected.
- **Multi-statement prevention** — semicolons inside queries are blocked.
- **Scope enforcement** — off-topic questions receive a polite fallback.

## 🛣️ Future Enhancements

- [ ] Human-in-the-loop SQL approval before execution
- [ ] Semantic layer (business-friendly column aliases)
- [ ] Query history & session export
- [ ] Snowflake / PostgreSQL backend support
- [ ] Streaming LLM responses

## 📄 License

MIT
