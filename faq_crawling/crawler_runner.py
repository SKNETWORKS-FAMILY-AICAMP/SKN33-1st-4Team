"""FAQ 크롤러 실행 흐름을 묶는 모듈."""

from __future__ import annotations

import pandas as pd

from faq_crawling.constants import DEFAULT_DETAIL_LIMIT, DEFAULT_PAGE_LIMIT
from faq_crawling.dataframe_helper import questions_to_dataframe
from faq_crawling.evdang_crawler import EVDangCrawler
from faq_crawling.evlounge_crawler import EVLoungeCrawler
from faq_crawling.ppomppu_crawler import PpomppuCrawler


def crawl_evdang_questions(
    keyword: str,
    *,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    detail_limit: int = DEFAULT_DETAIL_LIMIT,
) -> pd.DataFrame:
    """EVDang에서 검색어 기준 FAQ 후보 게시글을 수집합니다."""
    crawler = EVDangCrawler()

    results = crawler.crawl(
        keyword,
        page_limit=page_limit,
        detail_limit=detail_limit,
    )

    return questions_to_dataframe(results)


def crawl_evlounge_questions(
    keyword: str,
    *,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    detail_limit: int = DEFAULT_DETAIL_LIMIT,
) -> pd.DataFrame:
    """EV 라운지에서 검색어 기준 FAQ 후보 게시글을 수집합니다."""
    crawler = EVLoungeCrawler()

    results = crawler.crawl(
        keyword,
        page_limit=page_limit,
        detail_limit=detail_limit,
    )

    return questions_to_dataframe(results)


def crawl_ppomppu_questions(
    keyword: str,
    *,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    detail_limit: int = DEFAULT_DETAIL_LIMIT,
) -> pd.DataFrame:
    """뽐뿌 자동차포럼에서 전기차 관련 FAQ 후보 게시글을 수집합니다."""
    crawler = PpomppuCrawler()

    results = crawler.crawl(
        keyword,
        page_limit=page_limit,
        detail_limit=detail_limit,
    )

    return questions_to_dataframe(results)