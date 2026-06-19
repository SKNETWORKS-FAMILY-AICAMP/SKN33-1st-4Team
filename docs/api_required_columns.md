# 전기차 충전소 API 필수 컬럼 정리

출처: 공공데이터포털 한국환경공단 전기자동차 충전소 정보 OpenAPI, 데이터셋 `15076352`.

API 응답을 데이터 구조의 기준으로 봅니다. 디버깅용 CSV export 파일은 확인용으로만 보관하고, 실제 애플리케이션 실행 흐름은 MySQL 데이터를 조회하도록 구성해야 합니다.

## API 엔드포인트

| 엔드포인트 | 역할 | 프로젝트 사용 위치 |
|---|---|---|
| `getChargerInfo` | 충전소 및 충전기 정적 메타데이터 | 충전소 지도/상세, 사용 가능 충전기 표시 정보 |
| `getChargerStatus` | 실시간 충전기 상태 데이터 | 사용 가능 충전기 조회, 상태 분포 표시 |

## 최소 공통 식별키

두 엔드포인트에서 하나의 물리 충전기를 식별할 때 필요한 필드입니다.

| API 필드 | 의미 | 필수 여부 |
|---|---|---|
| `statId` | 충전소 ID | 필수 |
| `chgerId` | 충전소 안의 충전기 ID | 필수 |
| `busiId` | 운영기관 ID | 검증에 유용 |

충전기 자연키는 `(statId, chgerId)`로 잡는 것이 좋습니다. API 데이터를 매칭해야 하므로 auto increment ID만 단독 식별자로 쓰면 안 됩니다.

## `getChargerInfo` 주요 컬럼

현재 코드에서 이미 기대하고 있는 충전소/충전기 기본정보 필드입니다.

| API 필드 | 의미 | 권장 DB 위치 |
|---|---|---|
| `statId` | 충전소 ID | `charging_stations.stat_id`, `chargers.stat_id` |
| `statNm` | 충전소명 | `charging_stations.stat_nm` |
| `chgerId` | 충전기 ID | `chargers.chger_id` |
| `chgerType` | 충전기 타입 코드 | `chargers.chger_type` |
| `addr` | 주소 | `charging_stations.addr` |
| `addrDetail` | 상세주소 | `charging_stations.addr_detail` |
| `location` | 위치 설명 | `charging_stations.location` |
| `lat` | 위도 | `charging_stations.lat` |
| `lng` | 경도 | `charging_stations.lng` |
| `useTime` | 이용 가능 시간 | `charging_stations.use_time` |
| `busiId` | 운영기관 ID | `charging_stations.busi_id` |
| `busiNm` | 운영기관명 | `charging_stations.busi_nm` |
| `busiCall` | 운영기관 연락처 | `charging_stations.busi_call` |
| `output` | 충전용량 | `chargers.output` |
| `method` | 충전방식 | `chargers.method` |
| `zcode` | 시도 코드 | `regions.zcode`, `charging_stations.zcode` |
| `zscode` | 시군구 코드 | `charging_stations.zscode` |
| `kind` | 충전소 구분 | `charging_stations.kind` |
| `kindDetail` | 충전소 상세 구분 | `charging_stations.kind_detail` |
| `parkingFree` | 주차료 무료 여부 | `charging_stations.parking_free` |
| `note` | 비고 | `charging_stations.note` |
| `limitYn` | 이용자 제한 여부 | `charging_stations.limit_yn` |
| `limitDetail` | 이용자 제한 상세 | `charging_stations.limit_detail` |

공공데이터포털 설명에는 삭제 여부, 편의제공 여부, 지상/지하 층수 관련 정보도 언급됩니다. 실제 응답에 추가 필드가 들어오는지 확인해야 한다면 일시적으로 디버깅 export 범위를 넓혀 확인하고, 기본 CSV 백업과 DB에는 선택 컬럼만 저장합니다.

## `getChargerStatus` 주요 컬럼

공공데이터포털 상세 페이지에서 확인되는 상태 조회 응답 필드입니다.

| API 필드 | 의미 | 권장 DB 위치 |
|---|---|---|
| `busiId` | 운영기관 ID | `charger_status_logs.busi_id` |
| `statId` | 충전소 ID | `charger_status_logs.stat_id` |
| `chgerId` | 충전기 ID | `charger_status_logs.chger_id` |
| `stat` | 충전기 상태 코드 | `charger_status_logs.stat` |
| `statUpdDt` | 충전기 상태 갱신 일시 | `charger_status_logs.stat_upd_dt` |

데이터셋 설명에는 마지막 충전 시작/종료 일시, 충전중 시작 일시도 언급됩니다. 실제 응답에 `lastTsdt`, `lastTedt`, `nowTsdt` 같은 필드가 있으면 버리지 말고 `charger_status_logs`에 저장하는 편이 좋습니다.

## 상태 코드 처리 주의점

현재 팀 SQL 주석과 기존 Python 코드의 상태 코드 해석이 서로 맞지 않습니다. 기존 코드의 `AVAILABLE_STATUS = "2"`는 상태 코드 `2`를 사용 가능/충전 대기로 처리하고 있습니다.

최종 UI 라벨을 확정하기 전에 OpenAPI 활용가이드 또는 실제 샘플 응답으로 상태 코드 의미를 다시 확인해야 합니다. DB에는 원본 상태 코드를 저장하고, 화면 표시 라벨은 Python에서 변환하는 방식을 권장합니다.

## `resources/skn_team4_1st_pro.sql` 검토 결과

현재 SQL의 주요 문제점입니다.

| 문제 | 영향 |
|---|---|
| `tbl_charge_station.cs_id INT`가 API의 `statId`와 맞지 않음 | API ID는 문자열처럼 다뤄야 하며 앞자리 0 손실 가능성이 있음 |
| `tbl_charger.cp_id INT`가 API 충전기 식별 방식과 맞지 않음 | API는 `(statId, chgerId)`로 충전기를 식별하므로 실시간 상태 갱신이 어려움 |
| `busiId`, `busiNm`, `busiCall` 등 운영기관 필드가 없음 | 상세 정보 표시와 디버깅에 필요한 정보가 누락됨 |
| `zcode`, `zscode` 등 지역 필드가 없음 | 세 주제 모두에서 지역 필터링이 불편해짐 |
| `output`, `method`, `chgerType` 원본 API 값 저장이 부족함 | 충전용량과 충전기 타입 필터링이 약해짐 |
| 충전기 현재 상태만 `tbl_charger`에 저장함 | 상태 갱신 시점 추적과 장애 분석이 어려움 |
| `charger_status_logs` 테이블이 없음 | 상태 API 응답 이력 관리가 어려움 |
| 외래키 선언이 없음 | 충전소와 충전기 사이 데이터 무결성이 약함 |

권장 방향: 기존 teammate SQL은 초기 초안/참고 자료로 남기고, 다음 설계 기준은 `resources/recommended_ev_charger_schema.sql`을 기반으로 잡는 것이 좋습니다.
