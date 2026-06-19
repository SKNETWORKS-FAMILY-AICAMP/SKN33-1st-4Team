from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv


LOCALE_SEARCH_CACHE_TYPE = "locale_search"
CACHE_MINUTES = 30

DB_TO_DF_COLUMNS = {
    "cache_run_id": "cacheRunId",
    "stat_id": "statId",
    "chger_id": "chgerId",
    "stat_nm": "statNm",
    "chger_type": "chgerType",
    "addr": "addr",
    "addr_detail": "addrDetail",
    "location": "location",
    "lat": "lat",
    "lng": "lng",
    "use_time": "useTime",
    "busi_id": "busiId",
    "busi_nm": "busiNm",
    "busi_call": "busiCall",
    "output": "output",
    "method": "method",
    "zcode": "zcode",
    "zscode": "zscode",
    "kind": "kind",
    "kind_detail": "kindDetail",
    "parking_free": "parkingFree",
    "note": "note",
    "limit_yn": "limitYn",
    "limit_detail": "limitDetail",
    "stat": "stat",
    "stat_upd_dt": "statUpdDt",
    "district": "district",
    "neighborhood": "neighborhood",
}

DF_TO_DB_COLUMNS = {value: key for key, value in DB_TO_DF_COLUMNS.items()}
SNAPSHOT_DB_COLUMNS = [
    column for column in DB_TO_DF_COLUMNS if column != "cache_run_id"
]


class DatabaseConfigError(RuntimeError):
    """데이터베이스 설정이 없거나 잘못된 경우."""


class DatabaseError(RuntimeError):
    """데이터베이스 처리 중 발생한 오류."""


def _import_mysql_connector():
    try:
        import mysql.connector
    except ImportError as exc:
        raise DatabaseConfigError(
            "`mysql-connector-python`이 설치되어 있지 않습니다. requirements.txt를 설치해주세요."
        ) from exc

    return mysql.connector


def _load_db_config(env_path: Path) -> dict[str, Any]:
    load_dotenv(dotenv_path=env_path, override=False)

    database = os.getenv("MYSQL_DATABASE", "").strip()
    user = os.getenv("MYSQL_USER", "").strip()

    if not database or not user:
        raise DatabaseConfigError(
            "MySQL 설정이 없습니다. MYSQL_DATABASE와 MYSQL_USER를 설정해주세요."
        )

    return {
        "host": os.getenv("MYSQL_HOST", "localhost").strip() or "localhost",
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": user,
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": database,
        "charset": "utf8mb4",
        "autocommit": False,
    }


def get_connection(env_path: Path):
    mysql_connector = _import_mysql_connector()
    config = _load_db_config(env_path)
    return mysql_connector.connect(**config)


def _read_schema(schema_path: Path) -> list[str]:
    sql = schema_path.read_text(encoding="utf-8")
    return [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]


def init_db(project_root: Path) -> None:
    schema_path = project_root / "database" / "schema.sql"

    try:
        statements = _read_schema(schema_path)

        with get_connection(project_root / ".env") as connection:
            with connection.cursor(dictionary=True) as cursor:
                for statement in statements:
                    cursor.execute(statement)
                _ensure_api_cache_run_columns(cursor)
            connection.commit()
    except DatabaseConfigError:
        raise
    except Exception as exc:
        raise DatabaseError(f"MySQL 테이블 초기화에 실패했습니다: {exc}") from exc


