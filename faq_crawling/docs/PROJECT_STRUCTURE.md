# 프로젝트 구조 설명

이 문서는 다른 GPT나 개발자가 현재 프로젝트 맥락을 빠르게 이해할 수 있도록 정리한 구조 설명서입니다.

## 프로젝트 개요

전기차 충전소 데이터를 Streamlit으로 시각화하는 대시보드 프로젝트입니다.

현재 앱은 크게 세 페이지로 구성됩니다.

| 네비게이션 | 렌더 함수 | 설명 |
| --- | --- | --- |
| `대시보드` | `ui.dashboard_page.render_dashboard_page` | CSV 기반 전기차 충전소 사용량 지도, 지역별 사용량 차트, 충전용량 필터 |
| `실시간 사용가능한 충전기 조회` | `ui.locale_search_page.render_locale_search_page` | 공공데이터 API 기반 지역별 사용 가능 충전기 조회, 지도/테이블 표시, DB 저장/불러오기 |
| `FAQ검색` | `ui.faq_search_page.render_faq_search_page` | 현재는 타이틀만 있는 빈 페이지 |

앱 진입점은 `app.py`입니다.

## 실행 흐름

```text
app.py
├── ui/dashboard_page.py
├── ui/locale_search_page.py
└── ui/faq_search_page.py
```

`app.py`는 화면을 직접 구현하지 않고 Streamlit 페이지를 등록합니다.

```python
st.navigation(
    [dashboard_page, locale_search_page, faq_search_page],
    position="sidebar",
)
```

## 폴더 구조

```text
.
├── app.py
├── README.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── check_environment.py
├── data/
│   ├── test_data.csv
│   ├── coords.csv
│   └── annual-enterprise-survey-2023.csv
├── database/
│   ├── schema.sql
│   └── ERD.md
├── src/
│   ├── api.py
│   ├── constants.py
│   ├── db.py
│   └── preprocess.py
├── ui/
│   ├── dashboard_page.py
│   ├── locale_search_page.py
│   └── faq_search_page.py
├── locale_search/
│   ├── available_charger_search.py
│   └── location_filter.py
├── available_charger_view/
│   ├── map.py
│   └── table.py
├── charger_api_cache/
│   └── cached_api.py
├── charger_congestion/
│   └── status_chart.py
├── charger_capacity/
│   └── capacity_filter.py
├── usage_data/
│   └── charger_usage_data.py
├── usage_map/
│   └── regional_location_map.py
├── usage_chart/
│   └── regional_usage_chart.py
└── faq_crawling/
    └── __init__.py
```

## 주요 모듈 역할

| 경로 | 역할 |
| --- | --- |
| `app.py` | Streamlit 앱 진입점, 사이드바 네비게이션 등록 |
| `ui/dashboard_page.py` | 기존 CSV 기반 사용량 대시보드 페이지 |
| `ui/locale_search_page.py` | 실시간 사용 가능 충전기 조회 페이지 |
| `ui/faq_search_page.py` | FAQ검색 페이지 자리만 만든 상태 |
| `src/api.py` | 한국환경공단 전기차 충전소 API 호출 |
| `src/constants.py` | API 기본 URL, 지역 코드, 상태 코드 상수 |
| `src/preprocess.py` | API 기본정보와 상태정보 병합, 사용 가능 충전기 필터링 |
| `src/db.py` | MySQL 연결, 테이블 초기화, 캐시 조회/저장 |
| `locale_search/available_charger_search.py` | 지역 선택, API 조회, DB 불러오기/저장, 필터링 화면의 중심 로직 |
| `locale_search/location_filter.py` | 주소에서 시군구/읍면동 추출, 상세 지역 selectbox 렌더링 |
| `available_charger_view/table.py` | 사용 가능한 충전기 목록 테이블과 페이지네이션 |
| `available_charger_view/map.py` | 사용 가능한 충전기 위치 지도 |
| `charger_api_cache/cached_api.py` | Streamlit 캐시를 이용한 API 응답 캐싱 |
| `charger_congestion/status_chart.py` | 충전기 상태별 개수 차트 |
| `usage_data/charger_usage_data.py` | CSV 사용량 데이터 로딩 |
| `usage_map/regional_location_map.py` | 지역별 위치 지도 렌더링 |
| `usage_chart/regional_usage_chart.py` | 지역별 사용량 차트 렌더링 |
| `charger_capacity/capacity_filter.py` | 충전용량 선택 필터 |
| `faq_crawling/` | FAQ 크롤링 기능을 넣기 위해 새로 만든 패키지, 현재 구현 없음 |

