"""EVDang 게시글 검색 크롤러."""

from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse, urlencode

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .constants import EVDANG_ARTICLES_URL, EVDANG_BASE_URL


EVDANG_ARTICLE_PATH_PATTERN = re.compile(r"/articles/\d+")


class EVDangCrawler(BaseCrawler):
    """EVDang 검색 결과에서 전기차 사용자 질문 후보를 수집하는 크롤러.

    현재 단계에서는 검색 결과 목록에서 게시글 상세 URL만 추출합니다.
    제목, 본문, 작성일 같은 상세 페이지 파싱은 다음 단계에서 구현합니다.
    """

    source_name = "EVDang"
    category = "전체 게시판"
    first_page = 1

    def build_search_params(self, keyword: str, page: int = 1) -> dict[str, str | int]:
        """EVDang 검색 요청에 사용할 쿼리 파라미터를 만듭니다."""
        params: dict[str, str | int] = {
            "board": "all",
            "category": "",
            "board_category": "1",
            "q[title_or_body_or_comments_body_or_user_nick_name_cont]": keyword,
        }

        # EVDang 검색 페이지는 첫 페이지에는 page 파라미터가 없어도 됩니다.
        if page > 1:
            params["page"] = page

        return params

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """검색 URL을 사람이 확인할 수 있는 문자열로 생성합니다."""
        return (
            f"{EVDANG_ARTICLES_URL}?"
            f"{urlencode(self.build_search_params(keyword, page=page))}"
        )

    def crawl_list(self, keyword: str, page: int = 1) -> list[str]:
        """검색 결과 페이지에서 게시글 상세 URL 목록을 수집합니다."""
        response = self.safe_get(
            EVDANG_ARTICLES_URL,
            params=self.build_search_params(keyword, page=page),
        )
        soup = BeautifulSoup(response.text, "html.parser")

        detail_urls: list[str] = []

        # href 속성에 상세 글 URL이 들어간 경우를 수집합니다.
        for link in soup.select("a[href]"):
            detail_urls.extend(
                self._extract_article_urls(link.get("href", ""))
            )

        # EVDang 목록 행은 onclick="location.href='...'" 형태도 사용합니다.
        for element in soup.select("[onclick]"):
            detail_urls.extend(
                self._extract_article_urls(element.get("onclick", ""))
            )

        # HTML 전체에서 한 번 더 찾으면 마크업 구조가 조금 바뀌어도 링크를 놓칠 가능성이 줄어듭니다.
        detail_urls.extend(self._extract_article_urls(response.text))

        return list(dict.fromkeys(detail_urls))

    def crawl_detail(self, url: str) -> dict[str, Any]:
        """상세 페이지에서 FAQ 후보 데이터를 수집합니다."""
        response = self.safe_get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        published_at, comment_count, view_count = self._parse_article_meta(soup)

        return {
            "source_name": self.source_name,
            "category": self.category,
            "title": self._parse_title(soup),
            "content": self._parse_content(soup),
            "url": self._normalize_article_url(url),
            "published_at": published_at,
            "view_count": view_count,
            "comment_count": comment_count,
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _parse_title(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 제목을 추출합니다."""
        title_element = soup.select_one("a.fs-title")

        if title_element is not None:
            return title_element.get_text(" ", strip=True)

        og_title = soup.select_one("meta[property='og:title']")

        if og_title is not None:
            return og_title.get("content", "").strip()

        return ""

    def _parse_content(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 본문을 추출합니다."""
        content_element = soup.select_one("#article_body")

        if content_element is None:
            content_element = soup.select_one("div.fs-body")

        if content_element is None:
            og_description = soup.select_one("meta[property='og:description']")
            return (
                og_description.get("content", "").strip()
                if og_description is not None
                else ""
            )

        return content_element.get_text(" ", strip=True)

    def _parse_article_meta(
        self,
        soup: BeautifulSoup,
    ) -> tuple[str | None, int | None, int | None]:
        """상세 페이지 상단에서 작성일, 댓글 수, 조회수를 추출합니다."""
        meta_container = soup.select_one("div.d-flex.flex-wrap.justify-content-end")

        if meta_container is None:
            return None, None, None

        meta_values = [
            value.get_text(" ", strip=True)
            for value in meta_container.select("span")
            if value.get_text(" ", strip=True)
        ]

        published_at = meta_values[0] if len(meta_values) >= 1 else None
        comment_count = (
            self._parse_int(meta_values[1])
            if len(meta_values) >= 2
            else None
        )
        view_count = self._parse_int(meta_values[2]) if len(meta_values) >= 3 else None

        return published_at, comment_count, view_count

    def _parse_int(self, value: str) -> int | None:
        """문자열에서 숫자만 뽑아 정수로 변환합니다."""
        number_text = re.sub(r"[^0-9]", "", value)

        if not number_text:
            return None

        return int(number_text)

    def _extract_article_urls(self, text: str) -> list[str]:
        """문자열 안에서 EVDang 상세 게시글 URL을 찾아 표준 URL로 변환합니다."""
        if not text:
            return []

        decoded_text = html.unescape(text)
        article_urls: list[str] = []

        for match in EVDANG_ARTICLE_PATH_PATTERN.finditer(decoded_text):
            article_urls.append(
                self._normalize_article_url(match.group(0))
            )

        return article_urls

    def _normalize_article_url(self, href: str) -> str:
        """게시글 URL에서 검색용 쿼리스트링을 제거하고 표준 URL로 정리합니다."""
        absolute_url = urljoin(EVDANG_BASE_URL, href)
        parsed_url = urlparse(absolute_url)

        return urljoin(EVDANG_BASE_URL, parsed_url.path)
