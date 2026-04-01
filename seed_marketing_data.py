"""Generate a realistic sample marketing-campaign dataset (~1 000 rows).

Run once:
    python seed_marketing_data.py

The output CSV is written to  data/marketing_data.csv  and can be loaded
straight into SQLite by the application.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_PATH = OUTPUT_DIR / "marketing_data.csv"

# ── Campaign definitions ─────────────────────────────────────────────────
# Each campaign has a date range, a set of channels, and baseline metrics.
# The generator creates one row per (campaign × channel × week).

CHANNELS = ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"]

CAMPAIGNS = [
    {
        "name": "Spring Sale 2024",
        "start": date(2024, 3, 1),
        "end": date(2024, 5, 17),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 15_000,
        "base_ctr": 0.035,
        "base_cvr": 0.08,
        "base_spend": 550,
        "base_roas": 3.0,
    },
    {
        "name": "Summer Blast 2024",
        "start": date(2024, 6, 1),
        "end": date(2024, 8, 31),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 18_000,
        "base_ctr": 0.032,
        "base_cvr": 0.07,
        "base_spend": 620,
        "base_roas": 2.8,
    },
    {
        "name": "Back to School 2024",
        "start": date(2024, 8, 5),
        "end": date(2024, 10, 13),
        "channels": ["Google Ads", "Facebook", "Email", "Display"],
        "base_impressions": 12_000,
        "base_ctr": 0.030,
        "base_cvr": 0.09,
        "base_spend": 480,
        "base_roas": 3.2,
    },
    {
        "name": "Fall Promo 2024",
        "start": date(2024, 9, 16),
        "end": date(2024, 12, 1),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 14_000,
        "base_ctr": 0.033,
        "base_cvr": 0.085,
        "base_spend": 530,
        "base_roas": 2.9,
    },
    {
        "name": "Holiday Special 2024",
        "start": date(2024, 11, 1),
        "end": date(2025, 1, 12),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 22_000,
        "base_ctr": 0.040,
        "base_cvr": 0.10,
        "base_spend": 750,
        "base_roas": 3.5,
    },
    {
        "name": "New Year Push 2025",
        "start": date(2025, 1, 1),
        "end": date(2025, 3, 16),
        "channels": ["Google Ads", "Facebook", "Email", "Display"],
        "base_impressions": 13_000,
        "base_ctr": 0.034,
        "base_cvr": 0.075,
        "base_spend": 500,
        "base_roas": 2.7,
    },
    {
        "name": "Brand Awareness Q1",
        "start": date(2025, 1, 6),
        "end": date(2025, 6, 29),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 25_000,
        "base_ctr": 0.020,
        "base_cvr": 0.04,
        "base_spend": 400,
        "base_roas": 1.8,
    },
    {
        "name": "Product Launch Alpha",
        "start": date(2025, 3, 3),
        "end": date(2025, 5, 4),
        "channels": ["Google Ads", "Facebook", "LinkedIn", "Email", "Display"],
        "base_impressions": 20_000,
        "base_ctr": 0.038,
        "base_cvr": 0.065,
        "base_spend": 680,
        "base_roas": 2.5,
    },
    {
        "name": "Retargeting Wave",
        "start": date(2024, 2, 5),
        "end": date(2024, 8, 25),
        "channels": ["Google Ads", "Facebook", "Display"],
        "base_impressions": 10_000,
        "base_ctr": 0.055,
        "base_cvr": 0.12,
        "base_spend": 350,
        "base_roas": 4.0,
    },
    {
        "name": "Loyalty Rewards",
        "start": date(2024, 1, 1),
        "end": date(2025, 4, 28),
        "channels": ["Email", "Display", "Facebook"],
        "base_impressions": 8_000,
        "base_ctr": 0.060,
        "base_cvr": 0.14,
        "base_spend": 200,
        "base_roas": 5.5,
    },
    {
        "name": "Flash Sale Events",
        "start": date(2024, 4, 1),
        "end": date(2024, 6, 23),
        "channels": ["Google Ads", "Facebook", "Email", "Display"],
        "base_impressions": 16_000,
        "base_ctr": 0.042,
        "base_cvr": 0.11,
        "base_spend": 600,
        "base_roas": 3.8,
    },
    {
        "name": "Content Marketing Push",
        "start": date(2024, 4, 8),
        "end": date(2024, 9, 30),
        "channels": ["LinkedIn", "Facebook", "Email", "Display"],
        "base_impressions": 11_000,
        "base_ctr": 0.025,
        "base_cvr": 0.05,
        "base_spend": 300,
        "base_roas": 2.2,
    },
]

# Channel-specific multipliers — each channel behaves differently
CHANNEL_MODS = {
    "Google Ads": {"imp": 1.2, "ctr": 1.10, "cvr": 1.00, "spend": 1.30, "roas": 1.10},
    "Facebook":   {"imp": 1.5, "ctr": 0.85, "cvr": 0.90, "spend": 0.80, "roas": 0.90},
    "LinkedIn":   {"imp": 0.6, "ctr": 0.70, "cvr": 1.20, "spend": 1.50, "roas": 1.25},
    "Email":      {"imp": 0.4, "ctr": 1.50, "cvr": 1.40, "spend": 0.25, "roas": 3.00},
    "Display":    {"imp": 2.0, "ctr": 0.50, "cvr": 0.55, "spend": 0.65, "roas": 0.70},
}


def _weeks_between(start: date, end: date):
    """Yield the Monday of every ISO week in [start, end]."""
    current = start - timedelta(days=start.weekday())  # snap to Monday
    while current <= end:
        yield current
        current += timedelta(weeks=1)


def _jitter(value: float, pct: float = 0.20) -> float:
    """Apply ±pct random jitter to *value*."""
    return value * random.uniform(1 - pct, 1 + pct)


def generate_rows() -> list[dict]:
    """Return a list of row dicts ready for CSV export."""
    rows: list[dict] = []
    row_id = 1

    for camp in CAMPAIGNS:
        for channel in camp["channels"]:
            mod = CHANNEL_MODS[channel]

            for week_date in _weeks_between(camp["start"], camp["end"]):
                impressions = int(_jitter(camp["base_impressions"] * mod["imp"]))
                ctr = _jitter(camp["base_ctr"] * mod["ctr"], 0.15)
                clicks = int(impressions * ctr)
                cvr = _jitter(camp["base_cvr"] * mod["cvr"], 0.15)
                conversions = max(1, int(clicks * cvr))
                spend = round(_jitter(camp["base_spend"] * mod["spend"]), 2)
                revenue = round(spend * _jitter(camp["base_roas"] * mod["roas"], 0.15), 2)

                rows.append(
                    {
                        "campaign_id": row_id,
                        "campaign_name": camp["name"],
                        "channel": channel,
                        "impressions": impressions,
                        "clicks": clicks,
                        "conversions": conversions,
                        "spend": spend,
                        "revenue": revenue,
                        "date": week_date.isoformat(),
                    }
                )
                row_id += 1

    return rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = generate_rows()

    fieldnames = [
        "campaign_id", "campaign_name", "channel",
        "impressions", "clicks", "conversions",
        "spend", "revenue", "date",
    ]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Generated {len(rows)} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
