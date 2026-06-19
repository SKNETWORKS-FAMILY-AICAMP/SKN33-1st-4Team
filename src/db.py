from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


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