## 실시간 충전기 조회 데이터 흐름

```text
사용자 지역 선택
    ↓
locale_search.available_charger_search
    ↓
charger_api_cache.cached_api
    ↓
src.api
    ├── getChargerInfo
    └── getChargerStatus
    ↓
src.preprocess.merge_charger_data
    ↓
locale_search.location_filter.add_location_columns
    ↓
상세 지역 필터 / 상태 차트 / 용량 필터
    ↓
available_charger_view.table
available_charger_view.map
```

DB 저장/불러오기 흐름은 `src.db`가 담당합니다.

```text
DB 불러오기 버튼
    ↓
src.db.load_valid_locale_search_cache
    ↓
세션 상태 복원

DB 저장 버튼
    ↓
src.db.save_locale_search_cache
    ↓
api_cache_runs + charger_snapshots 저장
```

## DB 구조

현재 실제 적용 스키마는 `database/schema.sql`에 있습니다.

주요 테이블은 두 개입니다.

| 테이블 | 설명 |
| --- | --- |
| `api_cache_runs` | API 조회/캐시 실행 단위 저장 |
| `charger_snapshots` | 특정 캐시 실행 시점의 충전기별 상세 정보 저장 |

관계는 다음과 같습니다.

```text
api_cache_runs 1 ─── N charger_snapshots
```

ERD 정리는 `database/ERD.md`에 있습니다.

## 환경 변수

`.env.example`을 기준으로 `.env` 파일을 만들어 사용합니다.

필요한 주요 값은 다음과 같습니다.

| 변수 | 용도 |
| --- | --- |
| `EV_CHARGER_API_KEY` | 한국환경공단 전기차 충전소 API 키 |
| `MYSQL_HOST` | MySQL 호스트 |
| `MYSQL_PORT` | MySQL 포트 |
| `MYSQL_USER` | MySQL 사용자 |
| `MYSQL_PASSWORD` | MySQL 비밀번호 |
| `MYSQL_DATABASE` | MySQL 데이터베이스명 |

## 주요 의존성

`requirements.txt` 기준입니다.

| 패키지 | 용도 |
| --- | --- |
| `streamlit` | 웹 대시보드 |
| `pandas` | 데이터프레임 처리 |
| `requests` | 공공데이터 API 호출 |
| `geopy` | 주소 기반 좌표 조회 |
| `pydeck` | 지도 시각화 |
| `python-dotenv` | `.env` 로딩 |
| `pymysql` | MySQL 연결 |

## 다음 작업자가 주의할 점

- `database/schema.sql`은 현재 앱의 `src.db` 구현과 연결되어 있으므로 스키마 변경 시 `src/db.py`의 컬럼 매핑도 같이 수정해야 합니다.
- 실시간 조회 페이지는 `st.session_state` 키를 `basic`, `move` suffix로 나눠 관리합니다.
- `DB 저장` 버튼은 상세 지역 selectbox 렌더링 직후에 위치합니다.
- `FAQ검색` 페이지는 네비게이션만 연결된 상태이며 실제 크롤링/검색 UI는 아직 없습니다.
- CSV 기반 대시보드와 API 기반 실시간 조회는 데이터 흐름이 분리되어 있습니다.
