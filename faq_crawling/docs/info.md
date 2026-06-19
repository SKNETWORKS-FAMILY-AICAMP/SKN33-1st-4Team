# 한국환경공단 전기차 충전소 API

한국환경공단 API에서는 크게 **충전소 기본정보**와 **충전기 실시간 상태정보**를 제공합니다.

---

## 충전소 기본정보

| 정보            | API 필드 예시                 |
| ------------- | ------------------------- |
| 충전소명          | `statNm`                  |
| 충전소 ID        | `statId`                  |
| 충전기 ID        | `chgerId`                 |
| 충전기 타입        | `chgerType`               |
| 주소·상세주소       | `addr`, `addrDetail`      |
| 설치 위치 설명      | `location`                |
| 위도·경도         | `lat`, `lng`              |
| 이용 가능시간       | `useTime`                 |
| 운영기관 ID·명칭    | `busiId`, `bnm`, `busiNm` |
| 운영기관 연락처      | `busiCall`                |
| 충전용량(kW)      | `output`                  |
| 충전방식          | `method`                  |
| 시도·시군구 코드     | `zcode`, `zscode`         |
| 충전소 구분·상세 구분  | `kind`, `kindDetail`      |
| 주차료 무료 여부     | `parkingFree`             |
| 이용 안내 및 특이사항  | `note`                    |
| 이용자 제한 여부·내용  | `limitYn`, `limitDetail`  |
| 삭제 여부·사유      | `delYn`, `delDetail`      |
| 편의시설 제공 여부    | `trafficYn`               |
| 지상·지하 구분 및 층수 | 관련 층수 정보                  |

---

## 실시간 상태정보

| 정보           | API 필드      |
| ------------ | ----------- |
| 충전기 상태       | `stat`      |
| 상태 변경 일시     | `statUpdDt` |
| 마지막 충전 시작 일시 | `lastTsdt`  |
| 마지막 충전 종료 일시 | `lastTedt`  |
| 현재 충전 시작 일시  | `nowTsdt`   |

### 충전기 상태 코드

| 코드 | 상태     |
| -- | ------ |
| 1  | 통신 이상  |
| 2  | 충전 대기  |
| 3  | 충전 중   |
| 4  | 운영 중지  |
| 5  | 점검 중   |
| 9  | 상태 미확인 |

---

## API 기능

### 1. 충전소 정보 조회

* 충전소 위치
* 주소
* 운영기관
* 충전기 종류
* 충전 용량

주요 API:

```text
getChargerInfo
```

---

### 2. 충전소 상태 조회

API URL:

```text
http://apis.data.go.kr/B552584/EvCharger/getChargerStatus
```

조회 조건:

* 지역코드(`zcode`)
* 최근 상태 갱신 범위(`period`, 1~10분)
* 페이지 번호(`pageNo`)
* 조회 건수(`numOfRows`)

조회 가능한 정보:

* 충전 대기 여부
* 충전 중 여부
* 점검 상태
* 운영 중지 여부
* 최근 충전 이력

---

## API 이용 정책

* 무료 제공
* 개발계정 기준 일일 1,000건 호출 가능
* 실시간 상태 정보 제공
* 지속적으로 데이터 갱신

---

## 참고 링크

공공데이터포털 전기차 충전소 Open API

https://www.data.go.kr/data/15076352/openapi.do
