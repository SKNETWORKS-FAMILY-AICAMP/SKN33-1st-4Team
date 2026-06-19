from __future__ import annotations

import os

import mysql.connector
from dotenv import load_dotenv

from config.settings import DatabaseSettings


def _env_value(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def get_connection(db_settings=DatabaseSettings):
    load_dotenv()

    return mysql.connector.connect(
        host=_env_value("DB_HOST", "MYSQL_HOST", default="localhost"),
        port=int(_env_value("DB_PORT", "MYSQL_PORT", default="3306")),
        user=_env_value("DB_USER", "MYSQL_USER"),
        password=_env_value("DB_PASSWORD", "MYSQL_PASSWORD", default=""),
        database=_env_value("DB_DATABASE", "MYSQL_DATABASE"),
        charset="utf8mb4",
    )
