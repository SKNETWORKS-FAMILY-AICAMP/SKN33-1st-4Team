"""FAQ 크롤링 결과를 DataFrame으로 변환하는 도우미."""

from __future__ import annotations

from typing import Any

import pandas as pd


def questions_to_dataframe(results: list[dict[str, Any]]) -> pd.DataFrame:
    """크롤링 결과 리스트를 pandas DataFrame으로 변환합니다."""
    question_df = pd.DataFrame(results)

    if question_df.empty or "published_at" not in question_df.columns:
        return question_df

    published_at = pd.to_datetime(
        question_df["published_at"],
        errors="coerce",
        utc=True,
    )
    return (
        question_df.assign(_published_at_sort=published_at)
        .sort_values(
            "_published_at_sort",
            ascending=False,
            na_position="last",
            kind="stable",
        )
        .drop(columns="_published_at_sort")
        .reset_index(drop=True)
    )


def build_display_dataframe(question_df: pd.DataFrame) -> pd.DataFrame:
    """Streamlit 화면에 보여줄 최소 컬럼만 가진 DataFrame을 만듭니다."""
    if question_df.empty:
        return pd.DataFrame(columns=["인덱스", "작성일", "제목", "링크"])

    return pd.DataFrame(
        {
            "인덱스": range(1, len(question_df) + 1),
            "작성일": question_df.get(
                "published_at",
                pd.Series("", index=question_df.index),
            ),
            "제목": question_df["title"],
            "링크": question_df["url"],
        }
    )
