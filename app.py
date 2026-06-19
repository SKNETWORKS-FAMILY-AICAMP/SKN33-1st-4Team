from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from locale_status.ui.dashboard_page import render_search_locale_dashboard
from locale_status.ui.layout import apply_naver_style, render_app_header
from src.config import get_project_root
from src.ui.faq_crawling_faq_view import render_faq_crawling_faq_view
from src.ui.serar_locale_available_view import render_serar_locale_available_view
from src.ui.station_dashboard_view import render_station_dashboard_view


def render_search_page() -> None:
    render_app_header()
    render_search_locale_dashboard()


def render_dashboard_page() -> None:
    render_app_header()
    project_root = get_project_root()
    render_station_dashboard_view(project_root)


def render_available_page() -> None:
    render_app_header()
    project_root = get_project_root()
    render_serar_locale_available_view(project_root)


def render_faq_page() -> None:
    render_app_header()
    render_faq_crawling_faq_view()


def main() -> None:
    st.set_page_config(
        page_title="전기차 충전소 실시간 플랫폼",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_naver_style()

    search_page = st.Page(
        render_search_page,
        title="사용량 분석",
        icon="📊",
        default=True,
    )

    dashboard_page = st.Page(
        render_dashboard_page,
        title="충전소 지도 및 상세",
        icon="🗺️",
    )

    available_page = st.Page(
        render_available_page,
        title="충전기 현황",
        icon="⚡",
    )

    faq_page = st.Page(
        render_faq_page,
        title="FAQ 검색",
        icon="❓",
    )

    navigation = st.navigation(
        [search_page, dashboard_page, available_page, faq_page],
        position="sidebar",
    )

    navigation.run()


if __name__ == "__main__":
    main()
