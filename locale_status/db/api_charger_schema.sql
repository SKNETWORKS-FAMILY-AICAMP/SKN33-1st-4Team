-- 공공데이터 전기자동차 충전소 OpenAPI 응답 저장용 테이블입니다.
-- 목적:
-- 1. API에서 받아온 충전소/충전기/상태 정보를 한 테이블에 보관
-- 2. Streamlit은 API를 직접 호출하지 않고 이 테이블을 SELECT
-- 3. 나중에 팀원 ERD와 합칠 때 stat_id + chger_id 기준으로 분리/이관
--
-- 기준 API:
-- - getChargerInfo
-- - getChargerStatus
--
-- 주의:
-- - stat_id + chger_id 조합이 충전기 1대를 구분하는 핵심 키입니다.
-- - stat_upd_dt, last_tsdt, last_tedt, now_tsdt는 API 원본 문자열(yyyyMMddHHmmss)을
--   Python 수집 스크립트에서 DATETIME으로 변환해서 넣는 것을 권장합니다.

CREATE TABLE IF NOT EXISTS tbl_api_charger_snapshot (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '내부 자동 증가 ID',

    -- API 원본 식별자
    stat_id VARCHAR(20) NOT NULL COMMENT 'API 충전소 ID(statId)',
    chger_id VARCHAR(10) NOT NULL COMMENT 'API 충전기 ID(chgerId)',

    -- 충전소 기본정보
    stat_nm VARCHAR(100) NOT NULL COMMENT '충전소명(statNm)',
    addr VARCHAR(255) NOT NULL COMMENT '주소(addr)',
    addr_detail VARCHAR(255) NULL COMMENT '주소상세(addrDetail)',
    location VARCHAR(255) NULL COMMENT '상세위치(location)',
    lat DECIMAL(10, 7) NULL COMMENT '위도(lat)',
    lng DECIMAL(10, 7) NULL COMMENT '경도(lng)',
    use_time VARCHAR(100) NULL COMMENT '이용가능시간(useTime)',

    -- 운영기관 정보
    busi_id VARCHAR(10) NULL COMMENT '기관 아이디(busiId)',
    bnm VARCHAR(100) NULL COMMENT '기관명(bnm)',
    busi_nm VARCHAR(100) NULL COMMENT '운영기관명(busiNm)',
    busi_call VARCHAR(30) NULL COMMENT '운영기관 연락처(busiCall)',

    -- 충전기 기본정보
    chger_type VARCHAR(10) NULL COMMENT '충전기 타입(chgerType)',
    power_type VARCHAR(100) NULL COMMENT '전력 타입(powerType)',
    output DECIMAL(8, 2) NULL COMMENT '충전용량 kW(output)',
    method VARCHAR(30) NULL COMMENT '충전방식(method)',
    maker VARCHAR(100) NULL COMMENT '제조사(maker)',

    -- 실시간 상태정보
    stat TINYINT NULL COMMENT '충전기 상태(stat): 0 알수없음, 1 통신이상, 2 사용가능, 3 충전중, 4 운영중지, 5 점검중',
    stat_upd_dt DATETIME NULL COMMENT '상태갱신일시(statUpdDt)',
    last_tsdt DATETIME NULL COMMENT '마지막 충전시작일시(lastTsdt)',
    last_tedt DATETIME NULL COMMENT '마지막 충전종료일시(lastTedt)',
    now_tsdt DATETIME NULL COMMENT '충전중 시작일시(nowTsdt)',

    -- 지역/분류 정보
    zcode VARCHAR(10) NULL COMMENT '시도 지역코드(zcode)',
    zscode VARCHAR(10) NULL COMMENT '시군구 상세 지역코드(zscode)',
    kind VARCHAR(10) NULL COMMENT '충전소 구분 코드(kind)',
    kind_detail VARCHAR(20) NULL COMMENT '충전소 구분 상세 코드(kindDetail)',

    -- 이용/상태 부가정보
    parking_free CHAR(1) NULL COMMENT '주차료 무료 여부(parkingFree): Y/N',
    note VARCHAR(255) NULL COMMENT '충전소 안내(note)',
    limit_yn CHAR(1) NULL COMMENT '이용자 제한 여부(limitYn): Y/N',
    limit_detail VARCHAR(255) NULL COMMENT '이용 제한 사유(limitDetail)',
    del_yn CHAR(1) NULL COMMENT '삭제 여부(delYn): Y/N',
    del_detail VARCHAR(255) NULL COMMENT '삭제 사유(delDetail)',
    traffic_yn CHAR(1) NULL COMMENT '편의제공 여부(trafficYn): Y/N',
    install_year SMALLINT NULL COMMENT '설치년도(year)',
    floor_num VARCHAR(50) NULL COMMENT '지상/지하 층수(floorNum)',
    floor_type VARCHAR(10) NULL COMMENT '지상/지하 구분(floorType): F 지상, B 지하',

    -- 수집 관리 정보
    synced_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'API 동기화 시각',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 최초 생성 시각',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'DB 수정 시각',

    PRIMARY KEY (id),
    UNIQUE KEY uq_api_charger_snapshot (stat_id, chger_id),
    KEY idx_api_charger_region (zcode, zscode),
    KEY idx_api_charger_status (stat),
    KEY idx_api_charger_station_name (stat_nm),
    KEY idx_api_charger_synced_at (synced_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='공공데이터 전기차 충전소 API 현재상태 스냅샷';
