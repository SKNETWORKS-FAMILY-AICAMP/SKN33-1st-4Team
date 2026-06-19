import mysql.connector

from config.settings import DatabaseSettings
from db.connection import get_connection

def find_station_map(db_settings:DatabaseSettings) -> list:
    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select
                    cs_id, cs_name, cs_lat, cs_longi
                from
                    tbl_charge_station
                
                """)
            rows = cursor.fetchall()

    return [rows]


def find_station_details(db_settings:DatabaseSettings, keyword:str) -> list:

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select 
                    cs.cs_id, cs.cs_name, cs.cs_addr
                    , sum(if(cp.cp_charge_type=1, 1, 0)) as 완속
                    , sum(if(cp.cp_charge_type=2, 1, 0)) as 급속
                from tbl_charge_station cs
                    join tbl_charger cp
                    on cs.cs_id = cp.cs_id
                where cs.cs_id = %s
                group by cs.cs_id
                """, [keyword]
            )
            rows = cursor.fetchall()

    return rows

def find_station_by_region_summary(db_settings:DatabaseSettings) -> list:

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select 
                    a.region_cd, b.region_cd
                    ,a.region_name, b.region_name
                    , count(cs.cs_id)
                from tbl_region_cd a
                    , tbl_region_cd b
                    , tbl_charge_station cs
                    , map_station_region_cd sr
                where 
                    a.parent_cd is null 
                    and sr.cs_id = cs.cs_id
                    and sr.region_cd = b.region_cd
                    and a.region_cd = b.parent_cd
                group by a.region_cd, b.region_cd
                """
            )
            rows = cursor.fetchall()

    return rows

def find_region_sido(db_settings:DatabaseSettings) -> list:

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select region_cd, region_name 
                from tbl_region_cd
                where parent_cd is null
                """
            )
            rows = cursor.fetchall()

    return rows

def find_region_sigungu(db_settings:DatabaseSettings, keyword:str) -> list:

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select region_cd, region_name 
                from tbl_region_cd
                where parent_cd is not null 
                and parent_cd = %s
                """
            , [keyword])
            rows = cursor.fetchall()

    return rows

def find_station_by_region(db_settings:DatabaseSettings, keyword:str) -> list:

    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select 
                    b.region_cd as region_cd
                    ,concat(a.region_name,' ', b.region_name) as region_name
                    , cs.cs_id, cs.cs_name
                    , cs.cs_lat, cs.cs_longi
                from tbl_region_cd a
                    , tbl_region_cd b
                    , tbl_charge_station cs
                    , map_station_region_cd sr
                where 
                    a.parent_cd is null 
                    and sr.cs_id = cs.cs_id
                    and sr.region_cd = b.region_cd
                    and a.region_cd = b.parent_cd
                    and b.region_cd like concat(%s,'%')
                """
            , [keyword])
            rows = cursor.fetchall()

    return rows


def find_region_elec_usage(db_settings: DatabaseSettings) -> list:
    with get_connection(db_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                select
                    record,
                    sido,
                    sigungu,
                    kw_50,
                    kw_100,
                    kw_100_dual,
                    kw_200_dual,
                    kw_300_dual,
                    `usage`
                from tbl_region_elec_usage
                order by sido, sigungu, record
                """
            )
            rows = cursor.fetchall()

    return rows

def is_duplicate_key_error(error: mysql.connector.Error) -> bool:
    """DB 작업 중 duplicate key 오류인지 확인하는 보조 함수."""

    return error.errno == 1062
