from __future__ import annotations

import pandas as pd

from .constants import AVAILABLE_STATUS


# 기본정보와 상태정보를 결합
def merge_charger_data(
    info_items: list[dict[str, str]],
    status_items: list[dict[str, str]],
) -> pd.DataFrame:
    # 기본정보를 표 형태로 변환
    info_df = pd.DataFrame(info_items)
    # 상태정보를 표 형태로 변환
    status_df = pd.DataFrame(status_items)

    # 어느 한쪽이 비면 빈 표 반환
    if info_df.empty or status_df.empty:
        return pd.DataFrame()

    # 충전기를 식별할 공통 열
    merge_keys = ["statId", "chgerId"]
    # 기본정보에 식별 열이 있는지 확인
    if any(key not in info_df.columns for key in merge_keys):
        return pd.DataFrame()
    # 상태정보에 식별 열이 있는지 확인
    if any(key not in status_df.columns for key in merge_keys):
        return pd.DataFrame()

    # 오래된 상태 열은 기본정보에서 제거
    info_df = info_df.drop(
        columns=[
            column
            for column in ["stat", "statUpdDt"]
            if column in info_df.columns
        ]
    )
    # 상태정보에서 필요한 열만 선택
    status_columns = [
        column
        for column in ["statId", "chgerId", "stat", "statUpdDt"]
        if column in status_df.columns
    ]
    # 충전소와 충전기 번호로 결합
    merged_df = info_df.merge(
        # 같은 충전기는 최신 항목만 유지
        status_df[status_columns].drop_duplicates(merge_keys, keep="last"),
        on=merge_keys,
        how="inner",
        suffixes=("", "_status"),
    )

    # 충전용량을 숫자형으로 변환
    if "output" in merged_df.columns:
        merged_df["output"] = pd.to_numeric(
            merged_df["output"],
            errors="coerce",
        )

    # 지도 좌표 열을 차례대로 확인
    for column in ["lat", "lng"]:
        # 좌표 열이 있을 때 숫자로 변환
        if column in merged_df.columns:
            merged_df[column] = pd.to_numeric(
                merged_df[column],
                errors="coerce",
            )

    # 전처리가 끝난 표 반환
    return merged_df


# 충전용량 선택 항목 생성
def get_output_options(charger_df: pd.DataFrame) -> list[float]:
    # 데이터나 용량 열이 없으면 빈 목록
    if charger_df.empty or "output" not in charger_df.columns:
        return []

    # 중복과 빈 값을 빼고 정렬
    return sorted(charger_df["output"].dropna().unique().tolist())


# 사용 가능한 충전기만 필터링
def filter_available_chargers(
    charger_df: pd.DataFrame,
    selected_outputs: list[float],
) -> pd.DataFrame:
    # 상태 열이 없으면 빈 표 반환
    if charger_df.empty or "stat" not in charger_df.columns:
        return pd.DataFrame()

    # 충전 대기 상태만 남김
    filtered_df = charger_df[
        charger_df["stat"].astype(str) == AVAILABLE_STATUS
    ].copy()

    # 선택 용량이 없으면 빈 결과
    if "output" in filtered_df.columns and not selected_outputs:
        return filtered_df.iloc[0:0]

    # 선택한 충전용량만 남김
    if "output" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["output"].isin(selected_outputs)
        ]

    # 화면 표시용 정렬 열 선택
    sort_columns = [
        column
        for column in ["statNm", "output", "chgerId"]
        if column in filtered_df.columns
    ]
    # 사용 가능한 열을 기준으로 정렬
    if sort_columns:
        filtered_df = filtered_df.sort_values(sort_columns)

    # 필터링된 결과를 반환
    return filtered_df
