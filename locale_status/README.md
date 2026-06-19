# 그룹 B - 주제 2 작업 계획

담당자: 김일환, 정현두

## 주제 정의

주제 2의 핵심 질문은 다음과 같습니다.

```text
선택한 지역 또는 충전소에서 지금 바로 사용할 수 있는 충전기는 무엇인가?
```

주제 3과 같은 상태 데이터를 사용하지만, 주제 2는 혼잡도 분석이 아니라 **현재 사용 가능한 충전기 목록과 상세 정보**에 집중합니다.

## 최종 기능

- 지역 코드 또는 지역명 기준 필터링
- 충전소명 검색
- 충전기 타입 필터링
- 사용 가능한 충전기 목록 표시
- 충전소명, 주소, 충전기 ID, 충전기 타입, 충전용량, 충전방식 표시
- 마지막 상태 갱신 시각 표시
- 선택한 충전기 또는 충전소 상세 정보 표시

## 데이터 사용 규칙

- API는 수집 단계에서만 호출합니다.
- CSV는 백업과 디버깅 용도로만 저장합니다.
- Streamlit 화면은 CSV를 읽지 않습니다.
- Streamlit 화면은 API를 직접 호출하지 않습니다.
- Streamlit 화면은 MySQL SELECT 결과만 사용합니다.

## Group B 관련 공통 모듈

최종 실행 코드는 `serar_locale/`가 아니라 `src/` 아래에 둡니다.

| 파일 | 역할 |
|---|---|
| `src/queries/serar_locale_queries.py` | 사용 가능 충전기 조회 SQL |
| `src/service/serar_locale_availability.py` | DB 조회 결과를 화면에 맞게 가공 |
| `src/ui/serar_locale_available_view.py` | 주제 2 Streamlit 화면 |
| `app.py` | 최종 통합 Streamlit 진입점 |

`serar_locale/` 디렉터리는 작업 노트, 스크린샷, 중간 산출물을 보관하는 공간으로 사용합니다.

## DB 기준

Group B는 다음 테이블을 사용합니다.

```text
charging_stations
chargers
charger_status_logs
```

충전기 식별 기준:

```text
stat_id + chger_id
```

최신 상태 기준:

```text
charger_status_logs에서 충전기별 가장 최근 fetched_at
```

사용 가능 상태 기준:

```text
src.constants.AVAILABLE_STATUS
```

상태 코드의 실제 의미는 최종 제출 전 OpenAPI 활용가이드 또는 샘플 응답으로 다시 확인해야 합니다.

## 구현 순서

1. `resources/recommended_ev_charger_schema.sql` 기준으로 MySQL 테이블을 준비합니다.
2. `src/collect/export_selected_api_csv.py`로 선택 컬럼 CSV 백업을 생성합니다.
3. 같은 선택 컬럼을 MySQL에 저장하는 insert/upsert 로직을 구현합니다.
4. `src/service/serar_locale_availability.py`로 사용 가능 충전기 조회 결과를 확인합니다.
5. `src/ui/serar_locale_available_view.py`에서 Streamlit 화면을 구현합니다.
6. `app.py`에서 주제 2 화면을 통합 메뉴에 연결합니다.

## 주제 2와 주제 3의 경계

Group B가 담당할 것:

- 현재 사용 가능한 충전기 목록
- 충전기 단위 상세 정보
- 충전소/지역/타입 기준 필터링

Group C가 담당할 것:

- 혼잡도 점수
- 지역별 혼잡도 순위
- 시간대별 혼잡도 추이
- 충전소별 혼잡도 비교
