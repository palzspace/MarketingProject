"""RBAC role definitions and per-persona suggested prompts.

Each role controls:
  - which columns the persona may access
  - which columns are explicitly restricted
  - whether the persona is limited to aggregated results only
"""

ROLE_PERMISSIONS: dict[str, dict] = {
    "Marketing Analyst": {
        "allowed_columns": [
            "campaign_id",
            "campaign_name",
            "channel",
            "impressions",
            "clicks",
            "conversions",
            "date",
        ],
        "aggregation_only": False,
        "description": "Campaign and channel performance metrics",
        "restricted_columns": ["spend", "revenue"],
    },
    "Marketing Manager": {
        "allowed_columns": [
            "campaign_id",
            "campaign_name",
            "channel",
            "impressions",
            "clicks",
            "conversions",
            "spend",
            "revenue",
            "date",
        ],
        "aggregation_only": False,
        "description": "All marketing metrics across campaigns and channels",
        "restricted_columns": [],
    },
    "Finance Viewer": {
        "allowed_columns": [
            "campaign_id",
            "campaign_name",
            "channel",
            "spend",
            "revenue",
            "date",
        ],
        "aggregation_only": False,
        "description": "Spend and revenue summaries",
        "restricted_columns": ["impressions", "clicks", "conversions"],
    },
    "Executive": {
        "allowed_columns": [
            "channel",
            "spend",
            "revenue",
            "impressions",
            "clicks",
            "conversions",
            "date",
        ],
        "aggregation_only": True,
        "description": "Aggregated performance summary only",
        "restricted_columns": ["campaign_id", "campaign_name"],
    },
    "Admin": {
        "allowed_columns": [
            "campaign_id",
            "campaign_name",
            "channel",
            "impressions",
            "clicks",
            "conversions",
            "spend",
            "revenue",
            "date",
        ],
        "aggregation_only": False,
        "description": "Full access to all data and all rows",
        "restricted_columns": [],
    },
}

ROLES: list[str] = list(ROLE_PERMISSIONS.keys())

# ── Suggested prompts shown in the sidebar per role ──────────────────────
SUGGESTED_PROMPTS: dict[str, list[str]] = {
    "Marketing Analyst": [
        "Show clicks by channel",
        "Which campaign has the highest conversions?",
        "Compare impressions across campaigns",
        "Show conversion trends by month",
    ],
    "Marketing Manager": [
        "Show total revenue by channel",
        "Which campaign had the highest ROAS?",
        "Compare spend vs revenue by campaign",
        "Show monthly performance trends",
    ],
    "Finance Viewer": [
        "Show spend and revenue by month",
        "What is ROAS by channel?",
        "Show total spend by campaign",
        "Revenue trend over time",
    ],
    "Executive": [
        "Show total revenue trend by month",
        "Summarize performance by channel",
        "What is overall ROAS?",
        "Show high-level KPI summary",
    ],
    "Admin": [
        "Show all data for top 5 campaigns by revenue",
        "Compare all metrics across channels",
        "Show detailed campaign performance",
        "Full breakdown by campaign and channel",
    ],
}
