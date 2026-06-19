from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from urllib.parse import unquote
from xml.etree import ElementTree

import requests

from src.constants import API_BASE_URL


class EvChargerAPIError(RuntimeError):
    """Raised when the EV charger OpenAPI request or response is invalid."""


@dataclass(frozen=True)
class PageResult:
    items: list[dict[str, str]]
    total_count: int
    page_no: int
    num_of_rows: int


class EvChargerClient:
    """Small XML client for the Korea Environment Corporation EV charger API."""

    def __init__(self, api_key: str, *, timeout: int = 30) -> None:
        if not api_key.strip():
            raise EvChargerAPIError("EV_CHARGER_API_KEY is empty.")

        self.api_key = unquote(api_key.strip())
        self.timeout = timeout

    def fetch_page(
        self,
        endpoint: str,
        *,
        page_no: int = 1,
        num_of_rows: int = 9999,
        zcode: str | None = None,
        period: int | None = None,
    ) -> PageResult:
        params: dict[str, str | int] = {
            "ServiceKey": self.api_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
        }
        if zcode:
            params["zcode"] = zcode
        if period is not None:
            params["period"] = period

        try:
            response = requests.get(
                f"{API_BASE_URL}/{endpoint}",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            # requests 예외에는 ServiceKey가 포함된 전체 URL이 들어갈 수 있으므로
            # 사용자에게 보여줄 메시지에는 엔드포인트와 예외 타입만 남깁니다.
            raise EvChargerAPIError(
                f"API request failed for {endpoint}: {type(exc).__name__}"
            ) from exc

        return _parse_page(response.content, page_no, num_of_rows)

    def fetch_all(
        self,
        endpoint: str,
        *,
        num_of_rows: int = 9999,
        zcode: str | None = None,
        period: int | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, str]]:
        """엔드포인트의 모든 페이지를 조회합니다.

        max_pages는 개발 중 API 키와 파서만 빠르게 확인할 때 사용합니다.
        실제 전체 수집에서는 None으로 두면 totalCount 기준 전체 페이지를 가져옵니다.
        """
        first_page = self.fetch_page(
            endpoint,
            page_no=1,
            num_of_rows=num_of_rows,
            zcode=zcode,
            period=period,
        )
        items = list(first_page.items)
        page_count = max(1, ceil(first_page.total_count / num_of_rows))
        if max_pages is not None:
            page_count = min(page_count, max_pages)

        for page_no in range(2, page_count + 1):
            page = self.fetch_page(
                endpoint,
                page_no=page_no,
                num_of_rows=num_of_rows,
                zcode=zcode,
                period=period,
            )
            items.extend(page.items)

        return items


def _parse_page(
    content: bytes,
    page_no: int,
    num_of_rows: int,
) -> PageResult:
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as exc:
        raise EvChargerAPIError("API response is not valid XML.") from exc

    result_code = root.findtext(".//resultCode")
    result_message = root.findtext(".//resultMsg", default="Unknown API error")
    if result_code and result_code != "00":
        raise EvChargerAPIError(f"API error {result_code}: {result_message}")

    total_count = _to_int(root.findtext(".//totalCount"), default=0)
    items = [
        {child.tag: (child.text or "").strip() for child in item}
        for item in root.findall(".//item")
    ]

    return PageResult(
        items=items,
        total_count=total_count,
        page_no=page_no,
        num_of_rows=num_of_rows,
    )


def _to_int(value: str | None, *, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
