from __future__ import annotations

"""OpenAPI 응답에서 프로젝트가 실제로 사용할 컬럼 정의."""


# 충전소/충전기 기본정보 API(getChargerInfo)에서 저장할 컬럼입니다.
# 화면 표시, 지역 필터링, 충전기 상세정보에 필요한 값만 남깁니다.
CHARGER_INFO_COLUMNS = [
    "statId",
    "statNm",
    "chgerId",
    "chgerType",
    "addr",
    "addrDetail",
    "location",
    "lat",
    "lng",
    "useTime",
    "busiId",
    "busiNm",
    "busiCall",
    "output",
    "method",
    "zcode",
    "zscode",
    "kind",
    "kindDetail",
    "parkingFree",
    "note",
    "limitYn",
    "limitDetail",
]


# 실시간 상태 API(getChargerStatus)에서 저장할 컬럼입니다.
# 최신 사용 가능 여부와 상태 분포 표시에 필요한 상태 값을 저장합니다.
CHARGER_STATUS_COLUMNS = [
    "busiId",
    "statId",
    "chgerId",
    "stat",
    "statUpdDt",
    "lastTsdt",
    "lastTedt",
    "nowTsdt",
]


# CSV 백업에 함께 넣을 수집 메타데이터입니다.
# DB 저장 시에도 수집 이력 확인이 필요하면 같은 값을 저장할 수 있습니다.
EXPORT_METADATA_COLUMNS = [
    "source_endpoint",
    "requested_zcode",
    "fetched_at",
]


SELECTED_COLUMNS_BY_ENDPOINT = {
    "getChargerInfo": CHARGER_INFO_COLUMNS,
    "getChargerStatus": CHARGER_STATUS_COLUMNS,
}
