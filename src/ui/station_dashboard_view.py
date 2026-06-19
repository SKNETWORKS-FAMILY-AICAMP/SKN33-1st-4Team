from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.ui.station_map_view import render_station_map_view
from src.ui.station_region_view import render_station_region_view


def render_station_dashboard_view(project_root: Path) -> None:
    """전체 충전소 지도와 지역구별 조회 화면을 탭으로 구성합니다."""
    st.header("충전소 지도 및 상세")

    map_tab, region_tab = st.tabs(
        [
            "전체 충전소 지도",
            "지역구별 충전소 조회",
        ]
    )

    with map_tab:
        render_station_map_view(project_root)

    with region_tab:
        render_station_region_view()
