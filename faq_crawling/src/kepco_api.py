"""한전 빅데이터 전기차 충전소 API 요청 함수."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv


# 한전 빅데이터 전기차 충전소 API 주소
KEPCO_EV_CHARGE_URL = "https://bigdata.kepco.co.kr/openapi/v1/EVcharge.do"


class KepcoAPIError(RuntimeError):
    """한전 빅데이터 API 처리 중 발생한 오류."""


def load_kepco_api_key(env_path: Path) -> str:
    """환경변수 또는 .env 파일에서 한전 API 키를 읽는다."""
    load_dotenv(dotenv_path=env_path, override=False)
    return os.getenv("KEPCO_API_KEY", "").strip()


def get_kepco_ev_charge_data(
    *,
    api_key: str,
    metro_cd: str,
    city_cd: str,
) -> list[dict[str, Any]]:
    """한전 전기차 충전소 데이터를 JSON으로 요청한다.

    반환 데이터에는 충전소명, 주소, 급속/완속 충전기 수, 지원 차종(carType)
    등이 포함된다.
    """
    params = {
        "metroCd": metro_cd,
        "cityCd": city_cd,
        "apiKey": api_key,
        "returnType": "json",
    }

    try:
        response = requests.get(
            KEPCO_EV_CHARGE_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise KepcoAPIError(f"한전 API 요청에 실패했습니다: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise KepcoAPIError("한전 API 응답을 JSON으로 해석할 수 없습니다.") from exc

    data = payload.get("data", [])

    if not isinstance(data, list):
        raise KepcoAPIError("한전 API 응답의 data 형식이 올바르지 않습니다.")

    return data


def kepco_items_to_dataframe(items: list[dict[str, Any]]) -> pd.DataFrame:
    """한전 API 응답 목록을 DataFrame으로 변환하고 carType을 리스트로 분리한다."""
    df = pd.DataFrame(items)

    if df.empty:
        return df

    for column in ["rapidCnt", "slowCnt"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

    if {"rapidCnt", "slowCnt"}.issubset(df.columns):
        df["totalCnt"] = df["rapidCnt"] + df["slowCnt"]

    if "carType" in df.columns:
        df["carTypeList"] = df["carType"].fillna("").apply(_split_car_type)

    return df


def _split_car_type(value: str) -> list[str]:
    """쉼표로 연결된 지원 차종 문자열을 리스트로 변환한다."""
    return [
        car_type.strip()
        for car_type in str(value).split(",")
        if car_type.strip()
    ]
