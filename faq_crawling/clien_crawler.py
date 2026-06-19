"""클리앙 굴러간당 게시판 크롤러."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse, urlencode

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .constants import CLIEN_BOARD_URL


CLIEN_ARTICLE_PATH_PATTERN = re.compile(r"^/service/board/cm_car/\d+")


class ClienCrawler(BaseCrawler):
    """클리앙 굴러간당 게시글을 수집하는 크롤러.

    현재는 검색 결과 목록에서 게시글 상세 URL을 추출하는 단계까지 구현합니다.
    상세 페이지의 제목/본문/날짜 파싱은 다음 단계에서 채웁니다.
    """

    source_name = "클리앙"
    category = "굴러간당"

    def build_search_url(self, keyword: str, page: int = 0) -> str:
        """클리앙 굴러간당 검색 URL을 생성합니다."""
        query = urlencode(
            {
                "combine": "true",
                "q": keyword,
                "p": page,
                "sort": "recency",
                "boardCd": "",
                "isBoard": "false",
            }
        )
        return f"{CLIEN_BOARD_URL}?{query}"

    def crawl_list(self, keyword: str, page: int = 0) -> list[str]:
        """검색 결과에서 게시글 상세 URL 목록을 수집합니다."""
        search_url = self.build_search_url(keyword, page=page)
        response = self.safe_get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        detail_urls: list[str] = []

        # 검색 결과 HTML 안의 모든 링크 중 굴러간당 게시글 URL만 골라냅니다.
        for link in soup.select("a[href]"):
            href = link.get("href", "").strip()

            if not self._is_article_href(href):
                continue

            detail_urls.append(self._normalize_article_url(href))

        # 같은 글 링크가 목록 안에 여러 번 나올 수 있으므로 순서를 유지하며 중복 제거합니다.
        return list(dict.fromkeys(detail_urls))

    def crawl_detail(self, url: str) -> dict[str, Any]:
        """상세 페이지에서 FAQ 후보 데이터를 수집합니다."""
        # TODO: 다음 단계에서 제목, 본문, 작성일, 조회수, 댓글수를 추출합니다.
        self.safe_get(url)
        return {
            "source_name": self.source_name,
            "category": self.category,
            "title": "",
            "content": "",
            "url": url,
            "published_at": None,
            "view_count": None,
            "comment_count": None,
            "collected_at": None,
        }

    def _is_article_href(self, href: str) -> bool:
        """href 값이 클리앙 굴러간당 상세 게시글 링크인지 확인합니다."""
        if not href:
            return False

        parsed_url = urlparse(href)
        article_path = parsed_url.path

        return bool(CLIEN_ARTICLE_PATH_PATTERN.match(article_path))

    def _normalize_article_url(self, href: str) -> str:
        """상대경로/쿼리스트링이 섞인 게시글 링크를 표준 URL로 정리합니다."""
        parsed_url = urlparse(href)
        article_path = parsed_url.path

        return urljoin(CLIEN_BOARD_URL, article_path)
