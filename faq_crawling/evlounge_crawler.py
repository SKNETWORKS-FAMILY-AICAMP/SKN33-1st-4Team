"""EV 라운지 / EVPOST 검색 크롤러."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse, urlencode

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .constants import EVLOUNGE_BASE_URL, EVLOUNGE_SEARCH_URL


class EVLoungeCrawler(BaseCrawler):
    """EV 라운지 검색 결과에서 전기차 사용자 질문 후보를 수집하는 크롤러."""

    source_name = "EV 라운지"
    category = "EVPOST"
    first_page = 1

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """검색어와 페이지 번호로 EV 라운지 검색 URL을 생성합니다."""
        query = urlencode({"s": keyword})

        # 첫 페이지
        if page <= 1:
            return f"{EVLOUNGE_SEARCH_URL}?{query}"

        # WordPress 검색 페이지의 일반적인 페이지네이션 형태
        return f"{EVLOUNGE_BASE_URL}/wp/page/{page}/?{query}"

    def crawl_list(self, keyword: str, page: int = 1) -> list[str]:
        """검색 결과 페이지에서 게시글 상세 URL 목록을 수집합니다."""
        search_url = self.build_search_url(keyword, page=page)
        response = self.safe_get(search_url)

        soup = BeautifulSoup(response.text, "html.parser")

        detail_urls: list[str] = []

        for link in soup.select("a[href]"):
            href = link.get("href", "").strip()

            if not href:
                continue

            normalized_url = self._normalize_url(href)

            if self._is_article_url(normalized_url):
                detail_urls.append(normalized_url)

        # 같은 글이 여러 링크로 반복될 수 있으므로 중복 제거
        return list(dict.fromkeys(detail_urls))

    def crawl_detail(self, url: str) -> dict[str, Any]:
        """상세 페이지에서 제목, 본문, 작성일 등을 수집합니다."""
        response = self.safe_get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "source_name": self.source_name,
            "category": self.category,
            "title": self._parse_title(soup),
            "content": self._parse_content(soup),
            "url": self._normalize_url(url),
            "published_at": self._parse_published_at(soup),
            "view_count": None,
            "comment_count": self._parse_comment_count(soup),
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _normalize_url(self, href: str) -> str:
        """상대경로 또는 쿼리스트링이 섞인 URL을 표준 URL로 정리합니다."""
        absolute_url = urljoin(EVLOUNGE_BASE_URL, href)
        parsed_url = urlparse(absolute_url)

        # 검색 쿼리나 공유용 파라미터 제거
        return urljoin(EVLOUNGE_BASE_URL, parsed_url.path)

    def _is_article_url(self, url: str) -> bool:
        """EV 라운지 게시글 상세 URL인지 확인합니다."""
        parsed_url = urlparse(url)
        path = parsed_url.path

        if not path.startswith("/wp/"):
            return False

        # robots.txt에서 차단한 경로 제외
        disallowed_prefixes = (
            "/wp/eva/",
            "/wp/admin/",
            "/wp/wp-admin/",
            "/wp-content/plugins/",
            "/private",
        )

        if path.startswith(disallowed_prefixes):
            return False

        # 목록, 카테고리, 태그, 작성자, 페이지네이션 등은 제외
        excluded_prefixes = (
            "/wp/",
            "/wp/page/",
            "/wp/category/",
            "/wp/tag/",
            "/wp/author/",
        )

        if path in ("/wp/", "/wp"):
            return False

        if path.startswith(("/wp/page/", "/wp/category/", "/wp/tag/", "/wp/author/")):
            return False

        # 실제 게시글은 보통 /wp/게시글-슬러그/ 형태
        return True

    def _parse_title(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 제목을 추출합니다."""
        selectors = [
            "h1.entry-title",
            "h1.td-post-title",
            "h1",
        ]

        for selector in selectors:
            title_element = soup.select_one(selector)

            if title_element is not None:
                title = title_element.get_text(" ", strip=True)

                if title:
                    return title

        og_title = soup.select_one("meta[property='og:title']")

        if og_title is not None:
            return og_title.get("content", "").strip()

        return ""

    def _parse_content(self, soup: BeautifulSoup) -> str:
        """상세 페이지에서 게시글 본문을 추출합니다."""
        selectors = [
            "div.td-post-content",
            "div.entry-content",
            "article",
        ]

        for selector in selectors:
            content_element = soup.select_one(selector)

            if content_element is not None:
                content = content_element.get_text(" ", strip=True)

                if content:
                    return content

        og_description = soup.select_one("meta[property='og:description']")

        if og_description is not None:
            return og_description.get("content", "").strip()

        return ""

    def _parse_published_at(self, soup: BeautifulSoup) -> str | None:
        """상세 페이지에서 작성일을 추출합니다."""
        time_element = soup.select_one("time")

        if time_element is not None:
            datetime_value = time_element.get("datetime")

            if datetime_value:
                return datetime_value.strip()

            text_value = time_element.get_text(" ", strip=True)

            if text_value:
                return text_value

        meta_published = soup.select_one("meta[property='article:published_time']")

        if meta_published is not None:
            return meta_published.get("content", "").strip()

        return None

    def _parse_comment_count(self, soup: BeautifulSoup) -> int | None:
        """상세 페이지에서 댓글 수를 추정합니다."""
        comment_link = soup.select_one("a[href*='#comments']")

        if comment_link is None:
            return None

        text = comment_link.get_text(" ", strip=True)
        number_text = re.sub(r"[^0-9]", "", text)

        if not number_text:
            return None

        return int(number_text)
