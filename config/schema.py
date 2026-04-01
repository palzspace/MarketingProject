"""Database schema, paths, and application-wide constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "marketing.db"
CSV_PATH = DATA_DIR / "marketing_data.csv"

# ── Database Schema ──────────────────────────────────────────────────────
TABLE_NAME = "marketing_campaign_performance"

ALL_COLUMNS = [
    "campaign_id",
    "campaign_name",
    "channel",
    "impressions",
    "clicks",
    "conversions",
    "spend",
    "revenue",
    "date",
]

SCHEMA_DESCRIPTION = f"""\
Table: {TABLE_NAME}
Columns:
  - campaign_id    (INTEGER) : Unique row identifier
  - campaign_name  (TEXT)    : Name of the marketing campaign
  - channel        (TEXT)    : Marketing channel — Google Ads, Facebook, LinkedIn, Email, or Display
  - impressions    (INTEGER) : Number of ad impressions
  - clicks         (INTEGER) : Number of clicks received
  - conversions    (INTEGER) : Number of conversions (purchases / sign-ups)
  - spend          (REAL)    : Amount spent in USD
  - revenue        (REAL)    : Revenue generated in USD
  - date           (TEXT)    : Record date in YYYY-MM-DD format
"""

ALLOWED_TABLES = {TABLE_NAME}

# Keywords that must NEVER appear in an executed query
BLOCKED_KEYWORDS = frozenset(
    {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "EXEC",
        "EXECUTE",
        "GRANT",
        "REVOKE",
        "ATTACH",
        "DETACH",
    }
)

# ── LLM ──────────────────────────────────────────────────────────────────
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
