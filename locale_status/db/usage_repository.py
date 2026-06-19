from __future__ import annotations

from pathlib import Path

import pandas as pd

from locale_status.config.settings import REGION_NAME_ALIASES
from src.db import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_usage_dataset(
    usage_csv_path: Path,
    coords_csv_path: Path,
) -> pd.DataFrame:
    """Load regional electricity usage from the final ERD MySQL table."""
    query = """
        SELECT
            usage_data.record,
            usage_data.sido,
            usage_data.sigungu,
            usage_data.kw_50,
            usage_data.kw_100,
            usage_data.kw_100_dual,
            usage_data.kw_200_dual,
            usage_data.kw_300_dual,
            usage_data.`usage`,
            coord.lat,
            coord.longi AS lon
        FROM tbl_region_elec_usage AS usage_data
        LEFT JOIN tbl_region_coord AS coord
            ON coord.addr = CONCAT(usage_data.sido, ' ', usage_data.sigungu, ' 대한민국')
        ORDER BY usage_data.sido, usage_data.sigungu, usage_data.record
    """

    with get_connection(PROJECT_ROOT / ".env") as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    usage_df = pd.DataFrame(rows)
    if usage_df.empty:
        return usage_df

    usage_df = usage_df.rename(
        columns={
            "sido": "광역지자체",
            "sigungu": "시군구",
            "kw_50": "50키로와트",
            "kw_100": "100키로와트",
            "kw_100_dual": "100키로와트듀얼",
            "kw_200_dual": "200키로와트듀얼",
            "kw_300_dual": "300키로와트듀얼",
            "usage": "사용량(키로와트시)",
        }
    )

    numeric_columns = [
        "50키로와트",
        "100키로와트",
        "100키로와트듀얼",
        "200키로와트듀얼",
        "300키로와트듀얼",
        "사용량(키로와트시)",
        "lat",
        "lon",
    ]
    for column in numeric_columns:
        if column in usage_df.columns:
            usage_df[column] = pd.to_numeric(usage_df[column], errors="coerce")

    usage_df["address"] = (
        usage_df["광역지자체"].astype(str)
        + " "
        + usage_df["시군구"].astype(str)
        + " 대한민국"
    )
    usage_df["api_region"] = usage_df["광역지자체"].map(REGION_NAME_ALIASES)
    return usage_df
