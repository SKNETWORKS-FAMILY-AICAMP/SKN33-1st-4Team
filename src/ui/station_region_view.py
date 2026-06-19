from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_ROOT = PROJECT_ROOT / "locale"
if str(LOCALE_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCALE_ROOT))

from locale_ui.station_map_ui import view_station_by_region


def render_station_region_view() -> None:
    """지역구 선택에 따른 충전소 지도와 상세 화면을 렌더링합니다."""
    try:
        view_station_by_region()
    except Exception as exc:
        st.error(f"지역구별 충전소 정보를 불러오지 못했습니다: {exc}")
