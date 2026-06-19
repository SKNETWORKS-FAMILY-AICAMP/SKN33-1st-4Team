from __future__ import annotations

from urllib.parse import unquote
from xml.etree import ElementTree

import requests

from locale_status.config.settings import ChargerApiSettings


CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 120
API_RETRY_COUNT = 2


# 이 파일은 공공데이터포털 전기차 충전소 API와 통신하는 역할만 담당합니다.
# 화면이나 데이터 가공 로직은 다른 모듈에서 처리하고, 여기서는 XML 응답을
# 파이썬 딕셔너리 목록으로 바꿔 반환합니다.
class ChargerAPIError(RuntimeError):
    """충전소 API 오류를 나타냅니다."""


def _request_items(
    api_settings: ChargerApiSettings,
    endpoint: str,
    zcode: str,
    *,
    period: int | None = None,
) -> list[dict[str, str]]:
    # 두 API(getChargerInfo, getChargerStatus)가 공통으로 쓰는 요청 파라미터입니다.
    # ServiceKey는 인코딩된 키가 들어올 수 있어 unquote로 한 번 풀어줍니다.
    params: dict[str, str | int] = {
        "ServiceKey": unquote(api_settings.service_key),
        "pageNo": 1,
        "numOfRows": 100,
        "zcode": zcode,
    }
    if period is not None:
        params["period"] = period

    for attempt in range(1, API_RETRY_COUNT + 1):
        try:
            # endpoint만 바꿔 충전소 기본정보와 실시간 상태정보 API를 모두 호출합니다.
            response = requests.get(
                f"{api_settings.base_url}/{endpoint}",
                params=params,
                timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
            )
            response.raise_for_status()
            break
        except requests.Timeout as exc:
            if attempt == API_RETRY_COUNT:
                raise ChargerAPIError(
                    "공공데이터 API 서버 응답이 지연되어 요청 시간이 초과되었습니다. "
                    "다른 광역 지역으로 조회하거나 잠시 후 다시 시도해주세요."
                ) from exc
        except requests.RequestException as exc:
            if attempt == API_RETRY_COUNT:
                raise ChargerAPIError(f"API 요청에 실패했습니다: {exc}") from exc

    try:
        # 공공데이터 API 응답은 XML이므로 ElementTree로 파싱합니다.
        root = ElementTree.fromstring(response.content)
    except ElementTree.ParseError as exc:
        raise ChargerAPIError("API 응답을 XML로 해석할 수 없습니다.") from exc

    # resultCode가 00이 아니면 API 쪽 오류로 보고 화면에 보여줄 예외를 발생시킵니다.
    result_code = root.findtext(".//resultCode")
    result_message = root.findtext(".//resultMsg", default="알 수 없는 오류")
    if result_code and result_code != "00":
        raise ChargerAPIError(f"API 오류 {result_code}: {result_message}")

    # <item> 태그 하나가 충전기/충전소 한 건입니다.
    # 각 하위 태그 이름을 key로, 텍스트 값을 value로 가진 dict로 변환합니다.
    return [
        {child.tag: (child.text or "").strip() for child in item}
        for item in root.findall(".//item")
    ]


def get_charger_info(
    api_settings: ChargerApiSettings,
    zcode: str,
) -> list[dict[str, str]]:
    # 충전소명, 주소, 위도/경도, 충전용량 같은 정적인 기본정보를 가져옵니다.
    return _request_items(api_settings, "getChargerInfo", zcode)


def get_charger_status(
    api_settings: ChargerApiSettings,
    zcode: str,
    period: int = 10,
) -> list[dict[str, str]]:
    # 현재 충전 가능/충전 중/점검 중 같은 실시간 상태정보를 가져옵니다.
    return _request_items(
        api_settings,
        "getChargerStatus",
        zcode,
        period=period,
    )
