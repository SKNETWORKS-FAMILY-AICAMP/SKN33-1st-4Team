from __future__ import annotations

"""SQL for the locale available-charger view.

The current ERDCloud export, resources/skn_team4_1st_pro.sql, uses:
- tbl_charge_station(cs_id, cs_name, cs_addr, cs_lat, cs_longi)
- tbl_charger(cp_id, cp_name, cp_charge_type, cp_stat, cp_type, cs_id)
- map_station_region_cd(cs_id, region_cd)
- tbl_region_cd(region_cd, region_name, region_level, parent_cd)

The service/UI still expects OpenAPI-like aliases such as stat_id, stat_nm,
chger_id, chger_type, stat, zcode, and zscode. This query maps the local
dataset into those aliases.
"""


AVAILABLE_CHARGERS_BASE_QUERY = """
SELECT
    s.zcode,
    s.zscode,
    s.stat_id,
    s.stat_nm,
    s.addr,
    s.addr_detail,
    s.lat,
    s.lng,
    s.busi_nm,
    s.busi_call,
    c.chger_id,
    c.chger_type,
    c.output,
    c.method,
    c.stat,
    c.stat_upd_dt,
    c.fetched_at
FROM (
    SELECT
        cs.cs_id AS stat_id,
        cs.cs_name AS stat_nm,
        cs.cs_addr AS addr,
        NULL AS addr_detail,
        cs.cs_lat AS lat,
        cs.cs_longi AS lng,
        NULL AS busi_nm,
        NULL AS busi_call,
        CAST(COALESCE(parent_region.region_cd, region.region_cd) AS CHAR) AS zcode,
        CAST(region.region_cd AS CHAR) AS zscode
    FROM tbl_charge_station AS cs
    LEFT JOIN map_station_region_cd AS station_region
        ON station_region.cs_id = cs.cs_id
    LEFT JOIN tbl_region_cd AS region
        ON region.region_cd = station_region.region_cd
    LEFT JOIN tbl_region_cd AS parent_region
        ON parent_region.region_cd = region.parent_cd
) AS s
INNER JOIN (
    SELECT
        charger.cs_id AS stat_id,
        charger.cp_id AS chger_id,
        charger.cp_charge_type AS chger_type,
        NULL AS output,
        charger.cp_type AS method,
        CASE charger.cp_stat
            WHEN 1 THEN '2'
            WHEN 2 THEN '3'
            WHEN 3 THEN '5'
            WHEN 4 THEN '1'
            WHEN 5 THEN '1'
            WHEN 6 THEN '9'
            WHEN 7 THEN '4'
            ELSE '9'
        END AS stat,
        NULL AS stat_upd_dt,
        NULL AS fetched_at
    FROM tbl_charger AS charger
) AS c
    ON s.stat_id = c.stat_id
WHERE c.stat = %s
"""


AVAILABLE_CHARGERS_ORDER_BY = """
ORDER BY
    s.zcode,
    s.stat_nm,
    c.chger_type DESC,
    c.chger_id
"""
