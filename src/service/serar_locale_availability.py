from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.constants import AVAILABLE_STATUS
from src.db import get_connection
from src.queries.serar_locale_queries import (
    AVAILABLE_CHARGERS_BASE_QUERY,
    AVAILABLE_CHARGERS_ORDER_BY,
)


def load_available_chargers(
    project_root: Path,
    *,
    zcode: str | None = None,
    station_keyword: str | None = None,
    charger_type: str | None = None,
) -> pd.DataFrame:
    """MySQL에서 현재 사용 가능한 충전기 목록을 조회합니다.

    Streamlit 화면은 API나 CSV를 직접 보지 않고 이 함수만 호출하면 됩니다.
    이 함수는 주제 2의 핵심 질문인 "지금 사용할 수 있는 충전기는 무엇인가?"에 맞춰
    최신 상태 로그 기준 사용 가능 충전기만 반환합니다.
    """
    query, params = _build_available_chargers_query(
        zcode=zcode,
        station_keyword=station_keyword,
        charger_type=charger_type,
    )

    with get_connection(project_root / ".env") as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return _normalize_available_chargers(rows)


def _build_available_chargers_query(
    *,
    zcode: str | None,
    station_keyword: str | None,
    charger_type: str | None,
) -> tuple[str, list[Any]]:
    """선택 필터를 SQL WHERE 조건과 파라미터로 변환합니다."""
    query_parts = [AVAILABLE_CHARGERS_BASE_QUERY]
    params: list[Any] = [AVAILABLE_STATUS]

    if zcode:
        query_parts.append("AND s.zcode = %s")
        params.append(zcode)

    if station_keyword:
        query_parts.append("AND s.stat_nm LIKE %s")
        params.append(f"%{station_keyword}%")

    if charger_type:
        query_parts.append("AND c.chger_type = %s")
        params.append(charger_type)

    query_parts.append(AVAILABLE_CHARGERS_ORDER_BY)
    return "\n".join(query_parts), params


def _normalize_available_chargers(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """DB 조회 결과를 Streamlit에서 바로 쓰기 좋은 DataFrame으로 정리합니다."""
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # 숫자형 컬럼은 정렬과 그래프 처리를 위해 변환합니다.
    for column in ["lat", "lng", "output"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # 화면에서 사용할 요약 주소를 미리 만들어 UI 코드 중복을 줄입니다.
    if "addr" in df.columns and "addr_detail" in df.columns:
        df["display_addr"] = (
            df["addr"].fillna("")
            + " "
            + df["addr_detail"].fillna("")
        ).str.strip()

    return df
