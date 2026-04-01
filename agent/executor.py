"""SQLite database setup and read-only query execution."""

import logging
import sqlite3

import pandas as pd

from config.schema import CSV_PATH, DB_PATH, TABLE_NAME

logger = logging.getLogger(__name__)


def init_database() -> None:
    """Load the CSV dataset into a file-based SQLite database.

    Recreates the table on every startup so the DB always matches the CSV.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        logger.info(
            "Database initialised — %d rows loaded into '%s'.",
            len(df),
            TABLE_NAME,
        )
    finally:
        conn.close()


def execute_query(sql: str) -> pd.DataFrame:
    """Execute *sql* in **read-only** mode and return a DataFrame.

    The connection uses SQLite's ``?mode=ro`` URI flag — even if all
    application guardrails are bypassed, the engine itself refuses writes.
    """
    ro_uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(ro_uri, uri=True)
    try:
        df = pd.read_sql_query(sql, conn)
        logger.info("Query OK — %d row(s) returned.", len(df))
        return df
    finally:
        conn.close()
