"""FAQ 검색 페이지."""

from __future__ import annotations

import streamlit as st

from faq_crawling.base_crawler import CrawlerError
from faq_crawling.constants import DEFAULT_DETAIL_LIMIT, SEARCH_KEYWORDS
from faq_crawling.crawler_runner import (
    crawl_evdang_questions,
    crawl_evlounge_questions,
    crawl_ppomppu_questions,
)
from faq_crawling.dataframe_helper import build_display_dataframe


CRAWLER_OPTIONS = {
    "EVDang": crawl_evdang_questions,
    "EV 라운지": crawl_evlounge_questions,
    "뽐뿌 자동차포럼": crawl_ppomppu_questions,
}


def render_faq_search_page() -> None:
    """FAQ검색 화면을 렌더링한다."""
    st.title("FAQ검색")

    selected_source = st.selectbox(
        "크롤링 대상",
        options=list(CRAWLER_OPTIONS),
    )
    selected_keyword = st.selectbox(
        "검색 키워드",
        options=SEARCH_KEYWORDS,
        index=SEARCH_KEYWORDS.index("테슬라") if "테슬라" in SEARCH_KEYWORDS else 0,
    )

    detail_limit = st.number_input(
        "수집할 상세 게시글 수",
        min_value=1,
        max_value=30,
        value=min(DEFAULT_DETAIL_LIMIT, 10),
        step=1,
    )

    if st.button("FAQ 크롤링 실행", type="primary"):
        try:
            with st.spinner(f"{selected_source} 게시글을 수집하고 있습니다."):
                question_df = CRAWLER_OPTIONS[selected_source](
                    selected_keyword,
                    detail_limit=int(detail_limit),
                )

            st.session_state["faq_question_df"] = question_df

        except CrawlerError as exc:
            st.error(str(exc))

    question_df = st.session_state.get("faq_question_df")

    if question_df is None:
        return

    if question_df.empty:
        st.info("수집된 FAQ 후보 게시글이 없습니다.")
        return

    st.metric("수집 결과", f"{len(question_df):,}건")

    display_df = build_display_dataframe(question_df)

    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch",
        column_config={
            "링크": st.column_config.LinkColumn(
                "링크",
                display_text="링크 이동",
            ),
        },
    )
