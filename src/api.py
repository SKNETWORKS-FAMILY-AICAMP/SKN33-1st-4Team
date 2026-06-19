from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

import requests
from dotenv import load_dotenv

from .constants import (
    API_BASE_URL,
    API_CONNECT_TIMEOUT,
    API_NUM_OF_ROWS,
    API_READ_TIMEOUT,
    API_STATUS_PERIOD,
)


# API 오류를 구분하는 예외
class ChargerAPIError(RuntimeError):
    """충전소 API 오류를 나타냅니다."""


_SESSION = requests.Session()


# 환경변수나 파일에서 키 조회
def load_api_key(env_path: Path) -> str:
    # 기존 환경변수를 덮어쓰지 않고 .env 값을 불러옴
    load_dotenv(dotenv_path=env_path, override=False)
    return os.getenv("EV_CHARGER_API_KEY", "").strip()


# API를 호출해 항목 목록 생성
def _request_items(
    endpoint: str,
    api_key: str,
    zcode: str,
    *,
    period: int | None = None,
) -> list[dict[str, str]]:
    # API 요청에 필요한 값 구성
    params: dict[str, str | int] = {
        # 인증키의 인코딩을 한 번 해제
        "serviceKey": unquote(api_key),
        # 첫 번째 페이지를 요청
        "pageNo": 1,
        # 한 번에 받을 최대 건수
        "numOfRows": API_NUM_OF_ROWS,
        # 선택한 지역 코드를 전달
        "zcode": zcode,
    }
    # 상태 조회에만 갱신 범위 추가
    if period is not None:
        params["period"] = period

    # 네트워크 오류를 처리하며 요청
    try:
        # 지정한 API 주소로 요청 전송
        response = _SESSION.get(
            f"{API_BASE_URL}/{endpoint}",
            params=params,
            timeout=(API_CONNECT_TIMEOUT, API_READ_TIMEOUT),
        )
        # HTTP 오류가 있으면 예외 발생
        response.raise_for_status()
    # 요청 관련 오류를 한곳에서 처리
    except requests.RequestException as exc:
        raise ChargerAPIError(f"API 요청에 실패했습니다: {exc}") from exc

    # XML 응답을 읽을 수 있게 변환
    try:
        root = ElementTree.fromstring(response.content)
    # 잘못된 XML 응답을 처리
    except ElementTree.ParseError as exc:
        raise ChargerAPIError("API 응답을 XML로 해석할 수 없습니다.") from exc

    # API 처리 결과 코드를 확인
    result_code = root.findtext(".//resultCode")
    # API 결과 메시지를 확인
    result_message = root.findtext(".//resultMsg", default="알 수 없는 오류")
    # 성공 코드가 아니면 오류 표시
    if result_code and result_code != "00":
        raise ChargerAPIError(f"API 오류 {result_code}: {result_message}")

    # 변환된 항목을 담을 목록
    items: list[dict[str, str]] = []
    # XML의 각 충전기 항목 반복
    for item in root.findall(".//item"):
        # XML 자식 값을 딕셔너리화
        items.append({
            child.tag: (child.text or "").strip()
            for child in item
        })

    # 완성된 충전기 목록 반환
    return items


# 충전소 기본정보 API 호출
def get_charger_info(api_key: str, zcode: str) -> list[dict[str, str]]:
    return _request_items("getChargerInfo", api_key, zcode)


# 충전기 실시간 상태 API 호출
def get_charger_status(
    api_key: str,
    zcode: str,
    period: int = API_STATUS_PERIOD,
) -> list[dict[str, str]]:
    # 최근 갱신 범위를 포함해 요청
    return _request_items(
        "getChargerStatus",
        api_key,
        zcode,
        period=period,
    )
