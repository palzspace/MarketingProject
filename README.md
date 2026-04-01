# Text2SQL Assistant — Marketing Analytics with RBAC Simulation

A conversational AI agent that converts natural-language questions into SQL,
executes them against a marketing campaign database, and returns **tabular
results**, **natural-language explanations**, and **auto-generated charts** —
all filtered through a **role-based access control (RBAC) simulation layer**.

## Features

| Feature | Details |
| --- | --- |
| **Chat Interface** | Streamlit web UI with conversation history |
| **Text-to-SQL** | Claude converts plain English to SQLite-compatible SQL |
| **RBAC Simulation** | 5 demo personas with column-level access control |
| **Visualisation** | Auto-selects bar / line / histogram / pie charts |
| **Guardrails** | Read-only enforcement, schema validation, keyword blocking |
| **Orchestration** | LangGraph ReAct agent with tool-calling |

## RBAC Personas

| Persona | Access | Restrictions |
| --- | --- | --- |
| **Marketing Analyst** | campaign, channel, impressions, clicks, conversions | No spend/revenue |
| **Marketing Manager** | All columns | None |
| **Finance Viewer** | campaign, channel, spend, revenue | No impressions/clicks/conversions |
| **Executive** | Aggregated summaries only | No row-level detail |
| **Admin** | Full access | None |

## Architecture

```
User Question
     │
     ▼
┌──────────┐     ┌──────────┐     ┌───────────┐
│ Streamlit │────▶│ LangGraph│────▶│   Claude   │
│    UI     │◀────│  Agent   │◀────│  (Sonnet)  │
└──────────┘     └────┬─────┘     └───────────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
        ┌──────────┐   ┌──────────────┐
        │ RBAC     │   │ Matplotlib   │
        │ Validator│   │ Charts       │
        └────┬─────┘   └──────────────┘
             ▼
        ┌──────────┐
        │ SQLite   │
        │ (read-   │
        │  only)   │
        └──────────┘
```

## Quick Start

### 1. Clone and install

```bash
cd MarketingProject
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Generate sample data

```bash
python seed_marketing_data.py
```

### 3. Set your API key

```bash
copy .env.example .env
# Edit .env and add your Anthropic API key
```

### 4. Run the app

```bash
streamlit run app.py
```

The browser opens at **http://localhost:8501** — start asking questions!

## Demo Storyline

1. **Start as Marketing Analyst** — ask for clicks/conversions (allowed)
2. **Ask for spend/revenue** — blocked with friendly message
3. **Switch to Finance Viewer** — same query now works
4. **Switch to Executive** — only aggregated summaries returned
5. **Switch to Admin** — full row-level access

## Project Structure

```
MarketingProject/
├── app.py                     # Streamlit entry point
├── seed_marketing_data.py     # Sample data generator (~1000 rows)
├── visualization.py           # Chart generation (Matplotlib)
├── data/
│   └── marketing_data.csv     # Generated marketing dataset
├── agent/
│   ├── __init__.py
│   ├── graph.py               # LangGraph agent + tools
│   ├── rbac.py                # RBAC simulation engine
│   ├── executor.py            # SQLite setup & read-only execution
│   └── validator.py           # SQL guardrails + RBAC checks
├── config/
│   ├── __init__.py
│   ├── schema.py              # DB schema, paths, constants
│   └── roles.py               # Role definitions & suggested prompts
├── .streamlit/
│   └── config.toml            # Dark theme
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Safety and Guardrails

- **Read-only SQLite** (`?mode=ro`) — writes blocked at engine level
- **Keyword blocking** — INSERT, UPDATE, DELETE, DROP, etc.
- **Table/column validation** — unknown references rejected
- **Multi-statement prevention** — semicolons blocked
- **RBAC enforcement** — column-level and aggregation-level checks

## Streamlit Community Cloud Deployment

1. Push this repo to GitHub
2. Connect via [share.streamlit.io](https://share.streamlit.io)
3. Add `ANTHROPIC_API_KEY` in the Streamlit secrets manager
4. Deploy — done!

## License

MIT
