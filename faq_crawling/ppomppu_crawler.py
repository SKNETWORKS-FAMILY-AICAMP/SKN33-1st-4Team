"""뽐뿌 자동차포럼 크롤러."""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, CrawlerError


PPOMPPU_BASE_URL = "https://m.ppomppu.co.kr"
PPOMPPU_CAR_BOARD_URL = f"{PPOMPPU_BASE_URL}/new/bbs_list.php"
PPOMPPU_ARTICLE_PATH = "/new/bbs_view.php"
PPOMPPU_AUTO_PAGE_LIMIT = 10


class PpomppuCrawler(BaseCrawler):
    """뽐뿌 자동차포럼에서 전기차 관련 FAQ 후보 게시글을 수집하는 크롤러.

    robots.txt에서 /new/search_result.php 검색 URL은 제한되어 있으므로,
    사이트 검색 기능을 사용하지 않고 자동차포럼 목록 페이지를 수집한 뒤
    제목/본문 기준으로 전기차 관련 글만 필터링합니다.
    """

    source_name = "뽐뿌"
    category = "자동차포럼"

    def __init__(
        self,
        *,
        timeout: int = 10,
        headers: dict[str, str] | None = None,
        request_delay: float = 1.1,
    ) -> None:
        """뽐뿌 robots.txt의 Crawl-delay: 1을 고려해 요청 간격을 설정합니다."""
        super().__init__(
            timeout=timeout,
            headers=headers,
        )
        self.request_delay = request_delay

    def safe_get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ):
        """GET 요청 후 robots.txt의 Crawl-delay를 고려해 잠시 대기합니다."""
        response = super().safe_get(
            url,
            params=params,
        )
        time.sleep(self.request_delay)

        return response

    def build_search_url(self, keyword: str, page: int = 0) -> str:
        """자동차포럼 목록 URL을 생성합니다.

        뽐뿌는 검색 URL을 사용하지 않습니다.
        keyword는 URL 생성에는 쓰지 않고, 목록/상세 필터링에만 사용합니다.
        """
        page_number = page + 1

        params: dict[str, str | int] = {
            "id": "car",
        }

        if page_number > 1:
            params["page"] = page_number

        return f"{PPOMPPU_CAR_BOARD_URL}?{urlencode(params)}"

    def crawl(
        self,
        keyword: str,
        *,
        page_limit: int = 1,
        detail_limit: int = 20,
    ) -> list[dict[str, Any]]:
        """최근 목록을 넘겨 보며 선택 검색어의 글을 요청 개수만큼 수집합니다."""
        detail_urls: list[str] = []
        minimum_pages = max(1, page_limit)
        maximum_pages = max(minimum_pages, PPOMPPU_AUTO_PAGE_LIMIT)
        candidate_limit = max(detail_limit, min(detail_limit * 2, 50))

        for page in range(maximum_pages):
            detail_urls.extend(self.crawl_list(keyword, page=page))
            unique_urls = list(dict.fromkeys(detail_urls))
            scanned_pages = page + 1

            if scanned_pages >= minimum_pages and len(unique_urls) >= candidate_limit:
                break

        candidate_urls = list(dict.fromkeys(detail_urls))[:candidate_limit]
        results: list[dict[str, Any]] = []

        for detail_url in candidate_urls:
            try:
                results.append(self.crawl_detail(detail_url))
            except CrawlerError:
                continue

        results.sort(key=self._published_at_sort_key, reverse=True)
        return results[:detail_limit]

    def crawl_list(self, keyword: str, page: int = 0) -> list[str]:
        """자동차포럼 목록에서 전기차 관련 게시글 URL 후보를 수집합니다."""
        list_url = self.build_search_url(
            keyword,
            page=page,
        )
        response = self.safe_get(list_url)
        soup = BeautifulSoup(response.text, "html.parser")

        matched_article_urls: list[str] = []

        for link in soup.select("a[href]"):
            href = link.get("href", "").strip()

            if not self._is_article_href(href):
                continue

            article_url = self._normalize_article_url(href)
            link_text = link.get_text(" ", strip=True)

            if self._contains_filter_keyword(link_text, keyword):
                matched_article_urls.append(article_url)

        return list(dict.fromkeys(matched_article_urls))

    def crawl_detail(self, url: str) -> dict[str, Any]:
        """상세 페이지에서 FAQ 후보 데이터를 수집합니다."""
        response = self.safe_get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "source_name": self.source_name,
            "category": self.category,
            "title": self._parse_title(soup),
            "content": self._parse_content(soup),
            "url": self._normalize_article_url(url),
            "published_at": self._parse_published_at(soup),
            "view_count": self._parse_view_count(soup),
            "comment_count": self._parse_comment_count(soup),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _is_article_href(self, href: str) -> bool:
        """href 값이 뽐뿌 자동차포럼 상세 게시글 링크인지 확인합니다."""
        if not href:
            return False

        absolute_url = urljoin(
            PPOMPPU_BASE_URL,
            href,
        )
        parsed_url = urlparse(absolute_url)

        if parsed_url.path != PPOMPPU_ARTICLE_PATH:
            return False

        query_params = parse_qs(parsed_url.query)

        board_id = query_params.get("id", [""])[0]
        article_no = query_params.get("no", [""])[0]

        return board_id == "car" and article_no.isdigit()

    def _normalize_article_url(self, href: str) -> str:
        """게시글 URL을 표준 URL로 정리합니다."""
        absolute_url = urljoin(
            PPOMPPU_BASE_URL,
            href,
        )
        parsed_url = urlparse(absolute_url)
        query_params = parse_qs(parsed_url.query)

        article_no = query_params.get("no", [""])[0]

        return f"{PPOMPPU_BASE_URL}{PPOMPPU_ARTICLE_PATH}?id=car&no={article_no}"

    def _get_parent_text(self, link) -> str:
        """링크 주변 영역의 텍스트를 가져옵니다."""
        parent = link.find_parent(
            [
                "li",
                "tr",
                "div",
            ]
        )

        if parent is None:
            return ""

        return parent.get_text(" ", strip=True)

    def _contains_filter_keyword(self, text: str, keyword: str) -> bool:
        """목록 제목에 사용자가 선택한 검색어가 포함되어 있는지 확인합니다."""
        if not text or not keyword:
            return False

        return keyword.lower() in text.lower()

    def _parse_title(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 제목을 추출합니다."""
        og_title = soup.select_one("meta[property='og:title']")

        if og_title is not None:
            title = og_title.get("content", "").strip()

            if title:
                return self._clean_title(title)

        selectors = [
            "h1",
            "h2",
            "h3",
            ".view_title",
            ".title",
            ".subject",
            ".bbs_title",
        ]

        for selector in selectors:
            title_element = soup.select_one(selector)

            if title_element is None:
                continue

            title = title_element.get_text(" ", strip=True)

            if title:
                return self._clean_title(title)

        return ""

    def _parse_content(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 본문을 추출합니다."""
        selectors = [
            "#bbs_view_content",
            ".bbs_view_content",
            ".view_content",
            ".board-contents",
            ".bbs_contents",
            ".contents",
            ".article_content",
        ]

        for selector in selectors:
            content_element = soup.select_one(selector)

            if content_element is None:
                continue

            for unwanted in content_element.select(
                "script, style, iframe, .comment, .comments, .reply, .signature, .ad"
            ):
                unwanted.decompose()

            content = content_element.get_text(" ", strip=True)

            if content:
                return content

        og_description = soup.select_one("meta[property='og:description']")

        if og_description is not None:
            return og_description.get("content", "").strip()

        return ""

    def _parse_published_at(self, soup: BeautifulSoup) -> str | None:
        """상세 페이지에서 작성일을 추출합니다."""
        text = soup.get_text(" ", strip=True)

        patterns = [
            r"\d{4}[-.]\d{1,2}[-.]\d{1,2}\s+\d{1,2}:\d{2}",
            r"\d{2}[-.]\d{1,2}[-.]\d{1,2}\s+\d{1,2}:\d{2}",
            r"\d{4}[-.]\d{1,2}[-.]\d{1,2}",
            r"\d{2}[-.]\d{1,2}[-.]\d{1,2}",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                return match.group(0)

        return None

    def _parse_view_count(self, soup: BeautifulSoup) -> int | None:
        """상세 페이지에서 조회수를 추정합니다."""
        text = soup.get_text(" ", strip=True)

        patterns = [
            r"조회수\s*([0-9,]+)",
            r"조회\s*([0-9,]+)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                return self._parse_int(match.group(1))

        return None

    def _parse_comment_count(self, soup: BeautifulSoup) -> int | None:
        """상세 페이지에서 댓글 수를 추정합니다."""
        selectors = [
            ".comment_count",
            ".comment-count",
            ".reply_count",
            ".reply-count",
        ]

        for selector in selectors:
            comment_element = soup.select_one(selector)

            if comment_element is None:
                continue

            comment_text = comment_element.get_text(" ", strip=True)
            comment_count = self._parse_int(comment_text)

            if comment_count is not None:
                return comment_count

        text = soup.get_text(" ", strip=True)

        patterns = [
            r"댓글\s*([0-9,]+)",
            r"코멘트\s*([0-9,]+)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                return self._parse_int(match.group(1))

        return None

    def _parse_int(self, value: str) -> int | None:
        """문자열에서 숫자만 뽑아 정수로 변환합니다."""
        number_text = re.sub(
            r"[^0-9]",
            "",
            value,
        )

        if not number_text:
            return None

        return int(number_text)

    def _clean_title(self, title: str) -> str:
        """제목에서 사이트명 등 불필요한 문구를 제거합니다."""
        cleaned_title = title.strip()

        remove_patterns = [
            " - 뽐뿌",
            " :: 뽐뿌",
            "뽐뿌 - ",
        ]

        for pattern in remove_patterns:
            cleaned_title = cleaned_title.replace(
                pattern,
                "",
            )

        return cleaned_title.strip()
