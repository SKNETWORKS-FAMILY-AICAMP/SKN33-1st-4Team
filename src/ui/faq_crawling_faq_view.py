from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from faq_crawling.base_crawler import CrawlerError
from faq_crawling.constants import (
    DEFAULT_DETAIL_LIMIT,
    DEFAULT_PAGE_LIMIT,
    EV_KEYWORDS,
    SEARCH_KEYWORDS,
)
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


def filter_ev_questions(question_df: pd.DataFrame) -> pd.DataFrame:
    """제목 또는 본문에 전기차 관련 키워드가 포함된 글만 남깁니다."""
    if question_df.empty:
        return question_df

    keyword_pattern = "|".join(re.escape(keyword) for keyword in EV_KEYWORDS)
    title_series = (
        question_df["title"].fillna("")
        if "title" in question_df.columns
        else pd.Series("", index=question_df.index)
    )
    content_series = (
        question_df["content"].fillna("")
        if "content" in question_df.columns
        else pd.Series("", index=question_df.index)
    )
    text_series = title_series + " " + content_series

    filtered_df = question_df[
        text_series.str.contains(keyword_pattern, case=False, regex=True)
    ]

    return filtered_df.reset_index(drop=True)


def render_faq_crawling_faq_view() -> None:
    """FAQ 후보 게시글 검색 화면."""
    st.header("FAQ 검색")
    st.caption(
        "EVDang, EV 라운지, 뽐뿌 자동차포럼에서 전기차 관련 검색어로 게시글을 "
        "수집하고 FAQ 후보 질문 데이터로 확인합니다."
    )

    selected_source = st.selectbox(
        "크롤링 대상",
        options=list(CRAWLER_OPTIONS),
    )
    selected_keyword = st.selectbox(
        "검색 키워드",
        options=SEARCH_KEYWORDS,
        index=SEARCH_KEYWORDS.index("테슬라") if "테슬라" in SEARCH_KEYWORDS else 0,
    )

    option_columns = st.columns(2)
    with option_columns[0]:
        page_limit = st.number_input(
            "검색 페이지 수",
            min_value=1,
            max_value=5,
            value=DEFAULT_PAGE_LIMIT,
            step=1,
        )
    with option_columns[1]:
        detail_limit = st.number_input(
            "상세 게시글 최대 수",
            min_value=1,
            max_value=50,
            value=min(DEFAULT_DETAIL_LIMIT, 10),
            step=1,
        )

    if st.button("FAQ 크롤링 실행", type="primary"):
        try:
            with st.spinner(f"{selected_source} 게시글을 수집하고 있습니다."):
                question_df = CRAWLER_OPTIONS[selected_source](
                    selected_keyword,
                    page_limit=int(page_limit),
                    detail_limit=int(detail_limit),
                )
                if not question_df.empty:
                    question_df = filter_ev_questions(question_df)
                    if "url" in question_df.columns:
                        question_df = question_df.drop_duplicates(
                            subset=["url"],
                            keep="first",
                        ).reset_index(drop=True)

            st.session_state["faq_question_df"] = question_df
            st.session_state["faq_selected_source"] = selected_source
            st.session_state["faq_selected_keyword"] = selected_keyword
            st.success(f"{len(question_df):,}건을 수집했습니다.")
        except CrawlerError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"크롤링 중 오류가 발생했습니다: {exc}")

    question_df = st.session_state.get("faq_question_df")
    selected_result_source = st.session_state.get("faq_selected_source")
    selected_result_keyword = st.session_state.get("faq_selected_keyword")

    if question_df is None:
        return

    st.divider()
    st.subheader("수집 결과")
    if selected_result_source and selected_result_keyword:
        st.caption(
            f"수집 사이트: {selected_result_source} / 검색어: {selected_result_keyword}"
        )

    if question_df.empty:
        st.info("수집된 FAQ 후보 게시글이 없습니다.")
        return

    st.metric("수집 결과", f"{len(question_df):,}건")
    st.dataframe(
        build_display_dataframe(question_df),
        hide_index=True,
        width="stretch",
        column_config={
            "링크": st.column_config.LinkColumn("링크", display_text="링크 이동"),
        },
    )

    with st.expander("원본 데이터 보기"):
        st.dataframe(
            question_df,
            hide_index=True,
            width="stretch",
        )

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    safe_source_name = str(selected_result_source or selected_source).replace(" ", "_")
    safe_keyword = str(selected_result_keyword or selected_keyword).replace(" ", "_")
    csv_path = data_dir / f"ev_user_questions_{safe_source_name}_{safe_keyword}.csv"

    question_df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig",
    )
    st.success(f"CSV 파일로 저장했습니다: {csv_path}")

    csv_bytes = question_df.to_csv(index=False, encoding="utf-8-sig").encode(
        "utf-8-sig"
    )
    st.download_button(
        "CSV 다운로드",
        data=csv_bytes,
        file_name=csv_path.name,
        mime="text/csv",
    )
