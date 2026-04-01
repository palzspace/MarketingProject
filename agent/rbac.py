"""Application-level RBAC simulation engine.

Sits between SQL generation and SQL execution.  Inspects the generated
SQL, compares referenced columns with the active role's permissions,
and permits / denies / explains accordingly.
"""

import re

from config.roles import ROLE_PERMISSIONS
from config.schema import ALL_COLUMNS


class RBACError(Exception):
    """Raised when a query violates role-based access rules."""


# ── Public helpers ───────────────────────────────────────────────────────


def get_role_config(role: str) -> dict:
    """Return the full RBAC config dict for *role*."""
    if role not in ROLE_PERMISSIONS:
        raise RBACError(f"Unknown role: {role}")
    return ROLE_PERMISSIONS[role]


def get_allowed_columns(role: str) -> list[str]:
    return get_role_config(role)["allowed_columns"]


def get_restricted_columns(role: str) -> list[str]:
    return get_role_config(role)["restricted_columns"]


def is_aggregation_only(role: str) -> bool:
    return get_role_config(role)["aggregation_only"]


# ── SQL inspection (pragmatic regex — good enough for a POC) ─────────────


def extract_columns_from_sql(sql: str) -> set[str]:
    """Return the set of known column names referenced anywhere in *sql*."""
    upper = sql.upper()
    return {col for col in ALL_COLUMNS if re.search(rf"\b{col.upper()}\b", upper)}


def _has_aggregation(sql: str) -> bool:
    """Check whether *sql* uses GROUP BY or aggregate functions."""
    upper = sql.upper()
    if "GROUP BY" in upper:
        return True
    return any(fn in upper for fn in ("SUM(", "COUNT(", "AVG(", "MIN(", "MAX("))


# ── Main validation entry-point ──────────────────────────────────────────


def validate_rbac(sql: str, role: str) -> str:
    """Validate *sql* against the permissions of *role*.

    Returns the SQL unchanged when valid; raises ``RBACError`` otherwise.
    """
    config = get_role_config(role)
    allowed = set(config["allowed_columns"])

    # Expand SELECT * to mean "all columns"
    referenced = (
        set(ALL_COLUMNS)
        if re.search(r"SELECT\s+\*", sql, re.IGNORECASE)
        else extract_columns_from_sql(sql)
    )

    # ── Column-level check ───────────────────────────────────────────
    unauthorized = referenced - allowed
    if unauthorized:
        suggestions = _suggest_roles_for(unauthorized)
        raise RBACError(
            f"🔒 **Access Denied**\n\n"
            f"Your current simulated role **{role}** does not have access "
            f"to: **{', '.join(sorted(unauthorized))}**.\n\n"
            f"💡 Try switching to {suggestions} for this query."
        )

    # ── Aggregation-only check ───────────────────────────────────────
    if config["aggregation_only"] and not _has_aggregation(sql):
        raise RBACError(
            f"🔒 **Aggregation Required**\n\n"
            f"The **{role}** role can only view aggregated summaries. "
            f"Your query attempts to return row-level detail.\n\n"
            f"💡 Try asking for totals, averages, or summaries instead — "
            f"or switch to **Admin** or **Marketing Manager** for detail."
        )

    return sql


# ── Private helpers ──────────────────────────────────────────────────────


def _suggest_roles_for(columns: set[str]) -> str:
    """Return a comma-separated list of roles that can access *columns*."""
    matches = [
        f"**{role}**"
        for role, cfg in ROLE_PERMISSIONS.items()
        if columns <= set(cfg["allowed_columns"])
    ]
    return ", ".join(matches) if matches else "**Admin**"