def _ensure_api_cache_run_columns(cursor) -> None:
    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'api_cache_runs'
        """
    )
    existing_columns = {
        row["COLUMN_NAME"]
        for row in cursor.fetchall()
    }

    if "selected_district" not in existing_columns:
        cursor.execute(
            """
            ALTER TABLE api_cache_runs
            ADD COLUMN selected_district VARCHAR(100) NULL
            AFTER region_name
            """
        )

    if "selected_neighborhood" not in existing_columns:
        cursor.execute(
            """
            ALTER TABLE api_cache_runs
            ADD COLUMN selected_neighborhood VARCHAR(100) NULL
            AFTER selected_district
            """
        )


def load_valid_locale_search_cache(
    project_root: Path,
    region_code: str,
) -> tuple[pd.DataFrame, dict[str, str | None]] | None:
    query_cache_run = """
        SELECT id, selected_district, selected_neighborhood
        FROM api_cache_runs
        WHERE cache_type = %s
          AND region_code = %s
          AND expires_at > NOW()
        ORDER BY fetched_at DESC
        LIMIT 1
    """
    query_snapshots = f"""
        SELECT cache_run_id, {", ".join(SNAPSHOT_DB_COLUMNS)}
        FROM charger_snapshots
        WHERE cache_run_id = %s
        ORDER BY stat_nm, chger_id
    """

    try:
        with get_connection(project_root / ".env") as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    query_cache_run,
                    (LOCALE_SEARCH_CACHE_TYPE, region_code),
                )
                cache_run = cursor.fetchone()

                if not cache_run:
                    return None

                cursor.execute(query_snapshots, (cache_run["id"],))
                rows = cursor.fetchall()

        if not rows:
            return pd.DataFrame(), {
                "selected_district": cache_run.get("selected_district"),
                "selected_neighborhood": cache_run.get("selected_neighborhood"),
            }

        cached_df = pd.DataFrame(rows).rename(columns=DB_TO_DF_COLUMNS)

        for column in ["lat", "lng", "output"]:
            if column in cached_df.columns:
                cached_df[column] = pd.to_numeric(
                    cached_df[column],
                    errors="coerce",
                )

        return cached_df, {
            "selected_district": cache_run.get("selected_district"),
            "selected_neighborhood": cache_run.get("selected_neighborhood"),
        }
    except DatabaseConfigError:
        raise
    except Exception as exc:
        raise DatabaseError(f"MySQL 캐시 조회에 실패했습니다: {exc}") from exc


def save_locale_search_cache(
    project_root: Path,
    *,
    region_code: str,
    region_name: str,
    selected_district: str | None,
    selected_neighborhood: str | None,
    info_count: int,
    status_count: int,
    charger_data: pd.DataFrame,
) -> None:
    insert_cache_run = """
        INSERT INTO api_cache_runs (
            cache_type,
            region_code,
            region_name,
            selected_district,
            selected_neighborhood,
            fetched_at,
            expires_at,
            info_count,
            status_count,
            merged_count
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW(),
            DATE_ADD(NOW(), INTERVAL %s MINUTE),
            %s,
            %s,
            %s
        )
    """
    insert_snapshot = f"""
        INSERT INTO charger_snapshots (
            cache_run_id,
            {", ".join(SNAPSHOT_DB_COLUMNS)}
        )
        VALUES (
            %s,
            {", ".join(["%s"] * len(SNAPSHOT_DB_COLUMNS))}
        )
    """

    try:
        with get_connection(project_root / ".env") as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    insert_cache_run,
                    (
                        LOCALE_SEARCH_CACHE_TYPE,
                        region_code,
                        region_name,
                        selected_district,
                        selected_neighborhood,
                        CACHE_MINUTES,
                        info_count,
                        status_count,
                        len(charger_data),
                    ),
                )
                cache_run_id = cursor.lastrowid

                if not charger_data.empty:
                    records = _build_snapshot_records(
                        cache_run_id,
                        charger_data,
                    )
                    cursor.executemany(insert_snapshot, records)

            connection.commit()
    except DatabaseConfigError:
        raise
    except Exception as exc:
        raise DatabaseError(f"MySQL 캐시 저장에 실패했습니다: {exc}") from exc


def _build_snapshot_records(
    cache_run_id: int,
    charger_data: pd.DataFrame,
) -> list[tuple[Any, ...]]:
    records = []

    for _, row in charger_data.iterrows():
        values = [cache_run_id]

        for db_column in SNAPSHOT_DB_COLUMNS:
            df_column = DB_TO_DF_COLUMNS[db_column]
            value = row.get(df_column)

            if pd.isna(value):
                value = None

            values.append(value)

        records.append(tuple(values))

    return records
