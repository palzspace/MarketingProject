"""SQL validation and safety guardrails (with RBAC integration).

Defence-in-depth: the SQLite connection is read-only *and* we
pre-validate every query so the LLM receives clear, friendly
error messages instead of cryptic database exceptions.
"""

import logging
import re

from config.schema import ALLOWED_TABLES, BLOCKED_KEYWORDS
from agent.rbac import RBACError, validate_rbac  # noqa: F401 — re-export

logger = logging.getLogger(__name__)


class GuardrailError(Exception):
    """Raised when a query violates safety rules."""


def validate_query(sql: str, role: str) -> str:
    """Return the cleaned SQL if it passes every check.

    Raises ``GuardrailError`` for safety violations and
    ``RBACError`` for role-permission violations.
    """
    cleaned = sql.strip().rstrip(";")
    upper = cleaned.upper()

    # 1. Must start with SELECT
    if not upper.startswith("SELECT"):
        raise GuardrailError(
            "🚫 This assistant supports **read-only analytical queries** only. "
            "Data modifications are not allowed."
        )

    # 2. Block dangerous keywords
    for kw in BLOCKED_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            raise GuardrailError(
                f"🚫 `{kw}` operations are not permitted. "
                "This is a read-only analytics assistant."
            )

    # 3. Validate referenced tables
    referenced = {
        m.lower()
        for m in re.findall(r"(?:FROM|JOIN)\s+(\w+)", cleaned, re.IGNORECASE)
    }
    unknown = referenced - ALLOWED_TABLES
    if unknown:
        raise GuardrailError(
            f"🚫 Unknown table(s): **{', '.join(sorted(unknown))}**. "
            f"Available: {', '.join(sorted(ALLOWED_TABLES))}."
        )

    # 4. Block multi-statement queries
    if ";" in cleaned:
        raise GuardrailError("🚫 Multi-statement queries are not allowed.")

    # 5. RBAC column & aggregation checks
    validate_rbac(cleaned, role)

    logger.info("All guardrails passed for: %s", cleaned)
    return cleaned
