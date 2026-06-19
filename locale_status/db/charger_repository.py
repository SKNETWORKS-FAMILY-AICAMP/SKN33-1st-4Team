from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.db import get_connection


def load_charger_snapshot_from_db(
    project_root: Path,
    *,
    zcode: str | None = None,
) -> pd.DataFrame:
    """Load charger rows from the final ERD schema using API-compatible aliases."""
    query = """
        SELECT
            CAST(COALESCE(parent_region.region_cd, region.region_cd) AS CHAR) AS statZcode,
            CAST(region.region_cd AS CHAR) AS statZscode,
            CAST(station.cs_id AS CHAR) AS statId,
            station.cs_name AS statNm,
            station.cs_addr AS addr,
            NULL AS addrDetail,
            station.cs_lat AS lat,
            station.cs_longi AS lng,
            CAST(charger.cp_id AS CHAR) AS chgerId,
            CAST(charger.cp_charge_type AS CHAR) AS chgerType,
            NULL AS output,
            CAST(charger.cp_type AS CHAR) AS method,
            CASE COALESCE(latest_log.cp_stat, charger.cp_stat)
                WHEN 1 THEN '2'
                WHEN 2 THEN '3'
                WHEN 3 THEN '5'
                WHEN 4 THEN '1'
                WHEN 5 THEN '1'
                WHEN 6 THEN '9'
                WHEN 7 THEN '4'
                ELSE '9'
            END AS stat,
            latest_log.stat_upd_dt AS statUpdDt
        FROM tbl_charge_station AS station
        INNER JOIN tbl_charger AS charger
            ON charger.cs_id = station.cs_id
        LEFT JOIN map_station_region_cd AS station_region
            ON station_region.cs_id = station.cs_id
        LEFT JOIN tbl_region_cd AS region
            ON region.region_cd = station_region.region_cd
        LEFT JOIN tbl_region_cd AS parent_region
            ON parent_region.region_cd = region.parent_cd
        LEFT JOIN (
            SELECT log_rows.cp_id, log_rows.cp_stat, log_rows.stat_upd_dt
            FROM tbl_charger_status_log AS log_rows
            INNER JOIN (
                SELECT cp_id, MAX(collected_at) AS collected_at
                FROM tbl_charger_status_log
                GROUP BY cp_id
            ) AS latest
                ON latest.cp_id = log_rows.cp_id
               AND latest.collected_at = log_rows.collected_at
        ) AS latest_log
            ON latest_log.cp_id = charger.cp_id
        WHERE (%s IS NULL OR CAST(COALESCE(parent_region.region_cd, region.region_cd) AS CHAR) = %s)
        ORDER BY station.cs_name, charger.cp_id
    """

    with get_connection(project_root / ".env") as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, (zcode, zcode))
            rows = cursor.fetchall()

    charger_df = pd.DataFrame(rows)
    if charger_df.empty:
        return charger_df

    charger_df = charger_df.rename(
        columns={
            "statZcode": "zcode",
            "statZscode": "zscode",
            "addrDetail": "addrDetail",
        }
    )
    for column in ["lat", "lng", "output"]:
        if column in charger_df.columns:
            charger_df[column] = pd.to_numeric(charger_df[column], errors="coerce")

    return charger_df
