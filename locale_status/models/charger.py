from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt

import pandas as pd

from locale_status.config.settings import (
    AVAILABLE_STATUS,
    REGION_CODES,
    REGION_NAME_ALIASES,
    STATUS_COLORS,
    STATUS_LABELS,
)


# 이 파일은 API에서 받은 충전소 데이터를 화면에 쓰기 좋게 가공합니다.
# 기본정보와 실시간 상태 병합, 상태 라벨 추가, 거리 계산 같은 순수 데이터 처리를 담당합니다.
def merge_charger_data(
    info_items: list[dict[str, str]],
    status_items: list[dict[str, str]],
) -> pd.DataFrame:
    """충전소 기본정보와 실시간 상태정보를 결합합니다."""
    # API 응답 dict 목록을 pandas DataFrame으로 바꿔 병합하기 쉽게 만듭니다.
    info_df = pd.DataFrame(info_items)
    status_df = pd.DataFrame(status_items)

    if info_df.empty or status_df.empty:
        return pd.DataFrame()

    # statId(충전소 ID)와 chgerId(충전기 ID)가 같아야 같은 충전기로 볼 수 있습니다.
    merge_keys = ["statId", "chgerId"]
    if any(key not in info_df.columns for key in merge_keys):
        return pd.DataFrame()
    if any(key not in status_df.columns for key in merge_keys):
        return pd.DataFrame()

    info_df = info_df.drop(
        columns=[
            column
            for column in ["stat", "statUpdDt"]
            if column in info_df.columns
        ]
    )
    # 상태 API에서는 화면에 필요한 상태값과 갱신시각만 가져와 중복을 줄입니다.
    status_columns = [
        column
        for column in ["statId", "chgerId", "stat", "statUpdDt"]
        if column in status_df.columns
    ]
    merged_df = info_df.merge(
        status_df[status_columns].drop_duplicates(merge_keys, keep="last"),
        on=merge_keys,
        how="inner",
        suffixes=("", "_status"),
    )

    # 숫자 계산이나 정렬이 필요한 컬럼은 문자열에서 숫자로 바꿉니다.
    if "output" in merged_df.columns:
        merged_df["output"] = pd.to_numeric(
            merged_df["output"],
            errors="coerce",
        )

    for column in ["lat", "lng"]:
        if column in merged_df.columns:
            merged_df[column] = pd.to_numeric(
                merged_df[column],
                errors="coerce",
            )

    return merged_df


def get_output_options(charger_df: pd.DataFrame) -> list[float]:
    # 필터 UI에서 쓸 충전용량 목록을 만듭니다.
    if charger_df.empty or "output" not in charger_df.columns:
        return []
    return sorted(charger_df["output"].dropna().unique().tolist())


def filter_available_chargers(
    charger_df: pd.DataFrame,
    selected_outputs: list[float],
) -> pd.DataFrame:
    # 사용 가능 상태(stat == 2)인 충전기만 남기고, 선택한 충전용량으로 한 번 더 좁힙니다.
    if charger_df.empty or "stat" not in charger_df.columns:
        return pd.DataFrame()

    filtered_df = charger_df[
        charger_df["stat"].astype(str) == AVAILABLE_STATUS
    ].copy()

    if "output" in filtered_df.columns and not selected_outputs:
        return filtered_df.iloc[0:0]

    if "output" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["output"].isin(selected_outputs)
        ]

    sort_columns = [
        column
        for column in ["statNm", "output", "chgerId"]
        if column in filtered_df.columns
    ]
    if sort_columns:
        filtered_df = filtered_df.sort_values(sort_columns)

    return filtered_df


def resolve_region_from_query(
    region_query: str,
    usage_df: pd.DataFrame,
    default_region: str,
) -> str | None:
    # 사용자가 짧게 입력한 지역명도 API 공식 지역명으로 찾아주는 보조 함수입니다.
    query = region_query.strip()

    if not query:
        return default_region

    for region_name in REGION_CODES:
        if query in region_name:
            return region_name

    for short_name, official_name in REGION_NAME_ALIASES.items():
        if query in short_name or query in official_name:
            return official_name

    required_columns = {"광역지자체", "시군구", "api_region"}
    if not usage_df.empty and required_columns.issubset(usage_df.columns):
        matched_rows = usage_df[
            usage_df["광역지자체"].astype(str).str.contains(query, case=False, na=False)
            | usage_df["시군구"].astype(str).str.contains(query, case=False, na=False)
        ]
        matched_regions = matched_rows["api_region"].dropna().unique().tolist()
        if matched_regions:
            return matched_regions[0]

    return None


def enrich_realtime_data(charger_df: pd.DataFrame) -> pd.DataFrame:
    # API 원본 데이터에 화면 표시용 컬럼을 추가합니다.
    # 예: stat "2" -> stat_label "충전 대기", status_color 초록색
    if charger_df.empty:
        return charger_df

    enriched_df = charger_df.copy()

    if "stat" in enriched_df.columns:
        enriched_df["stat"] = enriched_df["stat"].astype(str)
        enriched_df["stat_label"] = (
            enriched_df["stat"].map(STATUS_LABELS).fillna("기타")
        )
        enriched_df["status_color"] = enriched_df["stat"].map(
            lambda value: STATUS_COLORS.get(str(value), [100, 116, 139, 180])
        )

    if "output" in enriched_df.columns:
        enriched_df["output"] = pd.to_numeric(
            enriched_df["output"],
            errors="coerce",
        )

    for column in ["lat", "lng"]:
        if column in enriched_df.columns:
            enriched_df[column] = pd.to_numeric(
                enriched_df[column],
                errors="coerce",
            )

    return enriched_df


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    # 두 위도/경도 사이의 거리를 구하는 하버사인 공식입니다.
    earth_radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c


def add_distance(
    charger_df: pd.DataFrame,
    user_lat: float,
    user_lng: float,
) -> pd.DataFrame:
    # 사용자 현재 위치와 각 충전기 사이의 거리를 계산해 distance_km 컬럼으로 붙입니다.
    if charger_df.empty or not {"lat", "lng"}.issubset(charger_df.columns):
        return charger_df

    distance_df = charger_df.dropna(subset=["lat", "lng"]).copy()
    distance_df["distance_km"] = distance_df.apply(
        lambda row: calculate_distance_km(
            user_lat,
            user_lng,
            float(row["lat"]),
            float(row["lng"]),
        ),
        axis=1,
    )
    return distance_df.sort_values("distance_km")
