"""SQL validation and safety guardrails.

Defence-in-depth: even though the SQLite connection is read-only,
we pre-validate every query so the LLM gets clear, friendly error
messages instead of cryptic database exceptions.
"""

import logging
import re

from src.config import ALLOWED_TABLES, BLOCKED_KEYWORDS

logger = logging.getLogger(__name__)


class GuardrailError(Exception):
    """Raised when a query violates safety rules."""


def validate_query(sql: str) -> str:
    """Return the cleaned SQL string, or raise *GuardrailError*."""
    cleaned = sql.strip().rstrip(";")
    upper = cleaned.upper()

    # 1. Must start with SELECT
    if not upper.startswith("SELECT"):
        raise GuardrailError(
            "🚫 I can only run **SELECT** queries. "
            "Data modifications are not allowed."
        )

    # 2. Reject blocked keywords
    for kw in BLOCKED_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            raise GuardrailError(
                f"🚫 `{kw}` operations are not permitted. "
                "I'm a strictly read-only assistant!"
            )

    # 3. Validate referenced tables (after FROM / JOIN)
    referenced = {
        m.lower()
        for m in re.findall(r"(?:FROM|JOIN)\s+(\w+)", cleaned, re.IGNORECASE)
    }
    unknown = referenced - ALLOWED_TABLES
    if unknown:
        raise GuardrailError(
            f"🚫 Unknown table(s): **{', '.join(sorted(unknown))}**. "
            f"Available tables: {', '.join(sorted(ALLOWED_TABLES))}."
        )

    # 4. Block sub-query tricks like "; DROP" hidden after a semicolon
    if ";" in cleaned:
        raise GuardrailError(
            "🚫 Multi-statement queries are not allowed."
        )

    logger.info("Guardrails passed for query: %s", cleaned)
    return cleaned
