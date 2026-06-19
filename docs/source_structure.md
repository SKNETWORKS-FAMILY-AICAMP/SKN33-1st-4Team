# 권장 소스 구조와 모듈 역할

이 문서는 최종 Streamlit 통합 애플리케이션을 기준으로 한 소스 구조 제안입니다.

## 핵심 원칙

- 최종 실행 파일은 `app.py` 하나로 통합합니다.
- Streamlit 화면은 API를 직접 호출하지 않습니다.
- Streamlit 화면은 CSV 파일을 읽지 않습니다.
- Streamlit 화면은 service 계층 함수를 호출하고, service 계층은 MySQL 조회 결과를 가공합니다.
- API 호출, 파싱, DB 저장, 화면 표시를 한 파일에 섞지 않습니다.

## 권장 흐름

```text
collect  API 호출
parse    응답 정리 및 선택 컬럼 추출
db       MySQL 연결 및 저장
queries  SELECT SQL 관리
service  화면에 필요한 데이터 형태로 가공
ui       Streamlit 화면 구성
app.py   전체 페이지 통합
```

## 디렉터리별 역할

| 경로 | 역할 |
|---|---|
| `app.py` | 최종 Streamlit 진입점 |
| `src/config.py` | 환경변수, 프로젝트 경로, 공통 설정 |
| `src/constants.py` | 지역코드, 상태코드 등 전체 상수 |
| `src/api_fields.py` | API에서 사용할 선택 컬럼 목록 |
| `src/collect/` | OpenAPI 호출, 선택 컬럼 CSV export |
| `src/parse/` | XML 응답에서 필요한 데이터 구조 생성 |
| `src/queries/` | 화면/서비스별 SELECT SQL 정의 |
| `src/service/` | 비즈니스 로직과 DataFrame 가공 |
| `src/ui/` | Streamlit 화면 단위 컴포넌트 |
| `group_a/`, `serar_locale/`, `faq_crawling/` | 작업 노트, 화면 캡처, 중간 산출물 |
| `resources/` | SQL 스키마, 참고 SQL |
| `docs/` | 가이드, ERD, 발표 자료 |
| `data/debug/` | 디버깅용 CSV export 결과 |

## 주제별 통합 방식

각 주제는 `src/ui/`에 화면 함수를 만들고, `app.py`에서 사이드바 또는 탭으로 연결합니다.

예시:

```python
from src.ui.serar_locale_available_view import render_serar_locale_available_view

page = st.sidebar.radio(
    "페이지",
    ["충전소 지도", "사용 가능 충전기", "FAQ 검색"],
)

if page == "사용 가능 충전기":
    render_serar_locale_available_view(project_root)
```

## Group B 권장 모듈

주제 2는 다음 모듈을 기준으로 개발합니다.

| 파일 | 역할 |
|---|---|
| `src/queries/serar_locale_queries.py` | 사용 가능 충전기 조회 SQL |
| `src/service/serar_locale_availability.py` | 조회 결과 가공, 필터 파라미터 관리 |
| `src/ui/serar_locale_available_view.py` | Streamlit 화면 |

주제 2 화면은 최종적으로 다음 질문에 답해야 합니다.

```text
선택한 지역 또는 충전소에서 지금 바로 사용할 수 있는 충전기는 무엇인가?
```

혼잡도 분석과 별도 한전 설치현황 화면은 최종 통합 앱에서 제외합니다. Group B는 충전기 목록과 현재 사용 가능 여부에 집중하고, `getChargerStatus` 응답은 현재 상태 표시와 사용 가능 충전기 필터링에만 사용합니다.
