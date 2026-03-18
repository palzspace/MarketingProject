"""Configuration and constants for the Marketing Text-to-SQL Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "marketing.db"
CSV_PATH = DATA_DIR / "marketing_data.csv"

# --- Database Schema ---
TABLE_NAME = "campaigns"

SCHEMA_DESCRIPTION = """
Table: campaigns
Columns:
  - campaign_id    (INTEGER) : Unique row identifier
  - campaign_name  (TEXT)    : Name of the marketing campaign
  - channel        (TEXT)    : Marketing channel — one of Email, Social Media, Paid Ads, SEO, Content
  - impressions    (INTEGER) : Number of ad impressions
  - clicks         (INTEGER) : Number of clicks received
  - conversions    (INTEGER) : Number of conversions (purchases/sign-ups)
  - spend          (REAL)    : Amount spent in USD
  - revenue        (REAL)    : Revenue generated in USD
  - date           (TEXT)    : Record date in YYYY-MM-DD format
""".strip()

ALLOWED_TABLES = {"campaigns"}

ALLOWED_COLUMNS = {
    "campaign_id",
    "campaign_name",
    "channel",
    "impressions",
    "clicks",
    "conversions",
    "spend",
    "revenue",
    "date",
}

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

# --- LLM ---
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
