from __future__ import annotations

from pathlib import Path

import streamlit as st

from locale_status.ui.dashboard_page import (
    load_usage_data,
    render_realtime_dashboard,
)
from src.constants import AVAILABLE_STATUS_LABEL, REGION_CODES
from src.db import DatabaseConfigError, DatabaseError
from src.service.serar_locale_availability import load_available_chargers


def render_serar_locale_available_view(project_root: Path) -> None:
    """DB 기반 사용 가능 충전기와 충전기 상태 화면을 렌더링합니다."""
    st.header("충전기 현황")

    available_tab, status_tab = st.tabs(
        ["DB 저장 현황", "충전기 상태 조회"]
    )

    with available_tab:
        _render_database_available_view(project_root)

    with status_tab:
        usage_df = load_usage_data()
        render_realtime_dashboard(usage_df)


def _render_database_available_view(project_root: Path) -> None:
    """MySQL 최신 상태 기준으로 현재 사용 가능한 충전기를 조회합니다."""
    st.subheader("저장 데이터 기반 사용 가능 충전기")

    selected_region_name = st.selectbox(
        "지역",
        ["전체", *REGION_CODES.keys()],
        help="OpenAPI 시도 코드 기준으로 저장된 MySQL 데이터를 필터링합니다.",
    )
    zcode = None if selected_region_name == "전체" else REGION_CODES[selected_region_name]

    station_keyword = st.text_input(
        "충전소명 검색",
        placeholder="예: 시청, 공영주차장",
    ).strip()

    charger_type = st.text_input(
        "충전기 타입 코드",
        placeholder="비워두면 전체 조회",
        help="API의 chgerType 원본 코드 기준입니다.",
    ).strip()

    if st.button("조회", type="primary"):
        _render_available_result(
            project_root=project_root,
            zcode=zcode,
            station_keyword=station_keyword or None,
            charger_type=charger_type or None,
        )


def _render_available_result(
    *,
    project_root: Path,
    zcode: str | None,
    station_keyword: str | None,
    charger_type: str | None,
) -> None:
    """조회 버튼 클릭 후 결과 테이블과 요약 지표를 표시합니다."""
    try:
        available_df = load_available_chargers(
            project_root,
            zcode=zcode,
            station_keyword=station_keyword,
            charger_type=charger_type,
        )
    except DatabaseConfigError as exc:
        st.error(str(exc))
        st.info(".env 파일의 MySQL 설정을 먼저 확인해주세요.")
        return
    except DatabaseError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"사용 가능 충전기 조회 중 예상하지 못한 오류가 발생했습니다: {exc}")
        return

    if available_df.empty:
        st.warning("조건에 맞는 사용 가능 충전기가 없습니다.")
        return

    station_count = available_df["stat_id"].nunique() if "stat_id" in available_df else 0
    charger_count = len(available_df)

    metric_left, metric_right = st.columns(2)
    metric_left.metric("사용 가능 충전기", f"{charger_count:,}대")
    metric_right.metric("충전소 수", f"{station_count:,}곳")

    st.caption(f"상태 기준: {AVAILABLE_STATUS_LABEL}")
    st.dataframe(
        _select_display_columns(available_df),
        width="stretch",
        hide_index=True,
    )


def _select_display_columns(df):
    """화면에 보여줄 컬럼만 고르고, 없는 컬럼은 자동으로 제외합니다."""
    display_columns = [
        "stat_nm",
        "display_addr",
        "chger_id",
        "chger_type",
        "output",
        "method",
        "stat",
        "stat_upd_dt",
        "fetched_at",
        "busi_nm",
        "busi_call",
    ]
    return df[[column for column in display_columns if column in df.columns]]
