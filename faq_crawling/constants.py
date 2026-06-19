"""FAQ 크롤링에서 공통으로 사용하는 상수."""

from __future__ import annotations


# 처음 수집할 검색어 목록입니다.
# 현재는 EVDang 검색어로 먼저 사용합니다.
SEARCH_KEYWORDS = [
    "전기차",
    "충전",
    "배터리",
    "테슬라",
    "아이오닉5",
    "아이오닉6",
    "EV6",
    "EV9",
    "모델3",
    "모델Y",
]


# 제목 또는 본문에 아래 키워드가 포함된 게시글만 FAQ 후보로 저장합니다.
EV_KEYWORDS = [
    "전기차",
    "EV",
    "충전",
    "급속충전",
    "완속충전",
    "배터리",
    "주행거리",
    "충전소",
    "아이오닉",
    "아이오닉5",
    "아이오닉6",
    "EV6",
    "EV9",
    "테슬라",
    "모델3",
    "모델Y",
    "코나EV",
    "니로EV",
    "화재",
]


# 클리앙 굴러간당 게시판 기본 주소입니다.
CLIEN_BOARD_URL = "https://www.clien.net/service/board/cm_car"


# EVDang 사이트 기본 주소와 검색 대상 주소입니다.
EVDANG_BASE_URL = "https://evdang.com"
EVDANG_ARTICLES_URL = f"{EVDANG_BASE_URL}/articles"

# EV 라운지 / EVPOST 기본 주소와 검색 대상 주소입니다.
EVLOUNGE_BASE_URL = "https://www.evpost.co.kr"
EVLOUNGE_SEARCH_URL = f"{EVLOUNGE_BASE_URL}/wp/"

# requests 요청 시 사용할 기본 User-Agent입니다.
# 일부 사이트는 User-Agent가 없으면 요청을 차단할 수 있습니다.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


# 검색 결과는 처음에는 키워드당 1페이지만 수집합니다.
DEFAULT_PAGE_LIMIT = 1


# 상세 페이지 요청이 너무 많아지지 않도록 초기 최대 수집 개수를 제한합니다.
DEFAULT_DETAIL_LIMIT = 20
