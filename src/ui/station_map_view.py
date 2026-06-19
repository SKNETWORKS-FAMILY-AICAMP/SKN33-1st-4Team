from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_ROOT = PROJECT_ROOT / "locale"
if str(LOCALE_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCALE_ROOT))

from locale_service.charge_station_map import get_region_elec_usage_df
from locale_ui.station_map_ui import view_station_map


def render_station_map_view(project_root: Path) -> None:
    """Render station map and regional electricity usage from MySQL."""
    st.subheader("충전소 위치 지도")
    try:
        view_station_map()
    except Exception as exc:
        st.error(f"충전소 위치 지도를 불러오지 못했습니다: {exc}")

    st.divider()
    st.subheader("지역별 전기차 충전기 사용량")

    try:
        usage_df = get_region_elec_usage_df()
    except Exception as exc:
        st.error(f"지역별 사용량 데이터를 불러오지 못했습니다: {exc}")
        return

    if usage_df.empty:
        st.warning("tbl_region_elec_usage 테이블에 표시할 데이터가 없습니다.")
        return

    numeric_columns = [
        "kw_50",
        "kw_100",
        "kw_100_dual",
        "kw_200_dual",
        "kw_300_dual",
        "usage",
    ]
    for column in numeric_columns:
        usage_df[column] = pd.to_numeric(usage_df[column], errors="coerce").fillna(0)

    usage_by_sido = (
        usage_df.groupby("sido", as_index=False)["usage"]
        .sum()
        .sort_values("usage", ascending=False)
    )

    st.bar_chart(
        usage_by_sido,
        x="sido",
        y="usage",
        x_label="시/도",
        y_label="사용량(kWh)",
    )
    st.dataframe(
        usage_by_sido,
        width="stretch",
        hide_index=True,
        column_config={
            "usage": st.column_config.NumberColumn("총 사용량(kWh)", format="localized")
        },
    )

    _render_capacity_filter(usage_df)


def _render_capacity_filter(usage_df: pd.DataFrame) -> None:
    st.divider()
    st.subheader("충전 용량별 현황")

    capacity_columns = [
        "kw_50",
        "kw_100",
        "kw_100_dual",
        "kw_200_dual",
        "kw_300_dual",
    ]
    selected_columns = st.multiselect(
        "충전 용량",
        options=capacity_columns,
        default=capacity_columns[:2],
        format_func=lambda value: value.replace("_", " ").upper(),
    )

    if not selected_columns:
        st.info("표시할 충전 용량을 하나 이상 선택해주세요.")
        return

    display_columns = ["sido", "sigungu", *selected_columns, "usage"]
    st.caption(f"조회 데이터: {len(usage_df):,}건")
    st.dataframe(
        usage_df[display_columns],
        width="stretch",
        hide_index=True,
    )
